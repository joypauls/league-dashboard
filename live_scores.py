import requests
import logging
import os
from typing import Dict, List, Optional
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
        Initialize the football-data.com API client.

        :param api_key: Your API key for football-data.com
        """
        self.base_url = "https://api.football-data.org"
        self.api_key = api_key

    def make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the FootyStats API.

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
                "Failed to communicate with football-data.com API."
            ) from e


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
    data = fbd_api.make_request(
        "/v4/competitions/PL/matches",
        params={"dateFrom": "2024-12-14", "dateTo": "2024-12-14"},
    )
    print(data)
