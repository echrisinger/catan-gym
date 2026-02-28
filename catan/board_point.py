from dataclasses import dataclass

from catan import PlayerColor
from catan.enums import BuildingType


@dataclass
class BoardPoint:
    """
    positionally from the left or top of the board, assuming it is a square drawn around the edges of the board
    there are 11 discrete spots a board point can be positioned vertically or horizontally
    -----------
       . . .
      . . . .
      . . . .
     . . . . .
     . . . . .
    . . . . . .
    . . . . . .
     . . . . .
     . . . . .
      . . . .
      . . . .
       . . .
    """

    row: int
    col: int

    color: PlayerColor = None
    building: BuildingType = None

    def __hash__(self):
        return hash(self.row * 11 + self.col)

    def is_neighbor(self, other: "BoardPoint") -> bool:
        return max(
            abs(self.row - other.row),
            abs(self.col - other.col)
        ) <= 1

    def settle(self, color: PlayerColor):
        if self.color is not None:
            raise RuntimeError('Board point is already occupied')

        self.color = color

    def is_ascending(self) -> bool:
        return self.row % 2 == 1

    def is_descending(self) -> bool:
        return self.row % 2 == 0

    def is_right_edge(self) -> bool:

        return self.col >= 10 - int(abs(self.row - 5.5) // 2)

    def is_bottom_edge(self) -> bool:
        """
        col {0, 10} -> max depth of 6
        {1, 9} -> 8
        [2,8] -> 10, 11
        :return:
        """
        return self.row >= 10 - 2 * (3 - max(3, abs(self.col - 5)))