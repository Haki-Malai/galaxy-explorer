import re
import requests
import random
import logging
import time
import matplotlib.pyplot as plt
from typing import Generator, Optional
from datetime import datetime
from cachetools import cached, TTLCache
from joblib import Memory


class StarWarsAPI:
    """A class for interacting with the Star Wars API.
    """
    BASE_URL: str = 'https://www.swapi.tech/api'

    API_ERROR_MSG: str = 'Error: Could not reach API. Status code: {}'
    NOT_FOUND_MSG: str = '\nThe force is not strong within you'
    HOMEWORLD_MSG: str = '\n\nHomeworld\n' + '-' * 10
    COMPARISON_MSG: str = '\n\nOn {}, 1 year on earth is ' + \
        '{} years and 1 day {} days'
    NO_COMPARISON_MSG: str = '\n\nCould not compare {} with Earth'

    CHARACTER_KEYS: dict = {'name': 'Name', 'height': 'Height',
                            'mass': 'Mass', 'birth_year': 'Birth Year'}
    HOMEWORLD_KEYS: dict = {'name': 'Name', 'population': 'Population'}

    EARTH_YEAR: float = 365.25
    EARTH_DAY: float = 24

    TIME_FORMAT: str = '%Y-%m-%d %H:%M:%S.%f'

    cache = TTLCache(maxsize=100, ttl=600)
    memory = Memory(location='.', verbose=0)

    def __init__(self, include_homeworld=False, verbose=False) -> None:
        """Initializes the StarWarsAPI class.
        :param world: Whether to print the character's home world.
        :param verbose: Whether to raise errors/warnings.
        """
        self.include_homeworld = include_homeworld
        self.verbose = verbose
        self.logger = self._create_logger()

    def _create_logger(self):
        """Creates a logger object.
        :return: The logger object.
        """
        logger = logging.getLogger('swapi')
        logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler('swapi.log')
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

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
        :raises requests.exceptions.RequestException: If connection error.
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

    def _get_homeworld(self, url: str) -> Optional[str]:
        """Gets the name of a character's home world.
        :param url: The url to make the request to.
        :return: The name of the character's home world, or None if unknown.
        """
        results = self._make_request(url)
        properties = results['properties']

        if properties.get('name') == 'unknown':
            return

        homeworld_str = self.HOMEWORLD_MSG
        for key, title in self.HOMEWORLD_KEYS.items():
            homeworld_str = homeworld_str + f'\n{title}: {properties[key]}'

        try:
            planet_year = float(properties['orbital_period'])
            planet_day = float(properties['rotation_period'])
            comparison = self._get_comparison_with_earth(planet_year, planet_day)
        except (ValueError, TypeError):
            return homeworld_str + \
                self.NO_COMPARISON_MSG.format(properties['name'])
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

    def generate_character_data(self, name: str) -> Generator[str, None, None]:
        """Generates data for a character in the Star Wars API by name.
        :param name: The name of the character to search.
        :return: A generator that yields data for a Star Wars character.
        """
        url = f'/people/?name={name}'
        start_time = time.monotonic()
        try:
            results = self._make_request(url)
            self.logger.info(f'Search made: {url}')
            end_time = time.monotonic()
            elapsed_time = end_time - start_time
            self.logger.info(f'Result: {results}, Time: {elapsed_time:.3f}s')
        except (requests.exceptions.RequestException, ValueError) as e:
            if self.verbose:
                raise e
            print(str(e))
            return

        for character in results:
            properties = character['properties']
            character_data = []
            for key, title in self.CHARACTER_KEYS.items():
                if key in properties:
                    character_data.append(f'{title}: {properties[key]}')

            if self.include_homeworld and 'homeworld' in properties:
                homeworld_str = self._get_homeworld(properties['homeworld'])
                character_data.append(homeworld_str)

            character_data.append(f'\n\ncached: {character["cached"]}')

            yield '\n'.join(character_data)

    def print_character_data(self, name: str) -> None:
        """Prints data for a character in the Star Wars API by name.
        :param name: The name of the character to search.
        """
        for data in self.generate_character_data(name):
            print('\n' + data)

    def generate_fake_searches(self, num_searches: int) -> None:
        fake_list = ['Luke', 'Darth', 'Leia', 'Han', 'Chewbacca',
                     'R2-D2', 'lu', 'dar', 'le', 'ha', 'ch', 'r2']
        for _ in range(num_searches):
            self.print_character_data(random.choice(fake_list))

    def load_logs(self) -> dict[list, list]:
        """Loads the logs from the swapi.log file.
        :return: A dictionary with the searches made, search results,
        and search times.
        """
        with open('swapi.log', 'r') as f:
            log_data = f.read()

        name_pattern = r'name=([^\s]+)'
        result_pattern = r"'name':\s+'(.*?)'"
        time_pattern = r'(?<=Time: )\d+\.\d+(?=s)'

        searches_made = re.findall(name_pattern, log_data)
        search_results = re.findall(result_pattern, log_data)
        search_times = re.findall(time_pattern, log_data)

        return {'searches_made': searches_made,
                'search_results': search_results,
                'search_times': search_times}

    def visualize_searches_made(self) -> None:
        """Vizualize the searches made.
        """
        searches_made = self.load_logs()['searches_made']
        if not searches_made:
            print('No searches to visualize.')
            return

        name_counts = {}
        for name in searches_made:
            if name in name_counts:
                name_counts[name] += 1
            else:
                name_counts[name] = 1

        names = list(name_counts.keys())
        counts = list(name_counts.values())
        plt.figure(figsize=(12, 6))
        plt.bar(names, counts)
        plt.xlabel("Name searched")
        plt.ylabel("Number of searches")
        plt.title("Searches by name")
        plt.xticks(rotation=15, fontsize=8)
        plt.show()

    def visualize_results(self) -> None:
        """Visualizes the results.
        """
        search_results = self.load_logs()['search_results']
        if not search_results:
            print('No results to visualize.')
            return

        result_counts = {}
        for name in search_results:
            if name in result_counts:
                result_counts[name] += 1
            else:
                result_counts[name] = 1

        results = list(result_counts.keys())
        counts = list(result_counts.values())
        plt.figure(figsize=(12, 6))
        plt.bar(results, counts)
        plt.xlabel("Result Name")
        plt.ylabel("Number of results")
        plt.title("Results by count")
        plt.xticks(rotation=15, fontsize=8)
        plt.show()

    def visualize_searches_by_time(self) -> None:
        """Visualizes the searches made by time.
        """
        data = self.load_logs()
        searches_made = data['searches_made']
        search_times = data['search_times']

        search_times = [float(time) for time in search_times]

        name_counts = {}
        for name in searches_made:
            if name in name_counts:
                name_counts[name] += 1
            else:
                name_counts[name] = 1

        names = list(name_counts.keys())

        search_times_by_name = {}
        for i, name in enumerate(names):
            if name in search_times_by_name:
                search_times_by_name[name].append(search_times[i])
            else:
                search_times_by_name[name] = [search_times[i]]

        for name in search_times_by_name:
            search_times_by_name[name] = sum(search_times_by_name[name]) \
                                         / len(search_times_by_name[name])

        search_times_by_name_list = list(search_times_by_name.items())
        sorted_search_times_by_name_list = sorted(
            search_times_by_name_list, key=lambda x: -x[1])

        names = [t[0] for t in sorted_search_times_by_name_list]
        times = [t[1] for t in sorted_search_times_by_name_list]

        plt.bar(names, times)
        plt.xlabel("Name searched")
        plt.ylabel("Average time (s)")
        plt.title("Search times by name")
        plt.show()
