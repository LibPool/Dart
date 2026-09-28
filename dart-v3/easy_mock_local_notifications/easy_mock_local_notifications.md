# easy_mock_local_notifications

**Tag**: mobile, testing

## 简介

Makes flutter_local_notifications work under `flutter test`. mockLocalNotifications.init() registers the real Android platform impl (the native registrant that normally does this doesn't run in tests, so the plugin throws a LateInitializationError) and stubs its `dexterous.com/flutter/ local_notifications` MethodChannel via easy_mock_channel — real Dart, no native.

## 官网

- 主页: https://github.com/Ahmed-Omar-Hommir/easy_mock
- 问题追踪: https://github.com/Ahmed-Omar-Hommir/easy_mock/issues
- pub.dev: https://pub.dev/packages/easy_mock_local_notifications

## 历史版本号

- 0.1.0 (2026-08-15)

## 获取地址

- pub.dev: https://pub.dev/packages/easy_mock_local_notifications
- pub 安装: `dart pub add easy_mock_local_notifications`
- Flutter 安装: `flutter pub add easy_mock_local_notifications`
- 最新版本: 0.1.0
- 最新版归档: https://pub.dev/api/archives/easy_mock_local_notifications-0.1.0.tar.gz
- 版本锁定: `easy_mock_local_notifications: ^0.1.0`
- 中央仓库: https://pub.dev/
