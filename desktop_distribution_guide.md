# 桌面版分发指南

## 打包

进入：

```text
desktop/electron-wrapper
```

运行：

```bat
build_desktop_windows.bat
```

生成结果在：

```text
desktop/electron-wrapper/dist/
```

## 分发前检查

- Windows 10 / 11 启动测试
- 桌面快捷方式测试
- 卸载测试
- 网络异常提示测试
- 杀毒误报检查
- 首次打开是否能自动进入线上地址

## 当前桌面版定位

当前是线上网页的桌面壳，适合试用和小范围分发。正式商业版后续可加入本地缓存、自动更新、崩溃日志和更完整安装器。
