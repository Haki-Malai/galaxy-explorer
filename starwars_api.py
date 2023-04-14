from typing import Generator
import requests


class StarWarsAPI:
    """A class for interacting with the Star Wars API.
    :method: `generate_character_data` returns a generator that yields
        data for a character in the Star Wars API.
    :method: `print_character_data` prints data for a character in the
        Star Wars API.
    """
    BASE_URL: str = 'https://www.swapi.tech/api'

    API_ERROR_MSG: str = 'Error: Could not reach API. Status code: {}'
    NOT_FOUND_MSG: str = '\nThe force is not strong within you'

    CHARACTER_KEYS: dict = {"name": "Name", "height": "Height",
                            "mass": "Mass", "birth_year": "Birth Year"}

    def _make_request(self, url: str) -> dict:
        """Makes a GET request to the Star Wars API
        :param url: The url to make the request to
        :return: The json data from the response
        """
        response = requests.get(self.BASE_URL + url)

        if response.status_code != 200:
            error_msg = self.API_ERROR_MSG.format(response.status_code)
            raise requests.exceptions.RequestException(error_msg)

        json_data = response.json()
        results = json_data['result']
        if not results:
            raise ValueError(self.NOT_FOUND_MSG)

        return results

    def generate_character_data(self, name: str, verbose: bool = False
                                ) -> Generator[str, None, None]:
        """Generates data for a character in the Star Wars API by name
        :param name: The name of the character to search
        :param verbose: Whether to raise errors or not
        :return: A generator that yields data for a character in the
            Star Wars API.
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
            yield "\n".join(character_data)

    def print_character_data(self, name, verbose=False) -> None:
        """Prints data for a character in the Star Wars API by name
        :param name: The name of the character to search
        :param verbose: Whether to raise errors or not
        """
        for data in self.generate_character_data(name, verbose):
            print('\n' + data)
