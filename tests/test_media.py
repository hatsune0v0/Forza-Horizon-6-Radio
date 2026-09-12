from fh6_radio_clean_v02 import Track, normalize_track, track_key


def test_track_metadata_is_normalized_and_keyed_without_account_data():
    track = normalize_track(Track("  Blue Hour ", "  Artist ", "  Album "))
    assert track == Track("Blue Hour", "Artist", "Album", None)
    assert track_key(track) == ("blue hour", "artist")


def test_incomplete_track_is_hidden():
    assert normalize_track(Track("", "Artist")) is None
    assert track_key(None) is None
