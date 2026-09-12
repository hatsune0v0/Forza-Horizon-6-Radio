# Clean-room provenance

## Scope

This directory contains an independently written first v0.2 slice. The parser
and state machine are pure; settings/fade helpers and the UDP/runtime modules
are thin, injectable adapters. There is still no Windows audio-session writer,
user interface, media integration, process inspection, build or distribution code.

## Allowed requirement sources

These user-provided product documents were used for behavioral requirements:

- `docs/09-v0.2-phase2-state-machine-design.md` (local requirement source)
- `docs/01-product-requirements.md` (local requirement source)

The generic Codex test-driven-development procedure was also read for development process guidance. It was not used as a product or implementation source.

## Prohibited sources

The implementation and tests were freshly authored for this staging tree. They were not copied from or intentionally adapted from:

- any v0.1 source code or tests;
- any current `fh6_radio_v02_*` implementation or tests;
- reverse-engineering analysis or extracted evidence;
- existing `dist`, `build`, packaged executables, or generated artifacts;
- any older staging tree.

This provenance note records engineering inputs and method; it is not a legal clean-room certification or a determination of authorship or publication rights.

## Method

The public API and behavioral tests were drafted from the user requirements and a provisional public protocol profile (FMData activity at byte 0, little-endian U32 0/1; race position U8 at byte 314): https://github.com/austinbaccus/forza-telemetry/tree/88aa7d59ac2684e16ef57862555c93f2af1a7ce3. That profile is FH4/5-compatible public evidence, not validated FH6 protocol authority. Tests were created first, their initial run was observed failing, and fresh Python modules were then written with new names and control flow. Runtime and UDP tests use localhost and injected sinks only; they do not access FH6 or a real audio device. Verification runs were performed only with the working directory set to this clean staging directory.

The earlier guessed interpretation of offsets 304/308/312 as RPM/speed fields was discarded. This slice intentionally exposes only the two fields needed by the state machine; bytes 304, 308, and 312 are ignored. No state decision uses RPM or speed.
