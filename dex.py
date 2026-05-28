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
CACHE_FILE_EXT: str = ".json"
CACHE_PATH_STR: str = os.path.join(os.path.dirname(__file__), CACHE_DIR)
CACHE_PATH: Path = Path(CACHE_PATH_STR)


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


def get_egg_groups(entry: JSON) -> list[str]:
    egg_groups: list[dict[str, str]] = entry.get("egg_groups")
    return [group.get("name") for group in egg_groups]


def parse_individual_evo_chain(before: list[Evolution],
                               evolves_to: dict[str,Any]) -> list[Evolution]:
    name: str = evolves_to.get("species").get("name")
    details: dict[str, Any] = evolves_to.get("evolution_details")[0] # Some will have multiple, so this is wrong
    lvl: int = details.get("min_level", -1)
    item: str | None = None
    if details.get("item") is not None:
        item = details.get("item").get("name")
    known_move: str | None = None
    if details.get("known_move") is not None:
        known_move = details.get("known_move").get("name")
    held_item: str | None = None
    if details.get("held_item") is not None:
        held_item = details.get("held_item").get("name")
    before.append(Evolution(name, lvl, item, known_move, held_item))
    if len(evolves_to.get("evolves_to")) != 0:
        parse_individual_evo_chain(before, evolves_to.get("evolves_to")[0])
    return before


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

    output = []
    base_form = chain.get("chain").get("species").get("name")
    for evolves_to in chain.get("chain").get("evolves_to"):
        sublist = [Evolution(base_form, 0, None, None, None)]
        output.append(parse_individual_evo_chain(sublist, evolves_to))
    return output


def print_evo_chain(chain: list[Evolution]):
    if len(chain) == 0:
        return
    print(chain.pop(0).pkmn_name, end="")
    for link in chain:
        transition_text: str = ""
        if link.min_level is not None:
            transition_text = str(link.min_level)
        if link.item is not None:
            transition_text += f"({link.item})"
        if link.known_move is not None:
            transition_text += f"({link.known_move})"
        if link.held_item is not None:
            transition_text += f"({link.held_item})"
        print(" --" + transition_text + "--> " + link.pkmn_name, end="")
    print()


def main():
    name = sys.argv.pop(1)
    contents: JSON | None = check_cache(CACHE_SUBDIR_POKEMON, name)
    if contents is None:
        response: Response = httpx.get(f"https://pokeapi.co/api/v2/pokemon-species/{name}/")
        if response.is_error:
            print(response.status_code)
            exit(1)
        else:
            contents: JSON = response.json()
            cache_species(contents)

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
