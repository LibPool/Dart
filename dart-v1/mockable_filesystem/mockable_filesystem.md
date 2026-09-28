# mockable_filesystem

**Tag**: desktop, testing

## 简介

Provides a FileSystem factory class for allocating File, Directory and Link objects, with two implementations - one which in turn returns the real objects from dart:io, and one which returns mock versions. This allows  tests to be written that make use of files and directories without having to create them on disk. The mock File/Directory/Link classes are not complete, but have sufficient functionality to work in most cases. The ultimate aim is to have complete mock implementations, as well as the  ability to mock Windows file systems on Linux/Mac and vice-versa, to help  with testing code for cross-platform correctness.

## 官网

- 主页: https://github.com/dart-lang/mockable_filesystem
- pub.dev: https://pub.dev/packages/mockable_filesystem

## 历史版本号

- 0.0.3 (2014-09-23)
- 0.0.1 (2013-07-24)

## 获取地址

- pub.dev: https://pub.dev/packages/mockable_filesystem
- pub 安装: `dart pub add mockable_filesystem`
- Flutter 安装: `flutter pub add mockable_filesystem`
- 最新版本: 0.0.3
- 最新版归档: https://pub.dev/api/archives/mockable_filesystem-0.0.3.tar.gz
- 版本锁定: `mockable_filesystem: ^0.0.3`
- 中央仓库: https://pub.dev/
