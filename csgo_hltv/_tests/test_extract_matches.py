from csgo_hltv.extract_matches import Extract


def test_check_files():
    extract = Extract
    assert not (extract is None)
