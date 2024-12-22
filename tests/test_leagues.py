from lgdash.leagues import SUPPORTED_LEAGUES


# tests consistency of dictionary keys, more like data validation?
def test_supported_leagues():
    required_keys = ["icon", "name"]
    has_required_keys = all(
        all(k in league for k in required_keys) for league in SUPPORTED_LEAGUES.values()
    )
    assert has_required_keys
