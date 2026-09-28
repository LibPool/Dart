# Dart / Flutter 库索引

本仓库收录 pub.dev 中央仓库中的 Dart 与 Flutter 包，按 Dart 大版本与包名组织。

- 大版本目录：`dart-v1`、`dart-v2`、`dart-v3`
- 包路径：`<package>/<package>.md`
- 包会根据各历史版本声明的 Dart SDK 约束，同时出现在兼容的大版本目录中
- 当前共枚举 90792 个 pub.dev 包

## 收录的中央仓库

| 中央仓库 | 地址 | 说明 |
| --- | --- | --- |
| pub.dev | https://pub.dev/ | Dart 与 Flutter 官方包仓库 |
| pub.dev API | https://pub.dev/api/packages | 包名、版本和 pubspec 元数据 |
| Dart 官网 | https://dart.dev/ | Dart 语言与工具链 |
| Flutter 官网 | https://flutter.dev/ | Flutter 应用框架 |

## 大版本统计

- `dart-v1`：4003 个包
- `dart-v2`：45486 个包
- `dart-v3`：57951 个包

## 生成方式

```bash
python tools/generate_index.py
```

生成器使用 SQLite 保存包清单和详情缓存，网络中断后可直接续跑。
