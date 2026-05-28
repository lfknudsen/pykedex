from dataclasses import dataclass
from typing import Any

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
    known_move_type: str | None


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

    def __str__(self):
        return self.text