# stream_trigger

**Tag**: library

## 简介

The Stream Trigger object does exactly what the name implies. Stream Trigger can be used to either 'trigger' transformations to particular data on data streams, or trigger logic to happen elsewhere, or both.
It works by spotting the supplied trigger data on a data stream, that once spotted, will trigger the corresponding 'handler' function supplied with it to be invoked. The handler function then has the option of replacing the trigger data found on the data stream, or leaving it be.
To replace the trigger data on the stream, the trigger's given handler can either return data of the same type as the stream, or can return a stream itself of equal typing. Stream Triggers can inject/merge one data stream into another at these specific trigger points if so desired.
Again, the replacement of the trigger data does not have to occur. So if this is not desired, returning a null object from the handler will indicate the data should not change. But please note, the handler must have a return.

## 官网

- 主页: https://twitter.com/WillSquire
- pub.dev: https://pub.dev/packages/stream_trigger

## 历史版本号

- 1.0.0 (2015-01-21)

## 获取地址

- pub.dev: https://pub.dev/packages/stream_trigger
- pub 安装: `dart pub add stream_trigger`
- Flutter 安装: `flutter pub add stream_trigger`
- 最新版本: 1.0.0
- 最新版归档: https://pub.dev/api/archives/stream_trigger-1.0.0.tar.gz
- 版本锁定: `stream_trigger: ^1.0.0`
- 中央仓库: https://pub.dev/
