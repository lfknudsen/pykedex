from classes import JSON
from net import retrieve_item, retrieve_location, retrieve_move, retrieve_species, retrieve_type


def get_column_widths(chains: list[list[str]]) -> list[int]:
    if len(chains) == 0:
        return []
    # We get the number of elements that each sublist might contain
    # to help avoid out-of-range exceptions
    column_count: int = 0
    for chain in chains:
        column_count = max(column_count, len(chain))

    # Initialise a list of the maximum character widths per column
    max_widths: list[int] = [len(word) for word in chains[0]]

    # Continuation of out-of-range avoidance, just to make it simpler inside the
    # for loop later
    while len(max_widths) < column_count:
        max_widths.append(0)

    for row in chains[1:]:
        for i in range(0, len(row)):
            max_widths[i] = max(max_widths[i], len(row[i]))
    return max_widths


def get_formatted_name(content: JSON) -> str:
    names: list[JSON] = content.get("names")
    for locale in names:
        if locale.get("language").get("name") == "en":
            return locale.get("name")
    return content.get("name", "Unknown").title()

def get_formatted_pkmn_name(name: str, verbose: bool) -> str:
    contents = retrieve_species(name, verbose)
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