import pytest
from requests.exceptions import RequestException

from starwars_api import StarWarsAPI


def test_make_request():
    api = StarWarsAPI()
    response = api._make_request('/people/1')
    assert isinstance(response, dict)
    assert 'properties' in response
    assert response['properties']['name'] == 'Luke Skywalker'


def test_make_request_with_error():
    api = StarWarsAPI()
    with pytest.raises(RequestException):
        api._make_request('/nonexistent')
    with pytest.raises(RequestException):
        api._make_request('/people/nonexistent')


def test_generate_character_data():
    api = StarWarsAPI()
    character_data = api.generate_character_data('Luke Skywalker')
    assert isinstance(character_data, type(api.generate_character_data('')))
    assert next(character_data).startswith('Name: Luke Skywalker\n')


def test_get_homeworld():
    api = StarWarsAPI()
    homeworld = api._get_homeworld('/planets/1')
    assert isinstance(homeworld, str)
    assert 'Tatooine' in homeworld
    assert 'Population: 200000' in homeworld


def test_get_homeworld_with_unknown():
    api = StarWarsAPI()
    homeworld = api._get_homeworld('/planets/28')
    assert homeworld is None


def test_get_homeworld_with_error():
    api = StarWarsAPI()
    with pytest.raises(RequestException):
        api._get_homeworld('/planets/nonexistent')


def test_get_comparison_with_earth():
    api = StarWarsAPI()
    comparison = api._get_comparison_with_earth(365.25, 24)
    assert isinstance(comparison, dict)
    assert comparison['year'] == 1.0
    assert comparison['day'] == 1.0
