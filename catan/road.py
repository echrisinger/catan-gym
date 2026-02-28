from dataclasses import dataclass

from catan.board_point import BoardPoint
from catan.enums import PlayerColor


@dataclass
class Road:
    point1: BoardPoint
    point2: BoardPoint

    color: PlayerColor = None

    def build(self, color: PlayerColor):
        if self.color is not None:
            raise RuntimeError('Road is already occupied')

        self.color = color

    def __hash__(self):
        return self.point1.__hash__() + self.point2.__hash__() * (BoardPoint.ROW_SIZE * BoardPoint.COL_SIZE)

    def __eq__(self, other):
        return self.point1 == other.point1 and self.point2 == other.point2
