import pandas as pd
from typing import Dict
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text

from .leagues import SUPPORTED_LEAGUES

# MATCH_STATUS_ORDER = ["Live", "HT", "FT", "Upcoming", "Postponed"]


def _extract_season_from_metadata(metadata: Dict) -> str:
    season_start_year = metadata["season"]["startDate"][:4]
    season_end_year = metadata["season"]["endDate"][:4]
    season = (
        f"{season_start_year}/{season_end_year}"
        if season_start_year != season_end_year
        else season_start_year
    )
    return season


def _extract_score_from_row(row: pd.Series) -> str:
    if row["clean_status"] == "Upcoming" or row["clean_status"] == "Postponed":
        return "-"
    return f"{row['home_score']} - {row['away_score']}"


def _extract_time_from_row(row: pd.Series) -> str:
    if row["clean_status"] == "Upcoming":
        return row["local_time"] + " " + row["local_tz"]
    if row["clean_status"] == "Live":
        return row["display_minutes"]
    # FT / HT / Postponed
    return row["clean_status"]


def print_dataframe(console: Console, df: pd.DataFrame, title: str):
    """
    Mainly used for interactive debugging and introspection.
    """
    table = Table(title=title)

    for col in df.columns:
        table.add_column(col)
    for _, row in df.iterrows():
        table.add_row(*[str(x) for x in row])

    console.print(table)


def print_todays_matches(console: Console, df: pd.DataFrame, title: str):

    # def _sort_matches(matches_df: pd.DataFrame) -> pd.DataFrame:
    #     return matches_df.sort_values(
    #         by=["clean_status", "local_datetime", "home_team"],
    #         key=lambda col: (
    #             col
    #             if col.name == "local_datetime" or col.name == "home_team"
    #             else col.apply(lambda x: MATCH_STATUS_ORDER.index(x))
    #         ),
    #     )
    # df = _sort_matches(df)

    df.sort_values(by=["utc_datetime", "home_team"], inplace=True)

    table = Table(title=title, box=box.HORIZONTALS, show_header=True)
    table.add_column("Home", justify="right")
    table.add_column("Score", justify="center")
    table.add_column("Away", justify="left")
    table.add_column("Time", justify="left")

    for _, row in df.iterrows():

        score_display = _extract_score_from_row(row)
        time_display = _extract_time_from_row(row)

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
        )

    console.print(table)


def print_upcoming_matches(console: Console, df: pd.DataFrame, title: str):

    df.sort_values(by=["utc_datetime"], inplace=True)
    # only show upcoming matches
    # as of now timezones can make today's matches show up otherwise
    df = df[df["clean_status"] == "Upcoming"]

    table = Table(title=title, box=box.HORIZONTALS, show_header=True)
    table.add_column("Home", justify="left")
    table.add_column("Away", justify="left")
    table.add_column("Date", justify="left")
    table.add_column("Time", justify="left")

    for _, row in df.iterrows():

        time_display = _extract_time_from_row(row)

        home_display = Text(row["home_team"])
        away_display = Text(row["away_team"])

        table.add_row(
            home_display,
            away_display,
            row["local_date"],
            time_display,
        )

    console.print(table)


def print_standings(console: Console, df: pd.DataFrame, metadata: Dict):
    season_str = _extract_season_from_metadata(metadata)
    title = f"Standings ({season_str})" if season_str else "Standings"

    table = Table(title=title, box=box.HORIZONTALS, show_header=True)
    table.add_column("", justify="right")
    table.add_column("Team", justify="left")
    table.add_column("Points", justify="right")
    table.add_column("Played", justify="right")
    table.add_column("W", justify="right")
    table.add_column("D", justify="right")
    table.add_column("L", justify="right")
    table.add_column("GF", justify="right")
    table.add_column("GA", justify="right")
    table.add_column("GD", justify="center")

    for _, row in df.iterrows():
        table.add_row(
            str(row["position"]),
            row["team"],
            str(row["points"]),
            str(row["played"]),
            str(row["won"]),
            str(row["draw"]),
            str(row["lost"]),
            str(row["goals_for"]),
            str(row["goals_against"]),
            str(row["goal_difference"]),
        )

    console.print(table)


def print_leagues(console: Console):
    table = Table(title="Supported Leagues", box=box.HORIZONTALS)
    table.add_column("Name")
    table.add_column("Code")
    for league in SUPPORTED_LEAGUES:
        table.add_row(SUPPORTED_LEAGUES[league]["name"], league)
    console.print(table)


def print_teams(console: Console, df: pd.DataFrame):

    df.sort_values(by=["team"], inplace=True)

    table = Table(title="Teams", box=box.HORIZONTALS)
    table.add_column("Name")
    table.add_column("Full Name")
    table.add_column("Country")
    for _, row in df.iterrows():
        table.add_row(row["team"], row["team_long"], row["area"])
    console.print(table)


# def top_scorers(console: Console, df: pd.DataFrame, title: str):
#     # console.print(Text(f"⚽ lgdash v{version}\n", style="bold"))
#     console.print(Text("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League"))
#     console.print("")
#     table = Table(title=title, box=box.HORIZONTALS, show_header=True)

#     table.add_column("Player", justify="left")
#     table.add_column("Team", justify="left")
#     table.add_column("Goals", justify="right")
#     table.add_column("Assists", justify="right")
#     # table.add_column("Penalties", justify="right")

#     for index, row in df.iterrows():
#         table.add_row(
#             row["name"],
#             row["team"],
#             str(row["goals"]),
#             str(row["assists"]),
#             # str(row["penalties"]),
#         )

#     console.print(table)
#     console.print("")


class LeagueDashboard:
    def __init__(self):
        self.console = Console()

    def _league_header(self, league_code: str):
        league_header = (
            SUPPORTED_LEAGUES[league_code]["icon"]
            + " "
            + SUPPORTED_LEAGUES[league_code]["name"]
        )
        self.console.print(Text(league_header))

    def today(self, league_code: str, df: pd.DataFrame):
        self._league_header(league_code)
        self.console.print("")
        if df.empty:
            self.console.print(Text("No matches today ¯\\_(ツ)_/¯", style="italic"))
        else:
            print_todays_matches(self.console, df, "Today's Matches")
        self.console.print("")

    def standings(self, league_code: str, df: pd.DataFrame, metadata: Dict):
        self._league_header(league_code)
        self.console.print("")
        if df.empty:
            self.console.print(Text("No standings found ¯\\_(ツ)_/¯", style="italic"))
        else:
            print_standings(self.console, df, metadata)
        self.console.print("")

    def schedule(self, league_code: str, df: pd.DataFrame):
        self._league_header(league_code)
        self.console.print("")
        if df.empty:
            self.console.print(
                Text("No upcoming matches found ¯\\_(ツ)_/¯", style="italic")
            )
        else:
            print_upcoming_matches(self.console, df, "Upcoming Matches")
        self.console.print("")

    def leagues(self):
        self.console.print("")
        print_leagues(self.console)
        self.console.print("")

    def teams(self, league_code: str, df: pd.DataFrame):
        self._league_header(league_code)
        self.console.print("")
        print_teams(self.console, df)
        self.console.print("")
