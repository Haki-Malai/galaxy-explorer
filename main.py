import click
from starwars_api import StarWarsAPI


@click.group()
def main():
    """A command line interface for the Star Wars API."""
    pass


@main.command()
@click.argument('name')
@click.option('-v', '--verbose', is_flag=True, help='Raise errors/warnings.')
def search(name, verbose):
    """Search for a character in the Star Wars API.
    """
    api = StarWarsAPI()
    api.print_character_data(name, verbose)


if __name__ == '__main__':
    main()
