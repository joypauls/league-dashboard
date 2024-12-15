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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    df = fbd_api.get_matches(today)

    # with open("live_matches_full_20251214.pkl", "wb") as file:
    #     pickle.dump(data, file)

    # with open("live_matches_half_20251214.pkl", "rb") as file:
    #     data = pickle.load(file)
    #     df = fbd_api._build_matches_df(data["matches"])

    console = Console()
    display.dashboard(console, df, "Today")

    # start_dt = today_dt + timedelta(days=1)
    # end_dt = today_dt + timedelta(days=7)
    # start = start_dt.strftime("%Y-%m-%d")
    # end = end_dt.strftime("%Y-%m-%d")
    # upcoming_df = fbd_api.get_matches(start, end)
    # display_score_table(console, upcoming_df, "Upcoming")
