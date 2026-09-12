from fh6_radio_clean_v02 import StrictAudioTarget


class Session:
    def __init__(self, name, fail=False):
        self.process_name = name
        self.fail = fail
        self.values = []

    def set_volume(self, value):
        if self.fail:
            raise RuntimeError("write failed")
        self.values.append(value)


class Provider:
    def __init__(self, sessions):
        self._sessions = sessions

    def sessions(self):
        return self._sessions


def test_strict_target_writes_all_matching_sessions_only():
    spotify = Session("Spotify.exe")
    second = Session("spotify")
    helper = Session("spotifyhelper.exe")
    chrome = Session("Chrome.exe")
    report = StrictAudioTarget(Provider([spotify, second, helper, chrome]), ("Spotify.exe", "Spotify")).write(0.75)
    assert report.matched == report.written == 2
    assert spotify.values == [0.75] and second.values == [0.75]
    assert helper.values == chrome.values == []


def test_one_session_failure_does_not_block_other_matches():
    failed = Session("Spotify.exe", fail=True)
    good = Session("Spotify.exe")
    report = StrictAudioTarget(Provider([failed, good])).write(0.5)
    assert (report.matched, report.written, report.failed) == (2, 1, 1)
    assert good.values == [0.5]


def test_missing_provider_and_no_match_are_safe():
    assert StrictAudioTarget(None).write(0.5).diagnostic == "audio session provider unavailable"
    report = StrictAudioTarget(Provider([Session("Chrome.exe")])).write(0.5)
    assert report.matched == report.written == 0
    assert report.diagnostic == "target application not running or has no audio session"
