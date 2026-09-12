# Telemetry Profile

The parser currently accepts a provisional 324-byte Horizon-compatible packet:

- byte 0: little-endian unsigned activity flag, strictly `0` or `1`;
- byte 314: unsigned race position, where a non-zero value is evidence of a
  race state.

The state machine requires consecutive observations before entering or leaving
race mode. Speed, RPM, wheel rotation, lap count and coordinates are not used.
This profile is based on public FH4/FH5 references and still requires
independent FH6 validation before claiming wire compatibility.

