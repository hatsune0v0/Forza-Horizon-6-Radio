# FH6 Radio

[中文](README.md) ｜ [English](README.en.md)

## FH6-radio-1.1.0

Current release: [FH6-radio-1.1.0](release-prep/FH6-radio-1.1.0/). Download the ZIP from GitHub Releases.

FH6 Radio is a Windows desktop volume controller for Forza Horizon 6. It reads game Data Out telemetry, adjusts a selected audio application's volume by driving context, and provides a Material Design settings interface.

### Features

- Context-aware volume for free roam, race, transition, menu/pause, and stopped states;
- Select one controllable audio application by process name or EXE path;
- Chinese/English, dark/light themes, and keyboard focus states;
- Keyboard shortcuts and XInput controller bindings;
- Preset covers, uploaded covers, and crawled cover mode;
- Cover selections and shortcut changes are saved immediately;
- Runtime logs, theme-aware scrolling, and log export.

<img width="606" height="570" alt="image" src="https://github.com/user-attachments/assets/4aff6d09-272c-4a7a-a966-5cac00598563" />

<img width="606" height="726" alt="image" src="https://github.com/user-attachments/assets/2c440bf1-45e5-4654-8447-9f9d5ae2873d" />

<img width="606" height="726" alt="image" src="https://github.com/user-attachments/assets/8a493df2-3e07-48f0-bbbc-55c1bf97fb5f" />

<img width="606" height="726" alt="image" src="https://github.com/user-attachments/assets/448c2d22-6efa-4545-9edb-26e77f5232d6" />

<img width="664" height="345" alt="image" src="https://github.com/user-attachments/assets/c3b71d1b-accf-4489-99de-a73c8b35086c" />


## Installation and Usage

1. Download and extract `FH6-radio-1.1.0.zip` from GitHub Releases to a writable folder.
2. Keep the directory structure intact and run `FH6 Radio v1.1.0/FH6 Radio v1.1.0.exe`.
3. Enable Data Out in Forza Horizon 6; the default listener is `127.0.0.1:5300`.
4. Select an audio application, then configure volume, shortcuts, and radio covers.

Do not copy only the EXE. Keep `_internal` and sibling resources with it. Configuration is stored in `%APPDATA%\\FH6RadioV02`.

## Important Notes

This project has not been specifically tested with NetEase Cloud Music, Kugou Music, Apple Music, or Tencent Music. Therefore, the current version does not guarantee successful retrieval of album artwork from these platforms.

## Run From Source

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/):

```powershell
uv sync --frozen --extra dev --extra build --extra overlay
uv run fh6-radio-v02-material
```

Run tests:

```powershell
uv run pytest -q
```

## Privacy and Compatibility

The application listens to FH6 Data Out locally and stores configuration and runtime logs in the user profile. It degrades safely with readable messages when Windows audio or input dependencies are unavailable. The original `地平线电台.exe` remains read-only, and legacy configurations and release directories stay isolated.

## Original Version Source
Thanks to ILLEMIUN for the authorization🎉

【地平线6自定义电台-支持所有音乐播放软件-哔哩哔哩】 https://b23.tv/sFVwHlH
