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

    def is_neighbor(self, other: "BoardPoint") -> bool:
        return max(
            abs(self.row - other.row),
            abs(self.col - other.col)
        ) <= 1

    def settle(self, color: PlayerColor):
        if self.color is not None:
            raise RuntimeError('Board point is already occupied')

        self.color = color