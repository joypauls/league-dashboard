import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from tzlocal import get_localzone

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
                    "matchday": match["matchday"],
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

        # dates and times
        system_timezone = get_localzone()
        logger.debug(f"Detected timezone {system_timezone}")
        df["local_datetime"] = df["utc_datetime"].dt.tz_convert(system_timezone)
        df["local_date"] = df["local_datetime"].dt.strftime("%Y-%m-%d")
        df["local_time"] = df["local_datetime"].dt.strftime("%H:%M")

        return self._sort_matches(df)

    def _build_standings_df(self, standings: List[Dict]) -> pd.DataFrame:
        standings_flat = []
        for team in standings:
            print(team)
            standings_flat.append(
                {
                    "position": team["position"],
                    "team": team["team"]["shortName"],
                    "tla": team["team"]["tla"],
                    "played": team["playedGames"],
                    "wins": team["won"],
                    "draws": team["draw"],
                    "losses": team["lost"],
                    "points": team["points"],
                    "goals_for": team["goalsFor"],
                    "goals_against": team["goalsAgainst"],
                    "goal_difference": team["goalDifference"],
                    # "form": team["form"],
                }
            )
        df = pd.DataFrame(standings_flat)

        return df

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
            logger.debug(f"Making request to {url}")
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

        :param start_date: start_date
        :param end_date: end_date
        :return: DataFrame containing matches
        """
        endpoint = "/v4/competitions/PL/matches"
        params = {"dateFrom": start_date, "dateTo": start_date}
        if end_date:
            params["dateTo"] = end_date
        data = self.make_request(endpoint, params=params)

        # import pickle

        # with open("live_matches_midway2_20251215.pkl", "wb") as file:
        #     pickle.dump(data, file)

        matches = data.get("matches", [])
        logger.debug(f"Retrieved {len(matches)} matches")

        return self._build_matches_df(matches)

    def get_standings(self) -> pd.DataFrame:
        """
        Fetch and process the most current league standings.

        :return: DataFrame containing standings
        """
        endpoint = "/v4/competitions/PL/standings"
        data = self.make_request(endpoint)

        standings = data.get("standings", [])
        for standing in standings:
            if standing["type"] == "TOTAL":
                standings = standing["table"]
                break
        logger.debug(f"Retrieved standings with {len(standings)} teams")

        return self._build_standings_df(standings)
