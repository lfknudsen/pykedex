import httpx
from httpx import Response
from caching import CACHE_SUBDIR_EVO, CACHE_SUBDIR_ITEMS, CACHE_SUBDIR_LOCATIONS, \
    CACHE_SUBDIR_MOVES, \
    CACHE_SUBDIR_SPECIES, \
    CACHE_SUBDIR_TYPES, cache_evo, cache_item, \
    cache_location, cache_move, cache_species, \
    cache_type, check_cache
from classes import JSON


def request(url: str, verbose: bool) -> JSON:
    if verbose:
        print(f"MAKING HTTP REQUEST TO {url}")
    response: Response = httpx.get(url)
    if response.is_error:
        print("Error: Status code", response.status_code)
        exit(1)
    try:
        return response.json()
    except Exception as e:
        print("Could not parse JSON: ", str(e))
        exit(1)

def retrieve_item(name: str, verbose: bool) -> JSON:
    contents: JSON | None = check_cache(CACHE_SUBDIR_ITEMS, name)
    if contents is None:
        contents: JSON = request(f"https://pokeapi.co/api/v2/item/{name}/", verbose)
        cache_item(contents)
    return contents


def retrieve_move(name: str, verbose: bool) -> JSON:
    contents: JSON | None = check_cache(CACHE_SUBDIR_MOVES, name)
    if contents is None:
        contents: JSON = request(f"https://pokeapi.co/api/v2/move/{name}/", verbose)
        cache_move(contents)
    return contents


def retrieve_type(name: str, verbose: bool) -> JSON:
    contents: JSON | None = check_cache(CACHE_SUBDIR_TYPES, name)
    if contents is None:
        contents: JSON = request(f"https://pokeapi.co/api/v2/type/{name}/", verbose)
        cache_type(contents)
    return contents


def retrieve_species(name: str, verbose: bool) -> JSON:
    contents: JSON | None = check_cache(CACHE_SUBDIR_SPECIES, name)
    if contents is None:
        contents: JSON = request(f"https://pokeapi.co/api/v2/pokemon-species/{name}/", verbose)
        cache_species(contents)
    return contents


def retrieve_location(name: str, verbose: bool) -> JSON:
    contents: JSON | None = check_cache(CACHE_SUBDIR_LOCATIONS, name)
    if contents is None:
        contents: JSON = request(f"https://pokeapi.co/api/v2/location/{name}/", verbose)
        cache_location(contents)
    return contents


def retrieve_evo(url: str, verbose: bool) -> JSON:
    chain_id = str(url.strip("/ ").rsplit("/", 1)[1])
    contents: JSON | None = check_cache(CACHE_SUBDIR_EVO, chain_id)
    if contents is None:
        contents: JSON = request(url, verbose)
        cache_evo(contents)
    return contents