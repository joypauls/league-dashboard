import click
import os
from datetime import datetime, timedelta
from rich.console import Console
from .client import FootballDataClient
from .config import FBD_ENV_VAR
from .display import today as today_display


api_key = os.getenv(FBD_ENV_VAR)
if not api_key:
    raise ValueError(
        f"API key not found. Please set the {FBD_ENV_VAR} environment variable."
    )


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """CLI App with Default Behavior and Subcommands"""
    if not ctx.invoked_subcommand:
        click.echo("Default behavior: This is the root command.")


@cli.command()
@click.option("--league", "-l", help="")
def live(league):
    # click.echo(f"Subcommand live executed with option: {league}")

    fbd_api = FootballDataClient(api_key)
    console = Console()

    today_dt = datetime.now()
    today = today_dt.strftime("%Y-%m-%d")
    df, metadata = fbd_api.get_matches(start_date=today, end_date=today, league=league)

    today_display(console, df, metadata)


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
