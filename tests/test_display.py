import pandas as pd
from lgdash.display import (
    _extract_season_from_metadata,
    _extract_score_from_row,
    _extract_time_from_row,
)


def test_extract_season_from_metadata():
    metadata = {
        "season": {
            "startDate": "2024-01-01",
            "endDate": "2025-01-01",
        }
    }
    season_str = _extract_season_from_metadata(metadata)
    assert season_str == "2024/2025"


def test_extract_score_from_row():
    row = pd.Series(
        {
            "clean_status": "FT",
            "home_score": 3,
            "away_score": 1,
        }
    )
    score_str = _extract_score_from_row(row)
    assert score_str == "3 - 1"

    row = pd.Series({"clean_status": "Live", "home_score": 2, "away_score": 5})
    score_str = _extract_score_from_row(row)
    assert score_str == "2 - 5"

    row = pd.Series(
        {
            "clean_status": "Upcoming",
            "home_score": None,
            "away_score": None,
        }
    )
    score_str = _extract_score_from_row(row)
    assert score_str == "-"


def test_extract_time_from_row():
    row = pd.Series(
        {
            "clean_status": "FT",
        }
    )
    time_str = _extract_time_from_row(row)
    assert time_str == "FT"

    row = pd.Series(
        {
            "clean_status": "Live",
            "display_minutes": "42'",
        }
    )
    time_str = _extract_time_from_row(row)
    assert time_str == "42'"

    row = pd.Series(
        {
            "clean_status": "Upcoming",
            "local_time": "15:00",
            "local_tz": "CST",
        }
    )
    time_str = _extract_time_from_row(row)
    assert time_str == "15:00 CST"
