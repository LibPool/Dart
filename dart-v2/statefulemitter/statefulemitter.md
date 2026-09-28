# statefulemitter

**Tag**: web, mobile, networking, state-management

## 简介

Extended EventEmitter that fires "statechange" event when state member is changed.
Child classes that inherit from EventEmitter can use the standard event emit, subscribe, unsubscribe, etc., methods of EventEmitter. This class adds a private _state member and a setState(object) and getState() method as well as getter/setter for the getState/SetState methods.
Whenever the state is changed, a 'statechange' event will be emitted with the previous state as argument.  This allows the handler to compare old state with new state, if desired.
This package was developed as part of a port of Modus Create's IoT platform, RoboDomo from JavaScript to Dart and Flutter.  The original can be found at https://github.com/RoboDomo.

## 官网

- 主页: https://github.com/ModusLabsOrg/RoboDomo-mono
- pub.dev: https://pub.dev/packages/statefulemitter

## 历史版本号

- 1.0.2 (2021-06-10)
- 1.0.1 (2021-06-04)
- 1.0.0 (2021-05-13)

## 获取地址

- pub.dev: https://pub.dev/packages/statefulemitter
- pub 安装: `dart pub add statefulemitter`
- Flutter 安装: `flutter pub add statefulemitter`
- 最新版本: 1.0.2
- 最新版归档: https://pub.dev/api/archives/statefulemitter-1.0.2.tar.gz
- 版本锁定: `statefulemitter: ^1.0.2`
- 中央仓库: https://pub.dev/
