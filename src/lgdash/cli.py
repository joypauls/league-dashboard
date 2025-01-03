import click
import os
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional

from lgdash.client import FootballDataClient
from lgdash.config import FBD_ENV_VAR
from lgdash.display import LeagueDashboard
from lgdash.leagues import SUPPORTED_LEAGUES, DEFAULT_LEAGUE
from lgdash import __version__

# TODO: should move this logic so user can use --help without the API key
api_token = os.getenv(FBD_ENV_VAR)
if not api_token:
    # TODO: fail more gracefully
    raise ValueError(
        f"API token not found. Please set the {FBD_ENV_VAR} environment variable."
    )
client = FootballDataClient(api_token)
dashboard = LeagueDashboard()


def _filter_to_team(df: pd.DataFrame, team: Optional[str]) -> pd.DataFrame:
    # TODO: normalize team names to allow for case-insensitive matching
    team_lower = team.lower()
    if team:
        return df[
            (df["home_team"].str.lower() == team_lower)
            | (df["away_team"].str.lower() == team_lower)
        ]
    return df


@click.group(invoke_without_command=True)
@click.version_option(__version__)
@click.pass_context
@click.option("--league", "-l", default=DEFAULT_LEAGUE, help="League code.")
def cli(ctx, league):
    """
    Command line tool for displaying live soccer scores and statistics.
    Default behavior is to show today's matches.
    """
    if not ctx.invoked_subcommand:
        if league in SUPPORTED_LEAGUES.keys():
            today = datetime.now().strftime("%Y-%m-%d")
            df, _ = client.get_matches(start_date=today, end_date=today, league=league)

            dashboard.today(league, df)
        else:
            click.echo(f"League code {league} is not supported.")


@cli.command()
@click.option("--league", "-l", type=str, default=DEFAULT_LEAGUE, help="League code")
@click.option("--team", "-t", type=str, help="Team name, as it appears in the app")
@click.option("--days", "-d", type=int, default=7, help="Days in future")
def schedule(league, team, days):
    """
    Scheduled matches after today. Defaults to next 14 days.
    """
    if league in SUPPORTED_LEAGUES.keys():
        now = datetime.now()
        start_date = now.strftime("%Y-%m-%d")
        end_date = (now + timedelta(days=days)).strftime("%Y-%m-%d")
        df, _ = client.get_matches(
            start_date=start_date, end_date=end_date, league=league
        )

        # okay if df becomes empty, dashboard handles that case
        if team:
            df = df if df.empty else _filter_to_team(df, team)

        dashboard.schedule(league, df)
    else:
        click.echo(f"League code {league} is not supported.")


@cli.command()
@click.option("--league", "-l", default=DEFAULT_LEAGUE, help="")
def standings(league):
    """
    Current standings for the league.
    """
    if league in SUPPORTED_LEAGUES.keys():
        df, metadata = client.get_standings(league=league)

        dashboard.standings(league, df, metadata=metadata)
    else:
        click.echo(f"League code {league} is not supported.")


@cli.command()
def leagues():
    """
    Supported leagues and their codes for reference.
    """
    dashboard.leagues()


@cli.command()
@click.option("--league", "-l", default=DEFAULT_LEAGUE, help="")
def teams(league):
    """
    List of teams in the league for reference.
    """
    if league in SUPPORTED_LEAGUES.keys():
        df, _ = client.get_teams(league=league)

        dashboard.teams(league, df)
    else:
        click.echo(f"League code {league} is not supported.")


###########
# Web App #
###########


# @cli.command()
# def server():
#     """Start a web server for browser-based experience."""
#     # Path to the streamlit app script
#     script_path = os.path.join(os.path.dirname(__file__), "app.py")
#     try:
#         subprocess.run(["streamlit", "run", script_path], check=True)
#     except FileNotFoundError:
#         click.echo(
#             "Streamlit is not installed. Please install it with:\n"
#             "pip install lgdash[web]"
#         )
#     except subprocess.CalledProcessError as e:
#         click.echo(f"Failed to start app: {e}")


if __name__ == "__main__":
    cli()
