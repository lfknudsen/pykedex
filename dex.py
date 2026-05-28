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
CACHE_FILE_EXT: str = ".json"
CACHE_PATH_STR: str = os.path.join(os.path.dirname(__file__), CACHE_DIR)
CACHE_PATH: Path = Path(CACHE_PATH_STR)

verbose = len(sys.argv) > 1 and sys.argv[1] == "-v"

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


@dataclass
class Text:
    text: str = ""

    def append(self, string: Any | None):
        if string is not None:
            if self.text != "":
                self.text += " "
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


def get_egg_groups(entry: JSON) -> list[str]:
    egg_groups: list[dict[str, str]] = entry.get("egg_groups")
    return [group.get("name") for group in egg_groups]


def retrieve_item(name: str) -> JSON:
    contents: JSON | None = check_cache(CACHE_SUBDIR_ITEMS, name)
    if contents is None:
        response: Response = httpx.get(f"https://pokeapi.co/api/v2/item/{name}/")
        if response.is_error:
            print(response.status_code)
            exit(1)
        else:
            contents: JSON = response.json()
            cache_item(contents)
    return contents


def retrieve_move(name: str) -> JSON:
    contents: JSON | None = check_cache(CACHE_SUBDIR_MOVES, name)
    if contents is None:
        response: Response = httpx.get(f"https://pokeapi.co/api/v2/move/{name}/")
        if response.is_error:
            print(response.status_code)
            exit(1)
        else:
            contents: JSON = response.json()
            cache_move(contents)
    return contents


def retrieve_pkmn(name: str) -> JSON:
    contents: JSON | None = check_cache(CACHE_SUBDIR_POKEMON, name)
    if contents is None:
        response: Response = httpx.get(f"https://pokeapi.co/api/v2/pokemon-species/{name}/")
        if response.is_error:
            print(response.status_code)
            exit(1)
        else:
            contents: JSON = response.json()
            cache_species(contents)
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
        sublist = [Evolution(base_form, None, None, None, None, False, None)]
        output.extend(parse_individual_evo_chain(sublist, evolves_to))
    return output


def print_evo_chain(chain: list[Evolution]):
    if len(chain) == 0:
        return
    print(chain.pop(0).pkmn_name, end="")
    for link in chain:
        transition_text: Text = Text()
        transition_text.append(link.min_level)
        transition_text.append(link.item)
        transition_text.append(link.known_move)
        transition_text.append(link.held_item)
        if link.min_happiness is not None:
            transition_text.append(f"with happiness {link.min_happiness}")
        if link.trade:
            transition_text.append("on trade")
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
