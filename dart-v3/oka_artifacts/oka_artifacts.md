# oka_artifacts

**Tag**: artifacts, storage, delta, content-addressed, mobile, ui, tooling

## 简介

Content-addressed artifact store with delta chains (ADR-0043): git stores provenance pointers, bytes live outside the codebase, and the snapshot cadence emerges from measured delta ratios. The "diff -> diff... -> snapshot only" storage shape for dills, AOT snapshots and any other build artifact class, with zstd --patch-from as the default codec behind a seam.

## 官网

- 主页: https://github.com/Arenukvern/oka
- 源码仓库: https://github.com/Arenukvern/oka/tree/main/packages/oka_artifacts
- 问题追踪: https://github.com/Arenukvern/oka/issues
- 文档: https://docs.page/arenukvern/oka
- pub.dev: https://pub.dev/packages/oka_artifacts

## 历史版本号

- 0.8.1 (2026-10-18)
- 0.8.0 (2026-10-17)
- 0.7.0 (2026-10-17)

## 获取地址

- pub.dev: https://pub.dev/packages/oka_artifacts
- pub 安装: `dart pub add oka_artifacts`
- Flutter 安装: `flutter pub add oka_artifacts`
- 最新版本: 0.8.1
- 最新版归档: https://pub.dev/api/archives/oka_artifacts-0.8.1.tar.gz
- 版本锁定: `oka_artifacts: ^0.8.1`
- 中央仓库: https://pub.dev/
