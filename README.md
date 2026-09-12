# FH6 Radio — independent rewrite work in progress

## 中文说明

这是 FH6 Radio 的独立重写 v0.2 开发版本，包含遥测解析、场景状态机、
音量目标适配、输入控制、媒体提示协调器和 Material 风格界面外壳。
项目不包含原始 EXE、解包证据、用户配置或 Spotify 凭据。

### 安装与运行

需要 Python 3.12 和 `uv`：

```text
uv sync --frozen --extra dev --extra ui
uv run python -m fh6_radio_clean_v02
```

运行测试：

```text
uv run pytest -p no:cacheprovider -q
```

Windows onedir 预览位于 `release/FH6-Radio-Clean-v0.2-windows/`，必须保留
其中的 `_internal` 目录。当前版本仍是独立重写开发版，FH6 协议和实际音频
控制需要用户自行验证；不会修改 FH6 游戏文件。

## English

This repository contains an independently written v0.2 implementation slice.
It includes a pure state/effect core, settings and fade logic, UDP/runtime
adapters, keyboard/XInput capture, media/overlay coordination, and a minimal
Material UI shell. The optional Windows audio bridge is isolated and degrades
safely when pycaw is unavailable. Spotify account/OAuth integration and FH6
wire compatibility remain provisional; the existing installed application is
unchanged.

The new implementation is authored from product requirements and separately
documented public protocol facts, without copying the historical implementation.
This is a development method, not a legal certification. See `PROVENANCE.md`.

## Validation

Python 3.12 is required. With `uv`, install the development and UI extras:

```text
uv sync --frozen --extra dev --extra ui
uv run pytest -p no:cacheprovider -q
```

The `audio` extra enables the optional Windows pycaw bridge; the `build`
extra enables PyInstaller. These integrations are intentionally optional.

Synthetic tests do not certify FH6 wire compatibility or actual audio behavior.
The provisional 324-byte Horizon packet profile needs independent FH6 validation.
Only the activity flag and race-position evidence are relevant to scene selection;
speed, RPM, wheel rotation, lap number and position coordinates must not be used.
The public staging tree currently contains 14 deterministic test modules; local
historical test suites are intentionally not part of this clean-room rewrite.

## Publication status

The public tree intentionally excludes Python environments, caches, build
output, reverse-engineering evidence, user configuration and credentials.
The `release/FH6-Radio-Clean-v0.2-windows/` directory contains the complete
onedir Windows preview, including `_internal`, `SHA256SUMS`, license notices
and a minimal run guide. Keep that directory intact when extracting it.

The modules are deliberately adapter-oriented: `Runtime` accepts injected
audio and process probes, `UdpService` can be stopped without owning a game or
player process, and `StrictAudioTarget` enforces exact names before writing to
an injected session provider. `MaterialWindow` exposes navigation and
callbacks but does not read UDP or audio sessions directly. Passing synthetic
tests does not certify FH6 wire compatibility or third-party audio control.

## Local build preview

With PyInstaller installed, a preview onedir build can be produced without
reading the original project:

```text
python -m PyInstaller --noconfirm --clean fh6_radio_clean_v02.spec --distpath build-preview/dist --workpath build-preview/work
```

The output is an onedir UI-shell preview, not a release candidate. It does not
include Spotify OAuth or WinRT metadata integration.
