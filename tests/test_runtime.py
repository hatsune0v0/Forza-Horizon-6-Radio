from fh6_radio_clean_v02 import Runtime, Scene, VolumeSettings


class Sink:
    def __init__(self):
        self.volumes = []
        self.intents = []

    def set_volume(self, value):
        self.volumes.append(value)

    def set_playback(self, intent):
        self.intents.append(intent)


def packet(position=0, race_on=1):
    data = bytearray(324)
    data[0] = race_on
    data[314] = position
    return bytes(data)


def test_runtime_applies_configured_scene_volume_and_dedupes():
    sink = Sink()
    runtime = Runtime(VolumeSettings(free_roam=100, race=60), sink=sink)
    runtime.start()
    runtime.ingest(packet(), now=0.0, fh6_running=True)
    runtime.ingest(packet(), now=0.1, fh6_running=True)
    runtime.ingest(packet(), now=0.2, fh6_running=True)
    assert sink.volumes[-1] == 1.0
    count = len(sink.volumes)
    runtime.tick(now=0.3, fh6_running=True)
    assert len(sink.volumes) == count


def test_runtime_stops_safely_without_audio_adapter():
    runtime = Runtime()
    runtime.start()
    status = runtime.ingest(packet(), now=2.0, fh6_running=True)
    assert status.diagnostic == "audio adapter unavailable"
    closed = runtime.close()
    assert closed.publication.current_scene is Scene.STOPPED


def test_force_sync_reapplies_current_target():
    sink = Sink()
    runtime = Runtime(VolumeSettings(race=50), sink=sink)
    runtime.start()
    for i in range(3):
        runtime.ingest(packet(position=1), now=i * 0.1, fh6_running=True)
    before = len(sink.volumes)
    runtime.force_sync()
    assert len(sink.volumes) == before + 1 and sink.volumes[-1] == 0.5


def test_injected_clock_drives_stale_timeout():
    now = [10.0]
    runtime = Runtime(clock=lambda: now[0])
    runtime.ingest(packet(), fh6_running=True)
    now[0] = 11.1
    status = runtime.tick(fh6_running=True)
    assert status.publication.current_scene is Scene.TRANSITION
