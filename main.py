import click
from starwars_api import StarWarsAPI


@click.group()
def main() -> None:
    """A command line interface for the Star Wars API.
    """
    pass


@main.command()
@click.argument('name', type=str)
@click.option('-w', '--world', is_flag=True, default=False,
              help='Print the character\'s home world.')
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='Raise errors/warnings.')
def search(name: str, world: bool, verbose: bool) -> None:
    """Search for a character in the Star Wars API.
    """
    api = StarWarsAPI(world, verbose)
    api.print_character_data(name)


@main.command()
@click.option('-c', '--clear', is_flag=True, default=False,
              help='Clear the cache.')
def cache(clear: bool) -> None:
    """Print the cache.
    """
    api = StarWarsAPI()
    if clear:
        api.clear_cache()
    click.echo('removed cache')


@main.command()
@click.argument('num_searches', type=int, default=20)
def fake(num_searches) -> None:
    """Generate fake searches.
    """
    api = StarWarsAPI()
    api.generate_fake_searches(num_searches)


@main.command()
@click.option('-r', '--results', is_flag=True, default=False,
              help='Visualize the results.')
def plot(results: bool) -> None:
    """Plot the application logs.
    """
    api = StarWarsAPI()
    if results:
        api.visualize_results()
    else:
        api.visualize_searches_made()

if __name__ == '__main__':
    main()
