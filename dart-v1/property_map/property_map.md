# property_map

**Tag**: web, ui, serialization

## 简介

PropertyMap allows you to quickly implement property bags in dart. It consists of 2 main classes: PropertyMap and PropertyList.
PropertyMap is a wrapper around Map<String, dynamic>. PropertyList is a wrapper around List<dynamic>.
The benefit of using them is that they can restrict the data that is added to them so it is possible to guarantee serialization, and they convert children Maps and Lists recursively to propertyMaps and PropertyLists.
By default, they can only take simple objects (as defined in dart:json) and Serializable objects. The configuration object passed to the constructor allows you to modify this behavior if needed.

## 官网

- 主页: https://github.com/sethillgard/property_map
- pub.dev: https://pub.dev/packages/property_map

## 历史版本号

- 0.0.16 (2013-02-04)
- 0.0.15 (2013-02-02)
- 0.0.14 (2013-01-31)
- 0.0.13 (2013-01-27)
- 0.0.12 (2013-01-26)
- 0.0.11 (2013-01-26)
- 0.0.1 (2013-01-14)

## 获取地址

- pub.dev: https://pub.dev/packages/property_map
- pub 安装: `dart pub add property_map`
- Flutter 安装: `flutter pub add property_map`
- 最新版本: 0.0.16
- 最新版归档: https://pub.dev/api/archives/property_map-0.0.16.tar.gz
- 版本锁定: `property_map: ^0.0.16`
- 中央仓库: https://pub.dev/
