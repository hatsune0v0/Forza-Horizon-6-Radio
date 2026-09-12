# Contributing

Keep changes within the independently written v0.2 implementation. Do not
submit the original executable, extracted or reverse-engineering evidence,
user configuration, Spotify credentials, game files, or local build output.

Run the test suite and compile check before opening a change:

```text
python -B -m pytest -p no:cacheprovider -q
python -B -m compileall -q fh6_radio_clean_v02 tests
```

Changes to Windows audio, Spotify metadata, overlay integration, or FH6
telemetry must include deterministic tests using injected or synthetic data.

