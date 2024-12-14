import requests
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from functools import lru_cache
from rich.console import Console
from rich.table import Table

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


def display_dataframe(df: pd.DataFrame, title: str):
    console = Console()
    table = Table(title=title)

    for col in df.columns:
        table.add_column(col)
    for index, row in df.iterrows():
        table.add_row(*[str(x) for x in row])

    console.print(table)


if __name__ == "__main__":
    api_key = os.getenv(FBD_ENV_VAR)

    if not api_key:
        raise ValueError(
            f"API key not found. Please set the {FBD_ENV_VAR} environment variable."
        )

    # client usage
    fbd_api = FootballDataClient(api_key)
    # data = fbd_api.make_request(
    #     "/v4/competitions/PL/matches", params={"status": "LIVE"}
    # )

    today = datetime.now().strftime("%Y-%m-%d")

    data = fbd_api.make_request(
        "/v4/competitions/PL/matches",
        params={"dateFrom": today, "dateTo": today},
    )

    matches = data.get("matches", [])
    matches_flat = []
    for match in matches:
        matches_flat.append(
            {
                "home_team": match["homeTeam"]["shortName"],
                "away_team": match["awayTeam"]["shortName"],
                "home_score": match["score"]["fullTime"]["home"],
                "away_score": match["score"]["fullTime"]["away"],
                "status": match["status"],
                "utc_date": match["utcDate"],
            }
        )

    df = pd.DataFrame(matches_flat)

    display_dataframe(df, "Today's Matches")
