import requests
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pickle
import pandas as pd
from rich.console import Console
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
    console = Console()

    today_dt = datetime.now()
    today = today_dt.strftime("%Y-%m-%d")
    # df, metadata = fbd_api.get_matches(start_date=today, end_date=today, league="PD")

    # with open("live_matches_half_20251214.pkl", "rb") as file:
    #     data = pickle.load(file)
    #     df = fbd_api._build_matches_df(data["matches"])

    # display.today(console, df, metadata)

    # # upcoming matches
    # start_dt = today_dt + timedelta(days=1)
    # end_dt = today_dt + timedelta(days=30)
    # start = start_dt.strftime("%Y-%m-%d")
    # end = end_dt.strftime("%Y-%m-%d")
    # upcoming_df, upcoming_meta = fbd_api.get_matches(start_date=start, end_date=end)
    # display.upcoming(console, upcoming_df, upcoming_meta)

    # standings
    standings_df, standings_meta = fbd_api.get_standings(league="PD")
    # standings_season = f"{standings_meta["season"]["startDate"][:4]}-{standings_meta["season"]["endDate"][:4]}"
    # print(standings_meta)
    display.standings(console, standings_df, standings_meta)

    # # top scorers
    # # scorers_meta, scorers_df = fbd_api.get_scorers(season="2023")
    # scorers_meta, scorers_df = fbd_api.get_scorers()
    # scorers_season = f"{scorers_meta["season"]["startDate"][:4]}-{scorers_meta["season"]["endDate"][:4]}"
    # display.top_scorers(console, scorers_df, f"Top Scorers ({scorers_season})")
