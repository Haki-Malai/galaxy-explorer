#!/usr/bin/env python3

import requests
import sys


class StarWarsAPI:
    BASE_URL = "https://www.swapi.tech/api/"

    def generate_character_data(self, name):
        """Generates data for a character in the Star Wars API by name"""
        url = f"{self.BASE_URL}people/?name={name}"
        response = requests.get(url)

        if response.status_code != 200:
            print("Error: Could not reach API.")
            return

        json_data = response.json()
        results = json_data["result"]
        if not results:
            print("The force is not strong within you.")
            return

        for character in results:
            properties = character["properties"]
            yield (
                f"Name: {properties['name']}\n"
                f"Height: {properties['height']}\n"
                f"Mass: {properties['mass']}\n"
                f"Birth year: {properties['birth_year']}"
            )

    def print_character_data(self, name):
        """Prints data for a character in the Star Wars API by name"""
        for data in self.generate_character_data(name):
            print('\n' + data)


if __name__ == "__main__":
    api = StarWarsAPI()
    if len(sys.argv) == 3 and sys.argv[1] == "search":
        name = sys.argv[2]
        api.print_character_data(name)
    else:
        print("Usage: ./main.py search [character name]")
