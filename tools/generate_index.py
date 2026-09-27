#!/usr/bin/env python3
"""Generate a complete pub.dev index for LibPool."""

from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import json
import re
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable


PUB_API = "https://pub.dev/api"
USER_AGENT = "LibPool-indexer/1.0 (+https://github.com/LibPool)"
DEFAULT_CACHE = Path("cache/pub_cache.sqlite3")
DEFAULT_WORKERS = 24
DEFAULT_PAGE_WORKERS = 24
RETRIES = 5
MAJORS = (2, 3)


class FetchError(RuntimeError):
    pass


def http_json(url: str, retries: int = RETRIES) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(retries):
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read()
                if response.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                return json.loads(body.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise FetchError(f"not found: {url}") from exc
            if 400 <= exc.code < 500 and exc.code != 429:
                raise FetchError(f"HTTP Error {exc.code}: {url}") from exc
            last_error = exc
        except Exception as exc:  # noqa: BLE001 - retry transient network errors
            last_error = exc
        if attempt + 1 < retries:
            time.sleep(min(8.0, 0.5 * (2**attempt)))
    raise FetchError(f"failed after {retries} attempts: {url}: {last_error}")


def init_cache(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=NORMAL")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS package_list (
            name TEXT PRIMARY KEY,
            summary_json TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS package_details (
            name TEXT PRIMARY KEY,
            details_json TEXT NOT NULL,
            fetched_at INTEGER NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS package_pages (
            page INTEGER PRIMARY KEY,
            payload_json TEXT NOT NULL,
            fetched_at INTEGER NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS package_list_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )


def fetch_package_page(page: int) -> list[dict[str, Any]]:
    try:
        payload = http_json(f"{PUB_API}/packages?page={page}")
    except FetchError as exc:
        message = str(exc)
        if "HTTP Error 400" in message or "not found" in message:
            return []
        raise
    return list(payload.get("packages") or [])


def fetch_package_list(
    connection: sqlite3.Connection,
    page_workers: int,
    refresh: bool,
) -> list[dict[str, Any]]:
    if refresh:
        connection.execute("DELETE FROM package_pages")
        connection.execute("DELETE FROM package_list")
        connection.execute(
            "DELETE FROM package_list_state WHERE key = 'complete'"
        )
        connection.commit()

    existing = connection.execute(
        "SELECT summary_json FROM package_list ORDER BY name"
    ).fetchall()
    complete = connection.execute(
        "SELECT value FROM package_list_state WHERE key = 'complete'"
    ).fetchone()
    if existing and complete and complete[0] == "1":
        packages = [json.loads(row[0]) for row in existing]
        print(f"Using cached package list: {len(packages)} packages")
        return packages

    print("Fetching pub.dev package list...")

    def cached_page(page: int) -> list[dict[str, Any]] | None:
        row = connection.execute(
            "SELECT payload_json FROM package_pages WHERE page = ?", (page,)
        ).fetchone()
        return json.loads(row[0]) if row is not None else None

    def store_page(page: int, packages: list[dict[str, Any]]) -> None:
        connection.execute(
            """
            INSERT OR REPLACE INTO package_pages(page, payload_json, fetched_at)
            VALUES (?, ?, ?)
            """,
            (page, json.dumps(packages, ensure_ascii=False), int(time.time())),
        )
        connection.commit()

    def get_page(page: int) -> list[dict[str, Any]]:
        packages = cached_page(page)
        if packages is not None:
            return packages
        packages = fetch_package_page(page)
        store_page(page, packages)
        return packages

    first_page = get_page(1)
    if not first_page:
        raise RuntimeError("pub.dev returned an empty first package page")

    high = 2
    while get_page(high):
        high *= 2
        if high > 65_536:
            raise RuntimeError("pub.dev package page count exceeded safety limit")
    low = high // 2
    while low + 1 < high:
        middle = (low + high) // 2
        if get_page(middle):
            low = middle
        else:
            high = middle
    last_page = low
    print(f"  last page: {last_page}")

    missing_pages = [
        page
        for page in range(1, last_page + 1)
        if connection.execute(
            "SELECT 1 FROM package_pages WHERE page = ?", (page,)
        ).fetchone()
        is None
    ]
    if missing_pages:
        print(
            f"  fetching {len(missing_pages)} missing pages "
            f"with {page_workers} workers"
        )
        completed = 0
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=page_workers
        ) as executor:
            futures = {
                executor.submit(fetch_package_page, page): page
                for page in missing_pages
            }
            for future in concurrent.futures.as_completed(futures):
                page = futures[future]
                try:
                    packages_for_page = future.result()
                except Exception as exc:  # noqa: BLE001 - report page context
                    raise RuntimeError(f"package page {page} failed: {exc}") from exc
                store_page(page, packages_for_page)
                completed += 1
                if completed % 100 == 0:
                    print(f"    {completed}/{len(missing_pages)} pages")

    packages: list[dict[str, Any]] = []
    for page in range(1, last_page + 1):
        packages.extend(get_page(page))
    connection.executemany(
        "INSERT OR REPLACE INTO package_list(name, summary_json) VALUES (?, ?)",
        [(item["name"], json.dumps(item, ensure_ascii=False)) for item in packages],
    )
    connection.execute(
        """
        INSERT OR REPLACE INTO package_list_state(key, value)
        VALUES ('complete', '1')
        """
    )
    connection.commit()
    print(f"Fetched {len(packages)} packages")
    return packages


def fetch_details(name: str) -> dict[str, Any]:
    payload = http_json(
        f"{PUB_API}/packages/{urllib.parse.quote(name, safe='')}"
    )
    return compact_details(payload)


def compact_details(payload: dict[str, Any]) -> dict[str, Any]:
    latest = payload.get("latest") or {}
    latest_pubspec = latest.get("pubspec") or {}
    keep_pubspec = (
        "description",
        "homepage",
        "repository",
        "issue_tracker",
        "documentation",
        "topics",
    )
    compact_versions: list[dict[str, Any]] = []
    for version in payload.get("versions") or []:
        pubspec = version.get("pubspec") or {}
        environment = pubspec.get("environment") or {}
        compact_versions.append(
            {
                "version": version.get("version"),
                "published": version.get("published"),
                "archive_url": version.get("archive_url"),
                "pubspec": {"environment": {"sdk": environment.get("sdk")}},
            }
        )
    return {
        "name": payload.get("name"),
        "latest": {
            "version": latest.get("version"),
            "published": latest.get("published"),
            "archive_url": latest.get("archive_url"),
            "pubspec": {
                key: latest_pubspec.get(key)
                for key in keep_pubspec
                if latest_pubspec.get(key) is not None
            },
        },
        "versions": compact_versions,
    }


def fetch_detail_worker(name: str) -> tuple[str, dict[str, Any]]:
    return name, fetch_details(name)


def populate_details(
    connection: sqlite3.Connection,
    package_names: Iterable[str],
    workers: int,
    use_processes: bool,
) -> int:
    cached = {
        row[0]
        for row in connection.execute("SELECT name FROM package_details")
    }
    missing = sorted(name for name in package_names if name not in cached)
    total = len(package_names)
    if not missing:
        print(f"Using cached package details: {len(cached)}/{total}")
        return len(cached)

    print(
        f"Fetching package details: {len(missing)} missing, "
        f"{len(cached)} cached, {workers} workers"
    )
    lock = threading.Lock()
    completed = 0
    failed: list[tuple[str, str]] = []
    in_flight = 0
    submitted = 0
    window_size = max(workers * 4, 64)

    executor_class: type[concurrent.futures.Executor]
    executor_class = (
        concurrent.futures.ProcessPoolExecutor
        if use_processes
        else concurrent.futures.ThreadPoolExecutor
    )
    with executor_class(max_workers=workers) as executor:
        futures: dict[concurrent.futures.Future[Any], str] = {}

        def submit_one() -> None:
            nonlocal in_flight, submitted
            if submitted >= len(missing):
                return
            name = missing[submitted]
            submitted += 1
            futures[executor.submit(fetch_detail_worker, name)] = name
            in_flight += 1

        for _ in range(min(window_size, len(missing))):
            submit_one()

        while futures:
            done, _ = concurrent.futures.wait(
                futures,
                return_when=concurrent.futures.FIRST_COMPLETED,
                timeout=30,
            )
            if not done:
                print(
                    f"  {completed}/{len(missing)} fetched, "
                    f"{len(failed)} failed, {in_flight} in flight",
                    flush=True,
                )
                continue
            for future in done:
                name = futures.pop(future)
                in_flight -= 1
                try:
                    fetched_name, payload = future.result()
                except Exception as exc:  # noqa: BLE001 - continue and report failures
                    failed.append((name, str(exc)))
                else:
                    with lock:
                        connection.execute(
                            """
                            INSERT OR REPLACE INTO package_details
                                (name, details_json, fetched_at)
                            VALUES (?, ?, ?)
                            """,
                            (
                                fetched_name,
                                json.dumps(payload, ensure_ascii=False),
                                int(time.time()),
                            ),
                        )
                        completed += 1
                        if completed % 250 == 0:
                            connection.commit()
                            print(
                                f"  {completed}/{len(missing)} fetched, "
                                f"{len(failed)} failed",
                                flush=True,
                            )
                submit_one()

            if (completed + len(failed)) % 1000 == 0:
                connection.commit()

    connection.commit()
    if failed:
        print(f"Failed package details: {len(failed)}", file=sys.stderr)
        for name, error in failed[:30]:
            print(f"  {name}: {error}", file=sys.stderr)
        if len(failed) > 30:
            print(f"  ... {len(failed) - 30} more", file=sys.stderr)
    return len(cached) + completed


_CONSTRAINT_RE = re.compile(
    r"(?P<op>\^|>=|<=|>|<|=)?\s*(?P<version>\d+(?:\.\d+){0,3})"
)


def _parse_version(value: str) -> tuple[int, int, int, int]:
    parts = [int(part) for part in value.split(".")[:4]]
    parts.extend([0] * (4 - len(parts)))
    return tuple(parts[:4])  # type: ignore[return-value]


def _branch_bounds(branch: str) -> tuple[tuple[int, int, int, int], bool, tuple[int, int, int, int], bool]:
    lower = (0, 0, 0, 0)
    lower_inclusive = True
    upper = (1_000_000, 0, 0, 0)
    upper_inclusive = False

    for match in _CONSTRAINT_RE.finditer(branch):
        operator = match.group("op") or "="
        version = _parse_version(match.group("version"))
        if operator == ">=":
            if version > lower:
                lower, lower_inclusive = version, True
        elif operator == ">":
            if version >= lower:
                lower, lower_inclusive = version, False
        elif operator == "<=":
            if version < upper:
                upper, upper_inclusive = version, True
        elif operator == "<":
            if version <= upper:
                upper, upper_inclusive = version, False
        elif operator == "^":
            if version[0] > 0:
                next_major = (version[0] + 1, 0, 0, 0)
            elif version[1] > 0:
                next_major = (0, version[1] + 1, 0, 0)
            else:
                next_major = (0, 0, version[2] + 1, 0)
            if version > lower:
                lower, lower_inclusive = version, True
            if next_major < upper:
                upper, upper_inclusive = next_major, False
        else:
            if version > lower:
                lower, lower_inclusive = version, True
            if version < upper:
                upper, upper_inclusive = version, True

    return lower, lower_inclusive, upper, upper_inclusive


def constraint_intersects_major(constraint: str | None, major: int) -> bool:
    if not constraint or not constraint.strip():
        return False
    major_start = (major, 0, 0, 0)
    major_end = (major + 1, 0, 0, 0)
    for branch in constraint.split("||"):
        lower, lower_inclusive, upper, upper_inclusive = _branch_bounds(branch)
        if lower > upper or (
            lower == upper and not (lower_inclusive and upper_inclusive)
        ):
            continue
        if upper <= major_start or lower >= major_end:
            continue
        return True
    return False


def supported_majors(payload: dict[str, Any]) -> list[int]:
    found: set[int] = set()
    for version in payload.get("versions") or []:
        pubspec = version.get("pubspec") or {}
        environment = pubspec.get("environment") or {}
        sdk = environment.get("sdk")
        for major in MAJORS:
            if constraint_intersects_major(sdk, major):
                found.add(major)
    if not found:
        found.add(3)
    return [major for major in MAJORS if major in found]


def safe_component(value: str) -> str:
    value = value.strip().replace("/", "_").replace("\\", "_")
    value = re.sub(r"[\x00-\x1f<>:\"|?*]", "_", value)
    return value.rstrip(". ") or "_"


def derive_tags(payload: dict[str, Any]) -> list[str]:
    latest = (payload.get("latest") or {}).get("pubspec") or {}
    topics = [
        str(item).strip()
        for item in latest.get("topics") or []
        if str(item).strip()
    ]
    text = " ".join(
        [
            payload.get("name") or "",
            latest.get("description") or "",
            " ".join(topics),
        ]
    ).lower()
    rules = [
        ("web", ("web", "browser", "http", "server", "api", "rest")),
        ("mobile", ("mobile", "android", "ios", "flutter")),
        ("desktop", ("desktop", "windows", "linux", "macos")),
        ("ui", ("ui", "widget", "theme", "animation", "design")),
        ("database", ("database", "sql", "sqlite", "postgres", "mysql")),
        ("serialization", ("json", "yaml", "toml", "xml", "serializ", "protobuf")),
        ("networking", ("network", "socket", "websocket", "http", "grpc")),
        ("testing", ("test", "mock", "fake", "assert")),
        ("security", ("auth", "crypto", "encrypt", "jwt", "oauth", "security")),
        ("state-management", ("state", "riverpod", "bloc", "provider")),
        ("tooling", ("cli", "build", "codegen", "generator", "lint")),
    ]
    for tag, needles in rules:
        if any(needle in text for needle in needles) and tag not in topics:
            topics.append(tag)
    return topics[:12] or ["library"]


def unique_links(items: Iterable[tuple[str, Any]]) -> list[tuple[str, str]]:
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for label, raw_url in items:
        url = str(raw_url or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        result.append((label, url))
    return result


def render_package(payload: dict[str, Any]) -> str:
    name = payload["name"]
    latest = payload.get("latest") or {}
    latest_pubspec = latest.get("pubspec") or {}
    versions = list(payload.get("versions") or [])
    versions.sort(
        key=lambda item: (
            str(item.get("published") or ""),
            str(item.get("version") or ""),
        ),
        reverse=True,
    )
    tags = derive_tags(payload)
    description = str(latest_pubspec.get("description") or "").strip()
    links = unique_links(
        [
            ("主页", latest_pubspec.get("homepage")),
            ("源码仓库", latest_pubspec.get("repository")),
            ("问题追踪", latest_pubspec.get("issue_tracker")),
            ("文档", latest_pubspec.get("documentation")),
            ("pub.dev", f"https://pub.dev/packages/{urllib.parse.quote(name)}"),
        ]
    )

    lines = [
        f"# {name}",
        "",
        f"**Tag**: {', '.join(tags)}",
        "",
        "## 简介",
        "",
        description or f"pub.dev 中央仓库中的 Dart/Flutter 包 {name}。",
        "",
        "## 官网",
        "",
    ]
    lines.extend(f"- {label}: {url}" for label, url in links)
    lines.extend(["", "## 历史版本号", ""])
    if versions:
        for version in versions:
            version_number = str(version.get("version") or "").strip()
            published = str(version.get("published") or "").strip()
            if not version_number:
                continue
            suffix = f" ({published[:10]})" if published else ""
            lines.append(f"- {version_number}{suffix}")
    else:
        lines.append("(无版本信息)")

    latest_version = str(latest.get("version") or "").strip()
    lines.extend(
        [
            "",
            "## 获取地址",
            "",
            f"- pub.dev: https://pub.dev/packages/{urllib.parse.quote(name)}",
            f"- pub 安装: `dart pub add {name}`",
            f"- Flutter 安装: `flutter pub add {name}`",
        ]
    )
    if latest_version:
        lines.append(f"- 最新版本: {latest_version}")
        lines.append(f"- 最新版归档: {latest.get('archive_url') or ''}")
        lines.append(
            f"- 版本锁定: `{name}: ^{latest_version}`"
            if re.match(r"^\d", latest_version)
            else f"- 当前版本: {latest_version}"
        )
    lines.append("- 中央仓库: https://pub.dev/")
    lines.append("")
    return "\n".join(lines)


def write_index(
    connection: sqlite3.Connection,
    package_names: Iterable[str],
) -> dict[int, int]:
    counts = {major: 0 for major in MAJORS}
    for index, name in enumerate(package_names, 1):
        row = connection.execute(
            "SELECT details_json FROM package_details WHERE name = ?", (name,)
        ).fetchone()
        if row is None:
            print(f"Missing cached details for {name}", file=sys.stderr)
            continue
        payload = json.loads(row[0])
        markdown = render_package(payload)
        component = safe_component(name)
        for major in supported_majors(payload):
            path = Path(f"dart-v{major}") / component / f"{component}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(markdown, encoding="utf-8")
            counts[major] += 1
        if index % 5000 == 0:
            print(f"  generated {index}/{len(package_names)}")
    return counts


def write_readme(counts: dict[int, int], total: int) -> None:
    major_lines = "\n".join(
        f"- `dart-v{major}`：{counts[major]} 个包" for major in MAJORS
    )
    content = f"""# Dart / Flutter 库索引

本仓库收录 pub.dev 中央仓库中的 Dart 与 Flutter 包，按 Dart 大版本与包名组织。

- 大版本目录：`dart-v2`、`dart-v3`
- 包路径：`<package>/<package>.md`
- 包会根据各历史版本声明的 Dart SDK 约束，同时出现在兼容的大版本目录中
- 当前共枚举 {total} 个 pub.dev 包

## 收录的中央仓库

| 中央仓库 | 地址 | 说明 |
| --- | --- | --- |
| pub.dev | https://pub.dev/ | Dart 与 Flutter 官方包仓库 |
| pub.dev API | https://pub.dev/api/packages | 包名、版本和 pubspec 元数据 |
| Dart 官网 | https://dart.dev/ | Dart 语言与工具链 |
| Flutter 官网 | https://flutter.dev/ | Flutter 应用框架 |

## 大版本统计

{major_lines}

## 生成方式

```bash
python tools/generate_index.py
```

生成器使用 SQLite 保存包清单和详情缓存，网络中断后可直接续跑。
"""
    Path("README.md").write_text(content, encoding="utf-8")
    for major in MAJORS:
        version_readme = f"""# Dart v{major} 库索引

- 收录来源：pub.dev 官方 API
- 包路径：`<package>/<package>.md`
- 当前共收录 {counts[major]} 个包
- 版本兼容性根据每个包历史版本的 `environment.sdk` 约束判定
"""
        Path(f"dart-v{major}").mkdir(parents=True, exist_ok=True)
        Path(f"dart-v{major}/README.md").write_text(
            version_readme, encoding="utf-8"
        )


def count_existing(version: str) -> int:
    root = Path(version)
    if not root.exists():
        return 0
    return sum(1 for _ in root.rglob("*.md")) - int((root / "README.md").exists())


def verify(counts: dict[int, int]) -> None:
    for major in MAJORS:
        actual = count_existing(f"dart-v{major}")
        if actual != counts[major]:
            raise RuntimeError(
                f"dart-v{major}: generated {counts[major]}, found {actual} files"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument(
        "--page-workers", type=int, default=DEFAULT_PAGE_WORKERS
    )
    parser.add_argument(
        "--refresh-list",
        action="store_true",
        help="discard the cached package list before fetching",
    )
    parser.add_argument(
        "--process-pool",
        action="store_true",
        help="use processes for package detail requests",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="fetch metadata but do not rewrite the markdown index",
    )
    args = parser.parse_args()

    args.cache.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(args.cache)
    try:
        init_cache(connection)
        package_list = fetch_package_list(
            connection, args.page_workers, args.refresh_list
        )
        package_names = [item["name"] for item in package_list]
        detailed = populate_details(
            connection,
            package_names,
            args.workers,
            args.process_pool,
        )
        if detailed < len(package_names):
            raise RuntimeError(
                f"incomplete metadata: {detailed}/{len(package_names)} packages"
            )
        if args.metadata_only:
            print("Metadata cache is complete.")
            return 0
        counts = write_index(connection, package_names)
        write_readme(counts, len(package_names))
        verify(counts)
        print(
            "Generated "
            + ", ".join(f"dart-v{major}={counts[major]}" for major in MAJORS)
        )
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
