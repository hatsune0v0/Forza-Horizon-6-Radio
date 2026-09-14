# FH6 Radio

[中文](README.md) ｜ [English](README.en.md)

## FH6-radio-1.1.0

当前发布版本：[FH6-radio-1.1.0](release-prep/FH6-radio-1.1.0/)。发布压缩包可从 GitHub Releases 获取。

FH6 Radio 是一个面向 Forza Horizon 6 的 Windows 桌面音量控制工具。它接收游戏 Data Out 遥测，根据驾驶场景调整指定音频应用的音量，并提供 Material Design 风格的设置界面。

### 主要功能

- 根据自由驾驶、比赛、转场、菜单/暂停和停止状态调整音量；
- 选择一个可控音频应用，支持进程名和 EXE 路径匹配；
- 中文/English、深色/浅色主题和键盘焦点状态；
- 键盘快捷键与 XInput 手柄绑定，支持复合键输入；
- 预置电台封面、上传封面和爬取封面模式；
- 封面选择与快捷键输入完成后立即保存；
- 运行日志、主题适配滚动条和日志导出。

<img width="540" height="570" alt="image" src="https://github.com/user-attachments/assets/7e690b65-65f2-49cc-bdd3-002e3cdb3601" />

<img width="665" height="570" alt="image" src="https://github.com/user-attachments/assets/e82dfbfa-2319-4b66-ad22-2d449865eb97" />

<img width="665" height="570" alt="image" src="https://github.com/user-attachments/assets/c9751a6d-688f-4c97-8d94-1f4630cd36f4" />

<img width="606" height="570" alt="image" src="https://github.com/user-attachments/assets/2727a8ff-257d-40b7-aaa0-db79a2e6cfd5" />

<img width="664" height="345" alt="image" src="https://github.com/user-attachments/assets/4641f848-f875-4f23-a241-980062083a9e" />


## 安装与运行

1. 从 GitHub Releases 下载并解压 `FH6-radio-1.1.0.zip` 到有写入权限的目录。
2. 保持完整目录结构，运行 `FH6 Radio v1.1.0/FH6 Radio v1.1.0.exe`。
3. 在 Forza Horizon 6 中启用 Data Out，默认监听 `127.0.0.1:5300`。
4. 在应用中选择音频应用，再配置音量、快捷键和电台封面。

不要只复制 EXE；`_internal` 目录和同级资源必须与 EXE 一起保留。配置文件保存在 `%APPDATA%\\FH6RadioV02`。

## 注意事项
没有进行针对网易云音乐、酷狗音乐、Apple Music、腾讯音乐的专项测试，目前版本不保证能成功爬取这些软件的专辑封面

## 从源码运行

需要 Python 3.12 和 [uv](https://docs.astral.sh/uv/)：

```powershell
uv sync --frozen --extra dev --extra build --extra overlay
uv run fh6-radio-v02-material
```

运行测试：

```powershell
uv run pytest -q
```

## 隐私与兼容

应用仅在本机监听 FH6 Data Out，并将配置和运行日志写入用户目录。缺少 Windows 音频或输入依赖时会安全降级并显示提示。原始 `地平线电台.exe` 保持只读，旧版本配置和发布目录彼此隔离。

## 初版来源

感谢ILLEMIUN的授权，解包现成的软件也是节省了不少工作量：XD

【地平线6自定义电台-支持所有音乐播放软件-哔哩哔哩】 
https://b23.tv/sFVwHlH
