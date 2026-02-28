from typing import NamedTuple


class Position(NamedTuple):
    row: int
    col: int

    @staticmethod
    def pair(p1: "Position", p2: "Position") -> tuple["Position", "Position"]:
        return (min(p1, p2), max(p1, p2))
