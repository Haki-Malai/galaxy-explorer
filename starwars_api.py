from typing import Generator, Optional
from datetime import datetime
from cachetools import cached, TTLCache
from joblib import Memory
import requests


class StarWarsAPI:
    """A class for interacting with the Star Wars API.
    """
    BASE_URL: str = 'https://www.swapi.tech/api'

    API_ERROR_MSG: str = 'Error: Could not reach API. Status code: {}'
    NOT_FOUND_MSG: str = '\nThe force is not strong within you'
    HOMEWORLD_MSG: str = '\nHomeworld\n' + '-' * 10
    COMPARISON_MSG: str = '\n\nOn {}, 1 year on earth is {} years and 1 day {} days'
    NO_COMPARISON_MSG: str = '\n\nCould not compare {} with Earth'

    CHARACTER_KEYS: dict = {'name': 'Name', 'height': 'Height',
                            'mass': 'Mass', 'birth_year': 'Birth Year'}
    HOMEWORLD_KEYS: dict = {'name': 'Name', 'population': 'Population'}

    EARTH_YEAR: float = 365.25
    EARTH_DAY: float = 24

    TIME_FORMAT: str = '%Y-%m-%d %H:%M:%S.%f'

    cache = TTLCache(maxsize=100, ttl=600)
    memory = Memory(location='.', verbose=0)

    def clear_cache(self) -> None:
        """Clears the cache.
        """
        self.cache.clear()
        self.memory.clear(warn=False)

    @cached(cache)
    @memory.cache
    def _make_request(self, url: str) -> dict:
        """Makes a GET request to the Star Wars API.
        :param url: The url to make the request to.
        :return: The json data from the response.
        :raises requests.exceptions.RequestException: If there is a connection error.
        :raises ValueError: If the results are empty.
        """
        if url.startswith('/'):
            url = self.BASE_URL + url
        response = requests.get(url)

        if response.status_code != 200:
            error_msg = self.API_ERROR_MSG.format(response.status_code)
            raise requests.exceptions.RequestException(error_msg)

        json_data = response.json()
        results = json_data.get('result', [])
        if not results:
            raise ValueError(self.NOT_FOUND_MSG)

        cached_time = datetime.now()
        for result in results:
            if isinstance(result, dict):
                result['cached'] = cached_time.strftime(self.TIME_FORMAT)

        return results

    def _get_homeworld(self, url: str) -> Optional[dict]:
        """Gets the name of a character's home world.
        :param url: The url to make the request to.
        :return: The name of the character's home world, or None if unknown.
        """
        results = self._make_request(url)
        properties = results['properties']

        if properties.get('name') == 'unknown':
            return None

        homeworld_str = self.HOMEWORLD_MSG
        for key, title in self.HOMEWORLD_KEYS.items():
            homeworld_str = homeworld_str + f'\n{title}: {properties[key]}'

        try:
            planet_year = float(properties['orbital_period'])
            planet_day = float(properties['rotation_period'])
            comparison = self._get_comparison_with_earth(planet_year, planet_day)
        except (ValueError, TypeError):
            return homeworld_str + self.NO_COMPARISON_MSG.format(properties['name'])
        homeworld_str = homeworld_str + self.COMPARISON_MSG.format(
            properties['name'], comparison['year'], comparison['day'])

        return homeworld_str

    def _get_comparison_with_earth(self, planet_year: float, planet_day: float
                                    )-> dict:
        """Gets the comparison between earth and a Star Wars planet.
        :return: The comparison between earth and Tatooine.
        """
        year_ratio = planet_year / self.EARTH_YEAR
        day_ratio = planet_day / self.EARTH_DAY

        return {'year': round(year_ratio, 2), 'day': round(day_ratio, 2)}

    def generate_character_data(self, name: str, include_homeworld: bool = False,
                                verbose: bool = False) -> Generator[str, None, None]:
        """Generates data for a character in the Star Wars API by name.
        :param name: The name of the character to search.
        :param include_homeworld: Whether to include homeworld data or not.
        :param verbose: Whether to raise errors or not.
        :return: A generator that yields data for a character in the Star Wars API.
        """
        url = f'/people/?name={name}'
        try:
            results = self._make_request(url)
        except (requests.exceptions.RequestException, ValueError) as e:
            if verbose:
                raise e
            print(str(e))
            return

        for character in results:
            properties = character['properties']
            character_data = []
            for key, title in self.CHARACTER_KEYS.items():
                if key in properties:
                    character_data.append(f'{title}: {properties[key]}')

            if include_homeworld and 'homeworld' in properties:
                homeworld_str = self._get_homeworld(properties['homeworld'])
                if homeworld_str:
                    character_data.append(homeworld_str)

            character_data.append(f'\n\ncached: {character["cached"]}')

            yield '\n'.join(character_data)

    def print_character_data(self, name: str, world: Optional[bool],
                             verbose=False) -> None:
        """Prints data for a character in the Star Wars API by name.
        :param name: The name of the character to search.
        :param verbose: Whether to raise errors or not.
        """
        for data in self.generate_character_data(name, world, verbose):
            print('\n' + data)
