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

## Installation and Usage

1. Download and extract `FH6-radio-1.1.0.zip` from GitHub Releases to a writable folder.
2. Keep the directory structure intact and run `FH6 Radio v1.1.0/FH6 Radio v1.1.0.exe`.
3. Enable Data Out in Forza Horizon 6; the default listener is `127.0.0.1:5300`.
4. Select an audio application, then configure volume, shortcuts, and radio covers.

Do not copy only the EXE. Keep `_internal` and sibling resources with it. Configuration is stored in `%APPDATA%\\FH6RadioV02`.

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

## Documentation

- [Standards index](docs/README.md)
- [Release and packaging](docs/06-release-and-packaging.md)
- [Bilingual implementation record](docs/21-bilingual-execution-2026-09-13.md)
- [Development log](devlog/README.md)

## Privacy and Compatibility

The application listens to FH6 Data Out locally and stores configuration and runtime logs in the user profile. It degrades safely with readable messages when Windows audio or input dependencies are unavailable. The original `地平线电台.exe` remains read-only, and legacy configurations and release directories stay isolated.
