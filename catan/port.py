from dataclasses import dataclass

from catan.board_point import BoardPoint
from catan.enums import PortType, PlayerColor


@dataclass
class Port:
    point1: BoardPoint
    point2: BoardPoint

    resource: PortType

    def is_settled(self) -> bool:
        return self.point1.color is not None or self.point2.color is not None

    def color(self) -> PlayerColor | None:
        return self.point1.color or self.point2.color
