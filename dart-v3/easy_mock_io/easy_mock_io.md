# easy_mock_io

**Tag**: mobile, testing

## 简介

In-memory dart:io for Flutter tests. mockMemoryIO.init() swaps IOOverrides.global for a MemoryFileSystem, so File and Directory access runs in memory and never touches disk. File locks are no-ops (parallel tests can't deadlock on the same file), the UNIT_TEST_ASSETS folder is seeded into the memory filesystem, and application directories under /app_root are pre-created.

## 官网

- 主页: https://github.com/Ahmed-Omar-Hommir/easy_mock
- 问题追踪: https://github.com/Ahmed-Omar-Hommir/easy_mock/issues
- pub.dev: https://pub.dev/packages/easy_mock_io

## 历史版本号

- 0.1.1 (2026-09-19)
- 0.1.0 (2026-08-15)

## 获取地址

- pub.dev: https://pub.dev/packages/easy_mock_io
- pub 安装: `dart pub add easy_mock_io`
- Flutter 安装: `flutter pub add easy_mock_io`
- 最新版本: 0.1.1
- 最新版归档: https://pub.dev/api/archives/easy_mock_io-0.1.1.tar.gz
- 版本锁定: `easy_mock_io: ^0.1.1`
- 中央仓库: https://pub.dev/
