import requests
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
from tzlocal import get_localzone

logger = logging.getLogger(__name__)


def convert_status(status: Optional[str]) -> str:
    if status == "IN_PLAY":
        return "Live"
    if status == "PAUSED":
        return "HT"
    if status == "FINISHED":
        return "FT"
    if status == "TIMED":
        return "Upcoming"
    if status == "SCHEDULED":
        return "Upcoming"
    if status == "POSTPONED":
        return "Postponed"
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
        df["matchday"] = df["matchday"].astype("Int64")

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

        return df

    def _build_standings_df(self, standings: List[Dict]) -> pd.DataFrame:
        standings_flat = []
        for team in standings:
            standings_flat.append(
                {
                    "position": team["position"],
                    "team": team["team"]["shortName"],
                    "tla": team["team"]["tla"],
                    "points": team["points"],
                    "played": team["playedGames"],
                    "won": team["won"],
                    "draw": team["draw"],
                    "lost": team["lost"],
                    "goals_for": team["goalsFor"],
                    "goals_against": team["goalsAgainst"],
                    "goal_difference": team["goalDifference"],
                    # "form": team["form"],
                }
            )
        df = pd.DataFrame(standings_flat)

        # format columns
        df["points"] = df["points"].astype("Int64")
        df["played"] = df["played"].astype("Int64")
        df["won"] = df["won"].astype("Int64")
        df["draw"] = df["draw"].astype("Int64")
        df["lost"] = df["lost"].astype("Int64")
        df["goals_for"] = df["goals_for"].astype("Int64")
        df["goals_against"] = df["goals_against"].astype("Int64")
        df["goal_difference"] = df["goal_difference"].astype("Int64")

        return df

    def _build_scorers_df(self, scorers: List[Dict]) -> pd.DataFrame:
        scorers_flat = []
        for scorer in scorers:
            scorers_flat.append(
                {
                    "name": scorer["player"]["name"],
                    "team": scorer["team"]["shortName"],
                    "goals": scorer["goals"],
                    "assists": scorer["assists"],
                    "penalties": scorer["penalties"],
                }
            )
        df = pd.DataFrame(scorers_flat)

        # format columns
        df["goals"] = df["goals"].astype("Int64").fillna(0)
        df["assists"] = df["assists"].astype("Int64").fillna(0)
        df["penalties"] = df["penalties"].astype("Int64").fillna(0)

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
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        matchday: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch and process matches.

        :param start_date: start_date
        :param end_date: end_date
        :return: DataFrame containing matches
        """
        endpoint = "/v4/competitions/PL/matches"
        params = {}
        # matchday takes precedence
        if matchday:
            params["matchday"] = matchday
        elif start_date and end_date:
            params["dateFrom"] = start_date
            params["dateTo"] = end_date
        data = self.make_request(endpoint, params=params)

        # import pickle

        # with open("live_matches_midway2_20251215.pkl", "wb") as file:
        #     pickle.dump(data, file)

        matches = data.get("matches", [])
        logger.debug(f"Retrieved {len(matches)} matches")
        if not matches:
            return pd.DataFrame()

        return self._build_matches_df(matches)

    def get_standings(self, season: Optional[int] = None) -> Tuple[Dict, pd.DataFrame]:
        """
        Fetch and process the most current league standings.

        :param season: Season/Year (e.g. 2024 for 2024/2025)
        :return: DataFrame containing standings
        """
        endpoint = "/v4/competitions/PL/standings"
        params = {}
        if season:
            params["season"] = season
        data = self.make_request(endpoint, params=params)

        standings = data.get("standings", [])
        # is this going to need to be different for different leagues?
        for standing in standings:
            if standing["type"] == "TOTAL":
                standings = standing["table"]
                break
        logger.debug(f"Retrieved standings with {len(standings)} teams")

        metadata = {}
        for key in data:
            if key != "standings":
                metadata[key] = data[key]

        return metadata, self._build_standings_df(standings)

    def get_scorers(
        self, season: Optional[int] = None, limit: Optional[int] = 10
    ) -> Tuple[Dict, pd.DataFrame]:
        """
        Fetch and process the most current top scorers.

        :param season: Season/Year (e.g. 2024 for 2024/2025)
        :return: DataFrame containing top scorers
        """
        endpoint = "/v4/competitions/PL/scorers"
        params = {"limit": limit}
        if season:
            params["season"] = season
        data = self.make_request(endpoint, params=params)

        season_metadata = data.get("season", {})
        if season_metadata:
            stages = season_metadata.get("stages", [])
            if len(stages) > 1:
                raise NotImplementedError(
                    "Multiple stages found in season, not yet fully supported"
                )

        scorers = data.get("scorers", [])
        logger.debug(f"Retrieved {len(scorers)} top scorers")

        metadata = {}
        for key in data:
            if key != "scorers":
                metadata[key] = data[key]

        return metadata, self._build_scorers_df(scorers)
