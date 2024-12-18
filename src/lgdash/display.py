import pandas as pd
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text

from lgdash import __version__ as version

MATCH_STATUS_ORDER = ["Live", "HT", "FT", "Upcoming", "Postponed"]


def dataframe(console: Console, df: pd.DataFrame, title: str):
    """
    Mainly used for interactive debugging and introspection.
    """
    table = Table(title=title)

    for col in df.columns:
        table.add_column(col)
    for index, row in df.iterrows():
        table.add_row(*[str(x) for x in row])

    console.print(table)


def todays_matches(console: Console, df: pd.DataFrame, title: str):

    def _sort_matches(matches_df: pd.DataFrame) -> pd.DataFrame:
        return matches_df.sort_values(
            by=["clean_status", "home_team"],
            key=lambda col: (
                col
                if col.name == "home_team"
                else col.apply(lambda x: MATCH_STATUS_ORDER.index(x))
            ),
        )

    df = _sort_matches(df)

    # all matchdays should be equal in this use case
    matchday = df["matchday"].iloc[0]
    title = f"{title} (Matchday {matchday})"
    table = Table(title=title, box=box.HORIZONTALS, show_header=True)

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
            score_display = "-"
            time_display = row["local_time"]
        if row["clean_status"] == "FT" or row["clean_status"] == "HT":
            time_display = row["clean_status"]
        if row["clean_status"] == "FT" or row["clean_status"] == "HT":
            time_display = row["clean_status"]
        if row["clean_status"] == "Postponed":
            score_display = "-"
            time_display = "Postponed"

        # home_display = Text(row["home_team"] + f" ({row["home_team_code"]})")
        # away_display = Text(row["away_team"] + f" ({row["away_team_code"]})")
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


def schedule(console: Console, df: pd.DataFrame, title: str):

    df = df.sort_values(by=["utc_datetime"]).head(10)

    table = Table(title=title, box=box.HORIZONTALS, show_header=True)

    table.add_column("Home", justify="left")
    table.add_column("Away", justify="left")
    table.add_column("Matchday", justify="left")
    table.add_column("Date", justify="left")
    table.add_column("Time", justify="left")

    for index, row in df.iterrows():

        time_display = row["display_minutes"]
        if row["clean_status"] == "Upcoming":
            time_display = row["local_time"]
        if row["clean_status"] == "FT" or row["clean_status"] == "HT":
            time_display = row["clean_status"]
        if row["clean_status"] == "FT" or row["clean_status"] == "HT":
            time_display = row["clean_status"]
        if row["clean_status"] == "Postponed":
            time_display = "Postponed"

        # home_display = Text(row["home_team"] + f" ({row["home_team_code"]})")
        # away_display = Text(row["away_team"] + f" ({row["away_team_code"]})")
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
            away_display,
            str(row["matchday"]),
            row["local_date"],
            time_display,
        )

    console.print(table)


def today(console: Console, df: pd.DataFrame, title: str):
    console.print(Text(f"⚽ League Dashboard v{version}\n", style="bold"))
    if df.empty:
        console.print(Text("No matches today ¯\\_(ツ)_/¯", style="italic"))
    else:
        todays_matches(console, df, title)
    console.print("")


def upcoming(console: Console, df: pd.DataFrame, title: str):
    console.print(Text(f"⚽ League Dashboard v{version}\n", style="bold"))
    if df.empty:
        console.print(
            Text("No matches found in next 30 days ¯\\_(ツ)_/¯", style="italic")
        )
    else:
        schedule(console, df, title)
    console.print("")


def standings(console: Console, df: pd.DataFrame, title: str):
    console.print(Text(f"⚽ League Dashboard v{version}\n", style="bold"))
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

    for index, row in df.iterrows():
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
    console.print("")


def top_scorers(console: Console, df: pd.DataFrame, title: str):
    console.print(Text(f"⚽ League Dashboard v{version}\n", style="bold"))
    table = Table(title=title, box=box.HORIZONTALS, show_header=True)

    table.add_column("Player", justify="left")
    table.add_column("Team", justify="left")
    table.add_column("Goals", justify="right")
    table.add_column("Assists", justify="right")
    table.add_column("Penalties", justify="right")

    for index, row in df.iterrows():
        table.add_row(
            row["name"],
            row["team"],
            str(row["goals"]),
            str(row["assists"]),
            str(row["penalties"]),
        )

    console.print(table)
    console.print("")
