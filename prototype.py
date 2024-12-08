import requests
import logging
import os
from typing import Dict, List, Optional
import pandas as pd
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FootyStatsClientError(Exception):
    """Custom exception for FootyStats API errors."""

    pass


class FootyStatsClient:
    def __init__(self, api_key: str):
        """
        Initialize the FootyStats API client.

        :param api_key: Your API key for FootyStats
        """
        self.base_url = "https://api.football-data-api.com"
        self.api_key = api_key

    def make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the FootyStats API.

        :param endpoint: The API endpoint (e.g., 'league-matches' or 'team-stats')
        :param params: Additional parameters for the request
        :return: Parsed JSON response as a dictionary
        """
        if params is None:
            params = {}
        params["key"] = self.api_key
        url = f"{self.base_url}/{endpoint}"

        try:
            logger.info(f"Making request to {url} with params {params}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise FootyStatsClientError(data["error"])
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise FootyStatsClientError(
                "Failed to communicate with FootyStats API."
            ) from e

    # @lru_cache(maxsize=128)
    def get_league_table(self, league_id: int) -> pd.DataFrame:
        """
        Fetch and process the league table for a specific league.

        :param league_id: The ID of the league
        :return: DataFrame containing the league table
        """
        endpoint = "league-tables"
        params = {"league_id": league_id}
        data = self.make_request(endpoint, params)

        # Parse table data
        table = data.get("data", {}).get("league_table", [])
        if not table:
            logger.warning("No league table data available.")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(table)

        df = df[
            [
                "position",
                "name",
                "matchesPlayed",
                "seasonWins_overall",
                "seasonDraws_overall",
                "seasonLosses_overall",
            ]
        ]

        # Add additional processing if needed (e.g., sorting, filtering)
        df = df.sort_values(by="position").reset_index(drop=True)
        return df

    def display_dataframe(self, df: pd.DataFrame):
        """
        Display a DataFrame in a structured format.

        :param df: DataFrame to display
        """
        if df.empty:
            logger.info("No data available to display.")
        else:
            print(df.head())


# Example usage
if __name__ == "__main__":
    api_key = os.getenv("FOOTYSTATS_API_KEY")
    print(api_key)

    if not api_key:
        raise ValueError(
            "API key not found. Please set the FOOTYSTATS_API_KEY environment variable."
        )

    footy_api = FootyStatsClient(api_key)

    # current league_id for Premier League
    pl_league_id = 12325
    league_table_df = footy_api.get_league_table(pl_league_id)
    footy_api.display_dataframe(league_table_df)
