import click
import os
from datetime import datetime, timedelta
from .client import FootballDataClient
from .config import FBD_ENV_VAR
from .display import LeagueDashboard
from .leagues import SUPPORTED_LEAGUES, DEFAULT_LEAGUE
from . import __version__


api_key = os.getenv(FBD_ENV_VAR)
if not api_key:
    # TODO: fail more gracefully
    raise ValueError(
        f"API key not found. Please set the {FBD_ENV_VAR} environment variable."
    )


@click.group(invoke_without_command=True)
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    """Command line tool for displaying live soccer scores and statistics."""
    if not ctx.invoked_subcommand:
        click.echo("Default behavior: This is the root command.")


@cli.command()
@click.option("--league", "-l", default=DEFAULT_LEAGUE, help="League code.")
def today(league):

    if league in SUPPORTED_LEAGUES.keys():
        fbd_api = FootballDataClient(api_key)
        today = datetime.now().strftime("%Y-%m-%d")
        df, _ = fbd_api.get_matches(start_date=today, end_date=today, league=league)

        dashboard = LeagueDashboard()
        dashboard.today(league, df)
    else:
        click.echo(f"League code {league} is not supported.")


@cli.command()
@click.option("--league", "-l", default=DEFAULT_LEAGUE, help="League code")
@click.option("--days", "-d", default=7, help="Days in future.")
def schedule(league, days):

    if league in SUPPORTED_LEAGUES.keys():
        fbd_api = FootballDataClient(api_key)
        now = datetime.now()
        start_date = now.strftime("%Y-%m-%d")
        end_date = (now + timedelta(days=days)).strftime("%Y-%m-%d")
        df, _ = fbd_api.get_matches(
            start_date=start_date, end_date=end_date, league=league
        )

        dashboard = LeagueDashboard()
        dashboard.schedule(league, df)
    else:
        click.echo(f"League code {league} is not supported.")


@cli.command()
@click.option("--league", "-l", default=DEFAULT_LEAGUE, help="")
def standings(league):

    if league in SUPPORTED_LEAGUES.keys():
        fbd_api = FootballDataClient(api_key)
        df, metadata = fbd_api.get_standings(league=league)

        dashboard = LeagueDashboard()
        dashboard.standings(league, df, metadata=metadata)
    else:
        click.echo(f"League code {league} is not supported.")


@cli.command()
def leagues():
    dashboard = LeagueDashboard()
    dashboard.leagues()


# @cli.command()
# @click.argument("argument")
# def one(argument):
#     """Execute Subcommand One"""
#     click.echo(f"Subcommand One executed with argument: {argument}")


# @cli.command()
# @click.option("--flag", "-f", is_flag=True, help="A flag for Subcommand Two")
# def two(flag):
#     """Execute Subcommand Two"""
#     click.echo(f"Subcommand Two executed with flag: {flag}")


if __name__ == "__main__":
    cli()
