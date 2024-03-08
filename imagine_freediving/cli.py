import click
from imagine_freediving.subcommands.visualize import visualize
from imagine_freediving.subcommands.overlay import overlay


@click.group()
def cli():
    pass


def main():
    cli.add_command(visualize)
    cli.add_command(overlay)
    cli()


if __name__ == "__main__":
    main()
