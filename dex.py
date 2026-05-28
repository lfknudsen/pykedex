import sys

from evo import print_evo_chains
from net import retrieve_pkmn
from classes import JSON


def get_egg_groups(entry: JSON) -> list[str]:
    egg_groups: list[dict[str, str]] = entry.get("egg_groups")
    return [group.get("name") for group in egg_groups]


def main():
    next_arg = 1
    verbose = len(sys.argv) > next_arg and sys.argv[next_arg] == "-v"
    if verbose:
        next_arg += 1
    name = sys.argv.pop(next_arg)
    contents: JSON = retrieve_pkmn(name, verbose)

    command: str = "id"
    if len(sys.argv) > next_arg:
        command = sys.argv.pop(next_arg).lower().strip()
    match command:
        case "id" | "no" | "nr" | "num":
            dex_num_entries: list[JSON] = contents.get("pokedex_numbers")
            for entry in dex_num_entries:
                if entry.get("pokedex").get("name") == "national":
                    print(entry.get("entry_number"))
                    exit(0)
            print("Not found")
            exit(1)
        case "egg" | "eggs" | "egg group" | "egg groups" | "egg-group" | "egg-groups" | "group" | "groups":
            [print(group.title()) for group in get_egg_groups(contents)]
        case "evo":
            print_evo_chains(name, contents, verbose)


if __name__ == "__main__":
    main()
