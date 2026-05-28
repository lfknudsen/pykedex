import sys
from typing import Any

from net import retrieve_evo, retrieve_item, retrieve_location, retrieve_move, retrieve_pkmn, \
    retrieve_type
from classes import Evolution, JSON, Text


def get_egg_groups(entry: JSON) -> list[str]:
    egg_groups: list[dict[str, str]] = entry.get("egg_groups")
    return [group.get("name") for group in egg_groups]


def get_formatted_name(content: JSON) -> str:
    names: list[JSON] = content.get("names")
    for locale in names:
        if locale.get("language").get("name") == "en":
            return locale.get("name")
    return content.get("name", "Unknown").title()


def get_formatted_pkmn_name(name: str, verbose: bool) -> str:
    contents = retrieve_pkmn(name, verbose)
    return get_formatted_name(contents)


def get_formatted_item_name(name: str, verbose: bool) -> str:
    contents = retrieve_item(name, verbose)
    return get_formatted_name(contents)


def get_formatted_move_name(name: str, verbose: bool) -> str:
    contents = retrieve_move(name, verbose)
    return get_formatted_name(contents)


def get_formatted_type_name(name: str, verbose: bool) -> str:
    contents = retrieve_type(name, verbose)
    return get_formatted_name(contents)


def get_formatted_location_name(name: str, verbose: bool) -> str:
    contents = retrieve_location(name, verbose)
    return get_formatted_name(contents)


def parse_individual_evo_chain(before: list[Evolution],
                               evolves_to: dict[str, Any],
                               verbose: bool) -> list[list[Evolution]]:
    name: str = get_formatted_pkmn_name(evolves_to.get("species").get("name"),
                                        verbose)
    chains: list[list[Evolution]] = []
    for details in evolves_to.get("evolution_details"):
        lvl: int = details.get("min_level", -1)
        item: str | None = None
        if details.get("item") is not None:
            item = get_formatted_item_name(details.get("item").get("name"),
                                           verbose)

        known_move: str | None = None
        if details.get("known_move") is not None:
            known_move = get_formatted_move_name(details.get("known_move").get("name"),
                                                 verbose)

        known_move_type: str | None = None
        if details.get("known_move_type") is not None:
            known_move_type = get_formatted_type_name(details.get("known_move_type").get("name"),
                                                      verbose)

        held_item: str | None = None
        if details.get("held_item") is not None:
            held_item = get_formatted_item_name(details.get("held_item").get("name"),
                                                verbose)

        min_happiness: int | None = None
        if details.get("min_happiness") is not None:
            min_happiness = details.get("min_happiness")

        time_of_day: str | None = None
        if details.get("time_of_day") is not None and details.get("time_of_day") != "":
            time_of_day = details.get("time_of_day")

        location: str | None = None
        if details.get("location") is not None:
            location = get_formatted_location_name(details.get("location").get("name"),
                                                   verbose)

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
                                           known_move_type,
                                           )]
        updated_chains = []
        if len(evolves_to.get("evolves_to")) != 0:
            for next_evo in evolves_to.get("evolves_to"):
                updated_chains.extend(parse_individual_evo_chain(updated_list, next_evo, verbose))
        else:
            updated_chains = [updated_list]
        chains.extend(updated_chains)
    return chains


def get_evolution_chain(pkmn: JSON, verbose: bool = False) -> list[list[Evolution]]:
    chain_entry: dict[str, str] | None = pkmn.get("evolution_chain", None)
    if chain_entry is None:
        return []
    chain_url: str | None = chain_entry.get("url", None)
    if chain_url is None:
        return []
    chain: JSON = retrieve_evo(chain_url, verbose)

    output: list[list[Evolution]] = []
    base_form = get_formatted_pkmn_name(chain.get("chain").get("species").get("name"),
                                        verbose)
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
                                 None,
                                 )
        sublist = [initial_form]
        output.extend(parse_individual_evo_chain(sublist, evolves_to, verbose))
    return output


def build_transition_text(link: Evolution) -> str:
    transition_text: Text = Text()
    transition_text.append("at lv", link.min_level)
    transition_text.append("using", link.item)
    transition_text.append("knowing", link.known_move)
    if link.known_move_type is not None:
        determiner: str = "a"
        if link.known_move_type[0] in "aeiou":
            determiner = "an"
        transition_text.append(f"knowing {determiner}",
                               f"{link.known_move_type}-type move")
    transition_text.append("holding", link.held_item)
    transition_text.append("with happiness", link.min_happiness)
    transition_text.append("during the", link.time_of_day)
    if link.location is not None:
        preposition: str = "in"
        on_words: tuple[str,...] = ("Route", "Mount", "Road", "Path", "Mountain")
        if link.location.startswith(on_words) or link.location.endswith(on_words):
            preposition = "on"
        transition_text.append(preposition, link.location)

    transition_text.append("with affection", link.min_affection)

    if link.trade:
        transition_text.append(None, "on trade")

    return transition_text.finalise()


def generate_evo_strings(chain: list[Evolution]) -> list[str]:
    if len(chain) == 0:
        return []
    output: list[str] = [chain.pop(0).pkmn_name]
    for link in chain:
        output.append(f"--{build_transition_text(link)}-->")
        output.append(link.pkmn_name)
    return output


def print_evo_chain(chain: list[Evolution]):
    print(" ".join(generate_evo_strings(chain)))

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
            for chain in get_evolution_chain(contents, verbose):
                for subchain in chain:
                    if subchain.pkmn_name.casefold() == name.casefold():
                        print_evo_chain(chain)
                        break


if __name__ == "__main__":
    main()
