# FH6 Radio

[中文](README.md) | [English](README.en.md)

这是 FH6 Radio 的独立重写 v0.2 开发版本。项目包含遥测解析、场景状态机、音量目标适配、键盘与 Xbox/XInput 输入控制、媒体提示协调器和 Material 风格界面外壳。项目不包含原始 EXE、解包证据、用户配置或 Spotify 凭据。

## 安装与运行

需要 Python 3.12 和 `uv`：

```text
uv sync --frozen --extra dev --extra ui
uv run python -m fh6_radio_clean_v02
```

运行测试：

```text
uv run pytest -p no:cacheprovider -q
```

Windows onedir 预览位于 `release/FH6-Radio-Clean-v0.2-windows/`，必须保留其中的 `_internal` 目录。程序不会修改 FH6 游戏文件。

## 功能介绍

- **FH6 遥测与场景识别**：接收 Data Out UDP 数据，识别自由漫游、比赛、转场、暂停和停止等状态。
- **按场景调节音量**：根据当前场景平滑设置目标应用音量，支持安全静音和状态切换。
- **受控应用选择**：可将音量控制绑定到 Spotify、Chrome 或其他可写 Windows 音频会话，避免误改其他应用。
- **键盘与 Xbox/XInput 控制**：支持播放、暂停、切歌和电台启停等输入控制，并可在运行时安全降级。
- **媒体提示与电台信息**：显示当前播放状态、歌曲信息和封面，并根据 FH6 前台和场景状态控制提示显示。
- **自定义电台封面**：支持使用用户自己的封面资源，并在资源不可用时回退到默认封面。
- **Material 风格桌面界面**：提供导航、主题、音量、输入、提示和日志页面，支持深色/浅色及主题色设置。
- **安全降级与可诊断性**：缺少 pycaw、XInput 或系统媒体接口时仍可启动，并显示可读状态或错误信息。

<img width="540" height="580" alt="image" src="https://github.com/user-attachments/assets/8efe16f6-7120-4f36-a45c-d14a0f43bfd9" /> 

<img width="730" height="640" alt="image" src="https://github.com/user-attachments/assets/066ab4ed-4f26-442e-bb1e-9c39dd5f40b4" />




## 实机验证

当前公开版本已完成以下实机验证：

- FH6：Data Out 连接和场景状态流程；
- Spotify：播放状态和目标音频会话控制；
- Chrome：作为可选受控音频目标进行音量控制。

以上验证针对当前独立重写版本完成。自动化测试仍不能替代不同硬件、系统音频设备和 FH6 配置下的用户复测。

## 功能与限制

可选的 Windows `pycaw` 音频桥接在缺少依赖时会安全降级。Spotify 账号/OAuth 登录和 WinRT 媒体元数据不是本 clean-room 版本的公开实现；播放器可通过系统媒体会话或用户已运行的应用进行验证。FH6 324 字节遥测配置仍应由用户按自身 Data Out 设置复核。

场景判断只使用活动状态和比赛排名证据，不使用速度、RPM、轮胎转速、圈数或位置坐标作为判定依据。

## 发布目录

`release/FH6-Radio-Clean-v0.2-windows/` 是完整 Windows onedir 预览，包含 `_internal`、许可声明、校验文件和运行说明。解压后必须保持目录结构完整，不能只复制 EXE。

## Clean-room 来源说明

本仓库是依据产品需求和公开协议资料独立编写的 v0.2 实现，不复制历史 v0.1 实现、解包证据或旧发布目录。详细来源、范围和限制见 [PROVENANCE.md](PROVENANCE.md)。
