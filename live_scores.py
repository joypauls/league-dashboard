import requests
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime

# import numpy as np
import pandas as pd

# from functools import lru_cache
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FBD_ENV_VAR = "FOOTBALLDATA_API_KEY"
# 2024-2025 season
# TODO: automate retreiving this with API
# CURRENT_PL_LEAGUE_ID = 12325
# CURRENT_PL_SEASON = "2024-2025"


class FootballDataClientError(Exception):
    """Custom exception for football-data.com API errors."""

    pass


class FootballDataClient:
    def __init__(self, api_key: str):
        """
        Initialize the football-data.org API client.

        :param api_key: Your API key for football-data.org
        """
        self.base_url = "https://api.football-data.org"
        self.api_key = api_key

    def make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the API.

        :param endpoint: The API endpoint
        :param params: Additional parameters for the request
        :return: Parsed JSON response as a dictionary
        """
        if params is None:
            params = {}
        headers = {"X-Auth-Token": self.api_key}
        url = f"{self.base_url}/{endpoint}"

        try:
            # logger.info(f"Making request to {url} with params {params}")
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise FootballDataClientError(data["error"])
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise FootballDataClientError(
                "Failed to communicate with football-data.org API."
            ) from e


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

        home_display = Text(row["home_team"])
        away_display = Text(row["away_team"])
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
            # row["clean_status"],
        )

    console.print(table)


if __name__ == "__main__":
    api_key = os.getenv(FBD_ENV_VAR)

    if not api_key:
        raise ValueError(
            f"API key not found. Please set the {FBD_ENV_VAR} environment variable."
        )

    # client usage
    fbd_api = FootballDataClient(api_key)
    data = fbd_api.make_request(
        "/v4/competitions/PL/matches", params={"status": "LIVE"}
    )

    today = datetime.now().strftime("%Y-%m-%d")

    data = fbd_api.make_request(
        "/v4/competitions/PL/matches",
        params={"dateFrom": today, "dateTo": today},
    )

    import pickle

    # with open("live_matches_full_20251214.pkl", "wb") as file:
    #     pickle.dump(data, file)

    # with open("live_matches_half_20251214.pkl", "rb") as file:
    #     data = pickle.load(file)

    def convert_score(score: Optional[int]) -> str:
        if pd.isna(score):
            return "-"
        return str(int(score))

    def convert_status(status: Optional[str]) -> str:
        if status == "IN_PLAY":
            return "Live"
        if status == "PAUSED":
            return "HT"
        if status == "FINISHED":
            return "FT"
        if status == "TIMED":
            return "Upcoming"
        if status == "TIMED":
            return "Upcoming"
        return status

    def create_display_minutes(
        minutes: Optional[int], injury_time: Optional[int]
    ) -> str:
        # print(type(minutes), type(injury_time))
        if pd.isna(minutes):
            return "-"
        elif pd.isna(injury_time):
            return f"{minutes}'"
        return f"{minutes}+{injury_time}'"

    #     return f"{score['fullTime']['home']} - {score['fullTime']['away']}

    matches = data.get("matches", [])
    matches_flat = []
    for match in matches:
        matches_flat.append(
            {
                "home_team": match["homeTeam"]["shortName"],
                "home_score": match["score"]["fullTime"]["home"],
                "away_score": match["score"]["fullTime"]["away"],
                "away_team": match["awayTeam"]["shortName"],
                "status": match["status"],
                "minute": match["minute"],
                "injury_time": match["injuryTime"],
                # "utc_date": match["utcDate"],
            }
        )

    df = pd.DataFrame(matches_flat)

    # formatting of dataset
    # nullable integers for score
    df["home_score"] = df["home_score"].astype("Int64")
    df["away_score"] = df["away_score"].astype("Int64")
    df["minute"] = df["minute"].astype("Int64")
    df["injury_time"] = df["injury_time"].astype("Int64")
    # print(df.dtypes)

    # convert for display
    # df["home_score"] = df["home_score"].apply(convert_score)
    # df["away_score"] = df["away_score"].apply(convert_score)
    df["clean_status"] = df["status"].apply(convert_status)
    df["display_minutes"] = df.apply(
        lambda row: create_display_minutes(row["minute"], row["injury_time"]), axis=1
    )

    status_order = ["Live", "HT", "FT", "Upcoming"]
    # df = df.sort_values(
    #     by="clean_status", key=lambda col: col.apply(lambda x: status_order.index(x))
    # )
    df = df.sort_values(
        by=["clean_status", "home_team"],
        key=lambda col: (
            col
            if col.name == "home_team"
            else col.apply(lambda x: status_order.index(x))
        ),
    )

    console = Console()
    console.print(Text("⚽ League Dashboard\n", style="bold"))
    # display_dataframe(console, df, "Today")
    display_score_table(console, df, "Today's Matches")
