import requests
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pickle
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
from lgdash.client import FootballDataClient
import lgdash.display as display

logging.basicConfig(format="| %(asctime)s | %(name)s | %(levelname)s | %(message)s")
package_logger = logging.getLogger("lgdash")
package_logger.setLevel(logging.INFO)
# package_logger.setLevel(logging.DEBUG)

FBD_ENV_VAR = "FOOTBALLDATA_API_KEY"


if __name__ == "__main__":
    api_key = os.getenv(FBD_ENV_VAR)

    if not api_key:
        raise ValueError(
            f"API key not found. Please set the {FBD_ENV_VAR} environment variable."
        )

    # client usage
    fbd_api = FootballDataClient(api_key)

    today_dt = datetime.now()
    today = today_dt.strftime("%Y-%m-%d")
    # df = fbd_api.get_matches(start_date=today, end_date=today)
    # df = fbd_api.get_matches(matchday=16)

    with open("live_matches_half_20251214.pkl", "rb") as file:
        data = pickle.load(file)
        df = fbd_api._build_matches_df(data["matches"])

    console = Console()
    display.today(console, df, "Today")
    # display.upcoming_matches(console, df, "Upcoming")

    # # upcoming matches
    # start_dt = today_dt + timedelta(days=1)
    # end_dt = today_dt + timedelta(days=30)
    # start = start_dt.strftime("%Y-%m-%d")
    # end = end_dt.strftime("%Y-%m-%d")
    # upcoming_df = fbd_api.get_matches(start_date=start, end_date=end)
    # # upcoming_df = fbd_api.get_matches(matchday=14)
    # display.upcoming(console, upcoming_df, "Schedule")

    # # standings
    # standings_meta, standings_df = fbd_api.get_standings()
    # standings_season = f"{standings_meta["season"]["startDate"][:4]}-{standings_meta["season"]["endDate"][:4]}"
    # display.standings(console, standings_df, f"Standings ({standings_season})")

    # top scorers
    # scorers_meta, scorers_df = fbd_api.get_scorers(season=2023)
    scorers_meta, scorers_df = fbd_api.get_scorers()
    scorers_season = f"{scorers_meta["season"]["startDate"][:4]}-{scorers_meta["season"]["endDate"][:4]}"
    display.top_scorers(console, scorers_df, f"Top Scorers ({scorers_season})")
