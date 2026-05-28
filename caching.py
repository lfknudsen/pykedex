import json
import os
from pathlib import Path
from classes import JSON

CACHE_DIR: str = "cache"
CACHE_SUBDIR_POKEMON: str = "pokémon"
CACHE_SUBDIR_EVO: str = "evo"
CACHE_SUBDIR_ITEMS: str = "items"
CACHE_SUBDIR_MOVES: str = "moves"
CACHE_SUBDIR_LOCATIONS: str = "locations"
CACHE_SUBDIR_TYPES: str = "types"
CACHE_FILE_EXT: str = ".json"
CACHE_PATH_STR: str = os.path.join(os.path.dirname(__file__), CACHE_DIR)
CACHE_PATH: Path = Path(CACHE_PATH_STR)

def output_file(category: str, name: str) -> Path:
    return Path(os.path.join(CACHE_PATH_STR, category, name + CACHE_FILE_EXT))

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


def cache_type(new_entry: JSON):
    output = output_file(CACHE_SUBDIR_TYPES, new_entry.get("name", "unknown"))
    dump_json(output, new_entry)