# disposito

**Tag**: analyzer-plugin, lints, static-analysis, memory, mobile, ui, state-management, tooling

## 简介

Analyzer plugin for object lifetimes: fields annotated with @Disposable must be cleaned up by the class that declares them, objects that own a lifecycle must not be created during a Flutter build, and a State must not hand itself out of its own dispose or build a late field during teardown.

## 官网

- 主页: https://github.com/arxdeus/disposito
- 问题追踪: https://github.com/arxdeus/disposito/issues
- pub.dev: https://pub.dev/packages/disposito

## 历史版本号

- 1.0.1 (2026-09-21)
- 0.2.3 (2025-05-18)
- 0.2.2 (2025-03-23)
- 0.2.1 (2025-03-21)
- 0.2.0 (2025-03-21)
- 0.1.0 (2025-03-20)

## 获取地址

- pub.dev: https://pub.dev/packages/disposito
- pub 安装: `dart pub add disposito`
- Flutter 安装: `flutter pub add disposito`
- 最新版本: 1.0.1
- 最新版归档: https://pub.dev/api/archives/disposito-1.0.1.tar.gz
- 版本锁定: `disposito: ^1.0.1`
- 中央仓库: https://pub.dev/
