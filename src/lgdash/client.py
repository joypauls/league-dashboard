import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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