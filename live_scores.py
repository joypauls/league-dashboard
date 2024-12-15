import requests
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pickle

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
MATCH_STATUS_ORDER = ["Live", "HT", "FT", "Upcoming"]


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


def convert_display_minutes(minutes: Optional[int], injury_time: Optional[int]) -> str:
    # print(type(minutes), type(injury_time))
    if pd.isna(minutes):
        return "-"
    elif pd.isna(injury_time):
        return f"{minutes}'"
    return f"{minutes}+{injury_time}'"


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

    def _sort_matches(self, matches_df: pd.DataFrame) -> pd.DataFrame:
        return matches_df.sort_values(
            by=["clean_status", "home_team"],
            key=lambda col: (
                col
                if col.name == "home_team"
                else col.apply(lambda x: MATCH_STATUS_ORDER.index(x))
            ),
        )

    def _build_matches_df(self, matches: List[Dict]) -> pd.DataFrame:
        matches_flat = []
        for match in matches:
            matches_flat.append(
                {
                    "home_team": match["homeTeam"]["shortName"],
                    "home_team_code": match["homeTeam"]["tla"],
                    "home_score": match["score"]["fullTime"]["home"],
                    "away_team": match["awayTeam"]["shortName"],
                    "away_team_code": match["awayTeam"]["tla"],
                    "away_score": match["score"]["fullTime"]["away"],
                    "status": match["status"],
                    "minute": match["minute"],
                    "injury_time": match["injuryTime"],
                    "utc_datetime": match["utcDate"],
                }
            )
        df = pd.DataFrame(matches_flat)

        # format columns
        df["utc_datetime"] = pd.to_datetime(df["utc_datetime"])
        # nullable integers
        df["home_score"] = df["home_score"].astype("Int64")
        df["away_score"] = df["away_score"].astype("Int64")
        df["minute"] = df["minute"].astype("Int64")
        df["injury_time"] = df["injury_time"].astype("Int64")

        # convert values for new columns
        df["clean_status"] = df["status"].apply(convert_status)
        df["display_minutes"] = df.apply(
            lambda row: convert_display_minutes(row["minute"], row["injury_time"]),
            axis=1,
        )

        return self._sort_matches(df)

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

    def get_matches(
        self, start_date: str, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch and process matches.

        Currently, PL (Premier League) is hardcoded.

        :param start_date: start_date
        :param end_date: end_date
        :return: DataFrame containing matches
        """
        endpoint = "/v4/competitions/PL/matches"
        params = {"dateFrom": start_date, "dateTo": start_date}
        if end_date:
            params["dateTo"] = end_date
        data = self.make_request(endpoint, params=params)

        matches = data.get("matches", [])

        return self._build_matches_df(matches)


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
