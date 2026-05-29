from dataclasses import dataclass
from enum import Enum, StrEnum

from classes import JSON
from net import retrieve_pkmn


class VersionGroup(StrEnum):
    RB = "red-blue"
    Y = "yellow"
    GS = "gold-silver"
    C = "crystal"
    RS = "ruby-sapphire"
    E = "emerald"
    FRLG = "firered-leafgreen"
    DP = "diamond-pearl"
    PL = "platinum"
    HGSS = "heartgold-soulsilver"
    COL = "colosseum"
    XD = "xd"
    BW = "black-white"
    BW2 = "black-2-white-2"
    XY = "x-y"
    ORAS = "omega-ruby-alpha-sapphire"
    SM = "sun-moon"
    USUM = "ultra-sun-ultra-moon"
    LG = "lets-go-pikachu-lets-go-eevee"
    SWSH = "sword-shield"
    SWSH_TIOA = "the-isle-of-armor"
    SWSH_TCT = "the-crown-tundra"
    BDSP = "brilliant-diamond-shining-pearl"
    LA = "legends-arceus"
    SV = "scarlet-violet"
    SV_TTM = "the-teal-mask"
    SV_TID = "the-indigo-disk"
    RG_JP = "red-green-japan"
    B_JP  = "blue-japan"
    LZA = "legends-za"
    LZA_MD = "mega-dimension"
    CHAMP = "champions"

class MoveLearnMethods(Enum):
    LEVEL_UP = 1
    EGG = 2
    TUTOR = 3
    MACHINE = 4
    STADIUM_SURFING_PIKACHU = 5
    LIGHT_BALL_EGG = 6
    COLOSSEUM_PURIFICATION = 7
    XD_SHADOW = 8
    XD_PURIFICATION = 9
    FORM_CHANGE = 10
    ZYGARDE_CUBE = 11


TEXT_PREFIX_COLOUR: str = "\033[2m"


def fade(text: str) -> str:
    return f"{TEXT_PREFIX_COLOUR}{text}\033[0m"


@dataclass
class Move:
    name: str
    method: str
    level_learned_at: int | None

    def __str__(self):
        if self.method == "level-up":
            return f"{str(self.level_learned_at).rjust(5)} {self.name}"
        elif self.method == "egg":
            return f"{fade("  egg")} {self.name}"
        elif self.method == "machine":
            return f"{fade("TM/HM")} {self.name}"
        elif self.method == "tutor":
            return f"{fade("tutor")} {self.name}"
        else:
            return f"{fade("-----")} {self.name}"


def move_key(move: Move) -> str:
    if move.method == "level-up":
        return f"{str(move.level_learned_at).rjust(5, "0")}:{move.name.casefold()}"
    else:
        return f"{move.method.casefold()}:{str(move.level_learned_at).rjust(5,"0")}:{move.name.casefold()}"

def print_moveset(name: str, game: VersionGroup, verbose: bool):
    content: JSON = retrieve_pkmn(name, verbose)
    print("Version group is", game.value)
    moves: list[JSON] = content.get("moves")
    if len(moves) == 0:
        return
    keep: list[Move] = []
    for move in moves:
        details: list[JSON] = move.get("version_group_details")
        for detail in details:
            if detail.get("version_group").get("name") == game.value:
                move_dto = Move(move.get("move").get("name").title(),
                                detail.get("move_learn_method").get("name"),
                                detail.get("level_learned_at"),
                                )
                keep.append(move_dto)

    keep.sort(key=move_key)
    for m in keep:
        print(m)