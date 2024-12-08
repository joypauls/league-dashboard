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

FS_ENV_VAR = "FOOTYSTATS_API_KEY"
# 2024-2025 season
# TODO: automate retreiving this with API
CURRENT_PL_LEAGUE_ID = 12325
CURRENT_PL_SEASON = "2024-2025"


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

        :param endpoint: The API endpoint
        :param params: Additional parameters for the request
        :return: Parsed JSON response as a dictionary
        """
        if params is None:
            params = {}
        params["key"] = self.api_key
        url = f"{self.base_url}/{endpoint}"

        try:
            # logger.info(f"Making request to {url} with params {params}")
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
    def get_league_table(self, season_id: int) -> pd.DataFrame:
        """
        Fetch and process the league table for a specific league.

        :param league_id: The ID of the league
        :return: DataFrame containing the league table
        """
        endpoint = "league-tables"
        params = {"season_id": season_id}
        data = self.make_request(endpoint, params)

        # parse table data
        table = data.get("data", {}).get("league_table", [])
        if not table:
            logger.warning("No league table data available.")
            return pd.DataFrame()

        df = pd.DataFrame(table)
        df = df.sort_values(by="position").reset_index(drop=True)
        return df

    def get_league_players(self, season_id: int) -> pd.DataFrame:
        """
        Fetch and process the players for a specific league.

        :param league_id: The ID of the league
        :return: DataFrame containing the league table
        """
        endpoint = "league-players"

        page_data = []
        page = 1
        has_more_data = True
        while has_more_data:
            params = {"season_id": season_id, "page": page}
            data = self.make_request(endpoint, params)

            # parse table data
            table = data.get("data", {})
            if not table:
                logger.warning("No league players data available.")
                return pd.DataFrame()

            df = pd.DataFrame(table)
            page_data.append(df)

            pagination_data = data.get("pager", {})
            has_more_data = page < pagination_data.get("max_page", page)
            page += 1

        df = pd.concat(page_data)
        # df = df.sort_values(by="position").reset_index(drop=True)
        return df


def clean_league_table(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {
        "position": "Position",
        "cleanName": "Team",
        "points": "Points",
        "matchesPlayed": "Played",
        "seasonWins_overall": "W",
        "seasonDraws_overall": "D",
        "seasonLosses_overall": "L",
        "seasonGoals": "GF",
        "seasonConceded": "GA",
        "seasonGoalDifference": "GD",
    }
    df = df[list(col_map.keys())]
    df = df.rename(columns=col_map)
    return df


def clean_league_players(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {
        "known_as": "Name",
        "goals_overall": "Goals",
        # "points": "Points",
        # "matchesPlayed": "Played",
        # "seasonWins_overall": "W",
        # "seasonDraws_overall": "D",
        # "seasonLosses_overall": "L",
        # "seasonGoals": "GF",
        # "seasonConceded": "GA",
        # "seasonGoalDifference": "GD",
    }
    df = df[list(col_map.keys())]
    df = df.rename(columns=col_map)
    return df


def filter_top_scorers(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(by="Goals", ascending=False).reset_index(drop=True).head(10)


def display_dataframe(df: pd.DataFrame, title: str):
    console = Console()
    table = Table(title=title)

    for col in df.columns:
        table.add_column(col)
    for index, row in df.iterrows():
        table.add_row(*[str(x) for x in row])

    console.print(table)


# def display_league_table(df: pd.DataFrame, title: str):
#     console = Console()
#     table = Table(title=title)

#     qualification_positions = [1, 2, 3, 4, 5, 18, 19, 20]
#     qualification_colors = [
#         "blue",
#         "blue",
#         "blue",
#         "blue",
#         "green",
#         "red",
#         "red",
#         "red",
#     ]
#     # PL_QUALIFICATION_MAP = []
#     #     1: "Champions League",
#     #     2: "Champions League",
#     #     3: "Champions League",
#     #     4: "Champions League",
#     #     5: "Europa League",
#     #     18: "Relegation",
#     #     19: "Relegation",
#     #     20: "Relegation",
#     # }
#     for col in df.columns:
#         table.add_column(col)
#     for _, row in df.iterrows():
#         if row["Position"] in qualification_positions:
#             color = qualification_colors[qualification_positions.index(row["Position"])]
#             row["Team"] = f"[{color}]{row['Team']}[/{color}]"
#         table.add_row(*[str(x) for x in row])

#     console.print(table)


if __name__ == "__main__":
    api_key = os.getenv(FS_ENV_VAR)

    if not api_key:
        raise ValueError(
            f"API key not found. Please set the {FS_ENV_VAR} environment variable."
        )

    # client usage
    footy_api = FootyStatsClient(api_key)
    league_table_df = footy_api.get_league_table(CURRENT_PL_LEAGUE_ID)
    league_players_df = footy_api.get_league_players(CURRENT_PL_LEAGUE_ID)

    # league table
    league_table_df = clean_league_table(league_table_df)
    display_dataframe(league_table_df, f"Premier League Table {CURRENT_PL_SEASON}")

    # league players
    league_players_df = clean_league_players(league_players_df)
    print(league_players_df.shape)
    display_dataframe(
        filter_top_scorers(league_players_df),
        f"Premier League Players {CURRENT_PL_SEASON}",
    )
