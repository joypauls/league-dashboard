import click


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """CLI App with Default Behavior and Subcommands"""
    if not ctx.invoked_subcommand:
        click.echo("Default behavior: This is the root command.")


@cli.command()
@click.argument("argument")
def one(argument):
    """Execute Subcommand One"""
    click.echo(f"Subcommand One executed with argument: {argument}")


@cli.command()
@click.option("--flag", "-f", is_flag=True, help="A flag for Subcommand Two")
def two(flag):
    """Execute Subcommand Two"""
    click.echo(f"Subcommand Two executed with flag: {flag}")


if __name__ == "__main__":
    cli()
