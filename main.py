import click
from starwars_api import StarWarsAPI
from typing import Optional


@click.group()
def main() -> None:
    """A command line interface for the Star Wars API."""
    pass


@main.command()
@click.argument('name', type=str)
@click.option('-v', '--verbose', is_flag=True, help='Raise errors/warnings.')
def search(name: str, verbose: Optional[bool] = False) -> None:
    """Search for a character in the Star Wars API.
    """
    api = StarWarsAPI()
    api.print_character_data(name, verbose)


if __name__ == '__main__':
    main()
