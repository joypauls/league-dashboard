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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FBD_ENV_VAR = "FOOTBALLDATA_API_KEY"


def display_dataframe(console: Console, df: pd.DataFrame, title: str):
    table = Table(title=title)

    for col in df.columns:
        table.add_column(col)
    for index, row in df.iterrows():
        table.add_row(*[str(x) for x in row])

    console.print(table)


def display_score_table(console: Console, df: pd.DataFrame, title: str):
    table = Table(title=title, box=box.HORIZONTALS)

    table.add_column("Home", justify="right")
    table.add_column("Score", justify="center")
    table.add_column("Away", justify="left")
    table.add_column("Time", justify="left")
    # just for debugging
    # table.add_column("state", justify="left")

    for index, row in df.iterrows():

        score_display = f"{row['home_score']} - {row['away_score']}"
        time_display = row["display_minutes"]
        if row["clean_status"] == "Upcoming":
            score_display = ""
            time_display = ""
        if row["clean_status"] == "FT" or row["clean_status"] == "HT":
            time_display = row["clean_status"]

        home_display = Text(row["home_team"] + f" ({row["home_team_code"]})")
        away_display = Text(row["away_team"] + f" ({row["away_team_code"]})")
        if not pd.isna(row["home_score"]):
            if row["home_score"] > row["away_score"]:
                home_display.stylize("orange1")
                away_display.stylize("blue")
            elif row["home_score"] < row["away_score"]:
                home_display.stylize("blue")
                away_display.stylize("orange1")
            else:
                home_display.stylize("blue")
                away_display.stylize("blue")

        table.add_row(
            home_display,
            score_display,
            away_display,
            time_display,
        )

    console.print(table)


def display_dashboard(console: Console, df: pd.DataFrame, title: str):
    console.print(Text("⚽ League Dashboard\n", style="bold"))
    display_score_table(console, df, title)
    console.print("")


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
    display_dashboard(console, df, "Today")

    # start_dt = today_dt + timedelta(days=1)
    # end_dt = today_dt + timedelta(days=7)
    # start = start_dt.strftime("%Y-%m-%d")
    # end = end_dt.strftime("%Y-%m-%d")
    # upcoming_df = fbd_api.get_matches(start, end)
    # display_score_table(console, upcoming_df, "Upcoming")
