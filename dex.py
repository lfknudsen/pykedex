import json
import os
import sys
from typing import Any
from pathlib import Path
import httpx
from httpx import Response
from dataclasses import dataclass

CACHE_DIR: str = "cache"
CACHE_SUBDIR_POKEMON: str = "pokémon"
CACHE_SUBDIR_EVO: str = "evo"
CACHE_SUBDIR_ITEMS: str = "items"
CACHE_SUBDIR_MOVES: str = "moves"
CACHE_SUBDIR_LOCATIONS: str = "locations"
CACHE_FILE_EXT: str = ".json"
CACHE_PATH_STR: str = os.path.join(os.path.dirname(__file__), CACHE_DIR)
CACHE_PATH: Path = Path(CACHE_PATH_STR)

verbose = __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "-v"


def output_file(category: str, name: str) -> Path:
    return Path(os.path.join(CACHE_PATH_STR, category, name + CACHE_FILE_EXT))


type JSON = dict[str, Any]


@dataclass
class Evolution:
    pkmn_name: str
    min_level: int | None
    item: str | None
    known_move: str | None
    held_item: str | None
    trade: bool
    min_happiness: int | None
    time_of_day: str | None
    location: str | None
    min_affection: int | None


@dataclass
class Text:
    text: str = ""

    def append(self, prefix: str | None, string: Any | None):
        if string is not None:
            if self.text != "":
                self.text += " "
            if prefix is not None:
                self.text += f"{prefix} "
            self.text += str(string)

    def finalise(self) -> str:
        if self.text != "":
            self.text = f"({self.text})"
        return self.text


def check_cache(category: str, filename: str) -> JSON | None:
    try:
        with open(output_file(category, filename)) as f:
            contents: str = f.read()
            return json.loads(contents)
    except:
        return None


def dump_json(filename: Path, json_contents: JSON):
    filename.parent.mkdir(exist_ok=True, parents=True)
    with open(filename, mode="w") as f:
        json.dump(json_contents, f)


def cache_species(new_entry: JSON):
    output = output_file(CACHE_SUBDIR_POKEMON, new_entry.get("name", "unknown"))
    dump_json(output, new_entry)


def cache_evo(new_entry: JSON):
    output = output_file(CACHE_SUBDIR_EVO, str(new_entry.get("id", "unknown")))
    dump_json(output, new_entry)


def cache_item(new_entry: JSON):
    output = output_file(CACHE_SUBDIR_ITEMS, new_entry.get("name", "unknown"))
    dump_json(output, new_entry)


def cache_move(new_entry: JSON):
    output = output_file(CACHE_SUBDIR_MOVES, new_entry.get("name", "unknown"))
    dump_json(output, new_entry)


def cache_location(new_entry: JSON):
    output = output_file(CACHE_SUBDIR_LOCATIONS, new_entry.get("name", "unknown"))
    dump_json(output, new_entry)


def request(url: str) -> JSON:
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


def get_egg_groups(entry: JSON) -> list[str]:
    egg_groups: list[dict[str, str]] = entry.get("egg_groups")
    return [group.get("name") for group in egg_groups]


def retrieve_item(name: str) -> JSON:
    contents: JSON | None = check_cache(CACHE_SUBDIR_ITEMS, name)
    if contents is None:
        contents: JSON = request(f"https://pokeapi.co/api/v2/item/{name}/")
        cache_item(contents)
    return contents


def retrieve_move(name: str) -> JSON:
    contents: JSON | None = check_cache(CACHE_SUBDIR_MOVES, name)
    if contents is None:
        contents: JSON = request(f"https://pokeapi.co/api/v2/move/{name}/")
        cache_move(contents)
    return contents


def retrieve_pkmn(name: str) -> JSON:
    contents: JSON | None = check_cache(CACHE_SUBDIR_POKEMON, name)
    if contents is None:
        contents: JSON = request(f"https://pokeapi.co/api/v2/pokemon-species/{name}/")
        cache_species(contents)
    return contents


def retrieve_location(name: str) -> JSON:
    contents: JSON | None = check_cache(CACHE_SUBDIR_LOCATIONS, name)
    if contents is None:
        contents: JSON = request(f"https://pokeapi.co/api/v2/location/{name}/")
        cache_location(contents)
    return contents


def get_formatted_name(content: JSON) -> str:
    names: list[JSON] = content.get("names")
    for locale in names:
        if locale.get("language").get("name") == "en":
            return locale.get("name")
    return content.get("name", "Unknown").title()


def get_formatted_pkmn_name(name: str) -> str:
    contents = retrieve_pkmn(name)
    return get_formatted_name(contents)


def get_formatted_item_name(name: str) -> str:
    contents = retrieve_item(name)
    return get_formatted_name(contents)


def get_formatted_move_name(name: str) -> str:
    contents = retrieve_move(name)
    return get_formatted_name(contents)


def get_formatted_location_name(name: str) -> str:
    contents = retrieve_location(name)
    return get_formatted_name(contents)


