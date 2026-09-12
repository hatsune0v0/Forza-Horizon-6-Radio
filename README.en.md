# FH6 Radio

[中文](README.md) | [English](README.en.md)

This repository contains an independently written FH6 Radio v0.2 implementation. It includes telemetry parsing, a scene state machine, audio-target adaptation, keyboard and Xbox/XInput input control, media/overlay coordination, and a Material style UI shell. It does not contain the original executable, reverse-engineering evidence, user configuration, or Spotify credentials.

## Install and run

Python 3.12 and `uv` are required:

```text
uv sync --frozen --extra dev --extra ui
uv run python -m fh6_radio_clean_v02
```

Run the tests with:

```text
uv run pytest -p no:cacheprovider -q
```

The Windows onedir preview is in `release/FH6-Radio-Clean-v0.2-windows/`. Keep its `_internal` directory. The application does not modify FH6 game files.

## Hardware validation

The current public version has been validated on real hardware with:

- FH6: Data Out connectivity and scene-state flow;
- Spotify: playback state and controlled audio-session volume;
- Chrome: volume control as an optional controlled audio target.

These checks cover the current independent rewrite. Automated tests cannot replace user verification on different hardware, Windows audio devices, or FH6 settings.

## Features and limitations

The optional Windows `pycaw` audio bridge degrades safely when unavailable. Spotify account/OAuth login and WinRT media metadata are not part of this public clean-room implementation; playback can be validated through the system media session or a user-run application. The provisional 324-byte FH6 telemetry profile should still be checked against the user's own Data Out settings.

Scene selection uses only activity state and race-position evidence. It does not use speed, RPM, wheel rotation, lap count, or position coordinates.

## Release directory

`release/FH6-Radio-Clean-v0.2-windows/` is a complete Windows onedir preview with `_internal`, license notices, checksums, and a run guide. Keep the directory layout intact after extraction; do not copy only the executable.

## Clean-room provenance

This repository is an independently written v0.2 implementation based on product requirements and public protocol material. It does not copy the historical v0.1 implementation, extracted evidence, or older release directories. See [PROVENANCE.md](PROVENANCE.md) for scope, sources, and limitations.
