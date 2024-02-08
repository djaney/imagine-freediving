import click
from imagine_freediving.subcommands.visualize import visualize


@click.group()
def cli():
    pass


def main():
    cli.add_command(visualize)
    cli()


if __name__ == "__main__":
    main()