def parse_individual_evo_chain(before: list[Evolution],
                               evolves_to: dict[str, Any]) -> list[list[Evolution]]:
    name: str = get_formatted_pkmn_name(evolves_to.get("species").get("name"))
    chains: list[list[Evolution]] = []
    for details in evolves_to.get("evolution_details"):
        lvl: int = details.get("min_level", -1)
        item: str | None = None
        if details.get("item") is not None:
            item = get_formatted_item_name(details.get("item").get("name"))

        known_move: str | None = None
        if details.get("known_move") is not None:
            known_move = get_formatted_move_name(details.get("known_move").get("name"))

        held_item: str | None = None
        if details.get("held_item") is not None:
            held_item = get_formatted_item_name(details.get("held_item").get("name"))

        min_happiness: int | None = None
        if details.get("min_happiness") is not None:
            min_happiness = details.get("min_happiness")

        time_of_day: str | None = None
        if details.get("time_of_day") is not None and details.get("time_of_day") != "":
            time_of_day = details.get("time_of_day")

        location: str | None = None
        if details.get("location") is not None:
            location = get_formatted_location_name(details.get("location").get("name"))

        min_affection: int | None = None
        if details.get("min_affection") is not None:
            min_affection = details.get("min_affection")

        trade: bool = False
        if details.get("trigger") is not None:
            trade = details.get("trigger").get("name") == "trade"

        updated_list = before + [Evolution(name,
                                           lvl,
                                           item,
                                           known_move,
                                           held_item,
                                           trade,
                                           min_happiness,
                                           time_of_day,
                                           location,
                                           min_affection,
                                           )]
        updated_chains = []
        if len(evolves_to.get("evolves_to")) != 0:
            for next_evo in evolves_to.get("evolves_to"):
                updated_chains.extend(parse_individual_evo_chain(updated_list, next_evo))
        else:
            updated_chains = [updated_list]
        chains.extend(updated_chains)
    return chains


def get_evolution_chain(entry: JSON) -> list[list[Evolution]]:
    chain_entry: dict[str, str] | None = entry.get("evolution_chain", None)
    if chain_entry is None:
        return []
    chain_url: str | None = chain_entry.get("url", None)
    if chain_url is None:
        return []
    chain_id = str(chain_url.rsplit("/", 1)[0])
    chain: JSON | None = check_cache(CACHE_SUBDIR_EVO, chain_id)
    if chain is None:
        response: Response = httpx.get(chain_url)
        if response.is_error:
            print(response.status_code)
            exit(1)
        else:
            chain: JSON = response.json()
            cache_evo(chain)

    output: list[list[Evolution]] = []
    base_form = get_formatted_pkmn_name(chain.get("chain").get("species").get("name"))
    for evolves_to in chain.get("chain").get("evolves_to"):
        initial_form = Evolution(base_form,
                                 None,
                                 None,
                                 None,
                                 None,
                                 False,
                                 None,
                                 None,
                                 None,
                                 None,
                                 )
        sublist = [initial_form]
        output.extend(parse_individual_evo_chain(sublist, evolves_to))
    return output


def print_evo_chain(chain: list[Evolution]):
    if len(chain) == 0:
        return
    print(chain.pop(0).pkmn_name, end="")
    for link in chain:
        transition_text: Text = Text()
        transition_text.append("at lv", link.min_level)
        transition_text.append("using", link.item)
        transition_text.append("knowing", link.known_move)
        transition_text.append("holding", link.held_item)
        transition_text.append("with happiness", link.min_happiness)
        transition_text.append("during the", link.time_of_day)
        if link.location is not None:
            preposition = "in"
            if link.location.startswith(("Route", "Mount")) or link.location.endswith("Mountain"):
                preposition = "on"
            transition_text.append(preposition, link.location)

        transition_text.append("with affection", link.min_affection)

        if link.trade:
            transition_text.append(None, "on trade")
        print(" --" + transition_text.finalise() + "--> " + link.pkmn_name, end="")
    print()


def main():
    if verbose:
        sys.argv.pop(1)
    name = sys.argv.pop(1)
    contents: JSON = retrieve_pkmn(name)

    command: str = "id"
    if len(sys.argv) > 1:
        command = sys.argv.pop(1).lower().strip()
    match command:
        case "id" | "no" | "nr" | "num":
            dex_num_entries: list[JSON] = contents.get("pokedex_numbers")
            for entry in dex_num_entries:
                if entry.get("pokedex").get("name") == "national":
                    print(entry.get("entry_number"))
                    exit(0)
            print("Not found")
            exit(1)
        case "egg" | "eggs" | "egg group" | "egg groups" | "egg-group" | "egg-groups" | "group":
            [print(group) for group in get_egg_groups(contents)]
        case "evo":
            [print_evo_chain(chain) for chain in get_evolution_chain(contents)]


if __name__ == "__main__":
    main()
