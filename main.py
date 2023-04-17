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
    :param name: The name of the character to search for.
    :param world: Print the character's home world.
    :param verbose: Raise errors/warnings.
    """
    api = StarWarsAPI(world, verbose)
    api.print_character_data(name)


@main.command()
@click.option('-c', '--clean', is_flag=True, default=False,
              help='Clear the cache.')
def cache(clean: bool) -> None:
    """Print the cache.
    :param clean: Clear the cache.
    """
    api = StarWarsAPI()
    if clean:
        api.clear_cache()
    click.echo('removed cache')


@main.command()
@click.argument('num_searches', type=int, default=20)
def fake(num_searches) -> None:
    """Generate fake searches.
    :param num_searches: The number of fake searches to generate.
    """
    api = StarWarsAPI()
    api.generate_fake_searches(num_searches)


@main.command()
@click.option('-r', '--results', is_flag=True, default=False,
              help='Visualize the results.')
@click.option('-t', '--time', is_flag=True, default=False,
              help='Visualize the time.')
def plot(results: bool, time: bool) -> None:
    """Plot the application logs.
    :param results: Plot the results.
    :param time: Plot the time.
    """
    api = StarWarsAPI()
    if results:
        api.visualize_results()
    elif time:
        api.visualize_searches_by_time()
    else:
        api.visualize_searches_made()


@main.command()
@click.option('-c', '--coverage', is_flag=True, default=False,
              help='Run the coverage report.')
def test(coverage: bool) -> None:
    """Run the tests.
    :param coverage: Run the coverage report.
    """
    import pytest
    if coverage:
        pytest.main(['--cov-report', 'term-missing', '--cov=starwars_api'])
    else:
        pytest.main()


if __name__ == '__main__':
    main()
