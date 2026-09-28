# debug

**Tag**: web, mobile, networking

## 简介

This is something of a clone/work-alike of the JavaScript debug package by TJ Holowaychuck at https://github.com/visionmedia/debug. Use:
  import 'package:debug/debug.dart';
  final debug = Debug('any_key_you_like')

  ...
  debug('any string you like, as if you called print()');

The DEBUG environment variable is checked to see if anything should be printed.  You can specify multiple keys in DEBUG by separating them with semicolon.  The * key matches ALL keys for all debugs.
This package was developed as part of a port of Modus Create's IoT platform, RoboDomo from JavaScript to Dart and Flutter.  The original can be found at https://github.com/RoboDomo.

## 官网

- 主页: https://github.com/ModusLabs/RoboDomo-mono
- pub.dev: https://pub.dev/packages/debug

## 历史版本号

- 1.0.0 (2021-05-13)

## 获取地址

- pub.dev: https://pub.dev/packages/debug
- pub 安装: `dart pub add debug`
- Flutter 安装: `flutter pub add debug`
- 最新版本: 1.0.0
- 最新版归档: https://pub.dev/api/archives/debug-1.0.0.tar.gz
- 版本锁定: `debug: ^1.0.0`
- 中央仓库: https://pub.dev/
