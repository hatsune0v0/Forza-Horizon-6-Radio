# Architecture

The rewrite keeps telemetry parsing, state transitions, audio targeting, input
capture, media/overlay coordination and the Qt shell in separate modules.
Runtime and UDP services accept injectable dependencies so tests do not touch a
real game, mixer or Spotify account. Windows integrations are optional adapters
and must degrade to a readable no-op when unavailable.

The UI shell never reads UDP packets or writes audio sessions directly. A
production integration should connect those boundaries through an application
controller and retain the same stop/close cleanup guarantees.

