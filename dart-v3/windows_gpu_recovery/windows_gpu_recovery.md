# windows_gpu_recovery

**Tag**: windows, gpu, d3d11, recovery, plugin, mobile, desktop

## 简介

Flutter Windows plugin that recovers from EGL_CONTEXT_LOST / D3D11 device removed (DXGI_ERROR_DEVICE_REMOVED) after system sleep or GPU driver reset. Uses a sentinel D3D11 device for detection and a Vectored Exception Handler to safely destroy the dead engine and create a fresh one.

## 官网

- 源码仓库: https://github.com/DitriXNew/windows_gpu_recovery
- 问题追踪: https://github.com/DitriXNew/windows_gpu_recovery/issues
- pub.dev: https://pub.dev/packages/windows_gpu_recovery

## 历史版本号

- 0.1.0 (2026-04-02)

## 获取地址

- pub.dev: https://pub.dev/packages/windows_gpu_recovery
- pub 安装: `dart pub add windows_gpu_recovery`
- Flutter 安装: `flutter pub add windows_gpu_recovery`
- 最新版本: 0.1.0
- 最新版归档: https://pub.dev/api/archives/windows_gpu_recovery-0.1.0.tar.gz
- 版本锁定: `windows_gpu_recovery: ^0.1.0`
- 中央仓库: https://pub.dev/
