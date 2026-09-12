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
