from typing import List, NamedTuple, Optional
from dataclasses import dataclass

from catan.board_point import BoardPoint
from catan.enums import HexType, PortType, PlayerColor
from catan.hex import Hex, HexPosition, HexFactory
from shuffle import copy_and_shuffle

PORT_AMOUNTS = (
    [PortType.ANY] * 4 +
    [PortType.WOOD] +
    [PortType.BRICK] +
    [PortType.WHEAT] +
    [PortType.ORE] +
    [PortType.SHEEP]
)

class Position(NamedTuple):
    row: int
    col: int

PORT_POSITIONS = [
    (Position(1, 2), Position(0, 3)),
    (Position(0, 5), Position(1, 6)),
    (Position(3, 1), Position(4, 1)),
    (Position(2, 8), Position(3, 9)),
    (Position(5, 10), Position(6, 10)),
    (Position(7, 1), Position(8, 1)),
    (Position(8, 9), Position(9, 8)),
    (Position(10, 2), Position(11, 3)),
    (Position(11, 5), Position(12, 6))
]

HEX_AMOUNTS = (
    [HexType.DESERT] +
    [HexType.WOOD] * 4 +
    [HexType.BRICK] * 3 +
    [HexType.WHEAT] * 4 +
    [HexType.ORE] * 3 +
    [HexType.SHEEP] * 4
)

DICE_TOKEN_SEQUENCE = [
    5, 2, 6, 3, 8,
    10, 9, 12, 11,
    4, 8, 10, 9,
    4, 5, 6, 3, 11
]

class DiceTokenStack:
    def __init__(self):
        self.stack = DICE_TOKEN_SEQUENCE[::-1]

    def get_token(self, hex_type: HexType) -> int:
        dice_roll = None

        if hex_type != HexType.DESERT:
            dice_roll = self.stack.pop()

        return dice_roll

def shuffle_hexes() -> List[HexType]:
    return copy_and_shuffle(HEX_AMOUNTS)

def shuffle_ports() -> List[PortType]:
    return copy_and_shuffle(PORT_AMOUNTS)

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

@dataclass
class Port:
    point1: BoardPoint
    point2: BoardPoint

    resource: PortType

    def is_settled(self) -> bool:
        return self.point1.color is not None or self.point2.color is not None

    def color(self) -> PlayerColor | None:
        return self.point1.color or self.point2.color

class Board:
    def __init__(self, hex_order: List[HexType], port_order: List[PortType]):
        self.hexes = self._build_hexes(hex_order)
        self.board_points = self._build_board_points()
        self.roads = self._build_roads()
        self.ports = self._build_ports(port_order)

    @staticmethod
    def _build_board_points() -> dict[Position, BoardPoint]:
        board_points = {}

        for row in range(0, 12):
            if row in {0, 11}:
                cols = [3, 5, 7]
            elif row in {1, 2, 9, 10}:
                cols = [2, 4, 6, 8]
            elif row in {3, 4, 7, 8}:
                cols = [1, 3, 5, 7, 9]
            else:
                cols = [0, 2, 4, 6, 8, 10]

            for col in cols:
                board_points[Position(row, col)] = BoardPoint(row, col)

        return board_points

    @staticmethod
    def _position_pair(p1: Position, p2: Position) -> tuple[Position, Position]:
        return (min(p1, p2), max(p1, p2))

    def _build_roads(self) -> dict[tuple[Position, Position], Road]:
        """
        builds roads from top/left of the board down & to the right.
        :return:
        """
        roads = {}
        for pos, point in self.board_points.items():
            if point.is_ascending():
                if not point.is_right_edge():
                    next_pos = Position(point.row - 1, point.col + 1)
                    next_point = self.board_points[next_pos]
                    road = Road(point, next_point)
                    roads[self._position_pair(pos, next_pos)] = road

                if not point.is_bottom_edge():
                    next_pos = Position(point.row + 1, point.col)
                    next_point = self.board_points[next_pos]
                    road = Road(point, next_point)
                    roads[self._position_pair(pos, next_pos)] = road
            elif point.is_descending() and not point.is_right_edge():
                next_pos = Position(point.row + 1, point.col + 1)
                next_point = self.board_points[next_pos]
                road = Road(point, next_point)
                roads[self._position_pair(pos, next_pos)] = road

        return roads


    def _build_ports(self, port_order: List[PortType]) -> dict[tuple[Position, Position], Port]:
        if len(port_order) != len(PORT_POSITIONS):
            raise RuntimeError('Cannot construct board with number of ports: %s, versus port positions: %s'.format(len(port_order), len(PORT_POSITIONS)))

        ports = dict()
        for i, (p1, p2) in enumerate(PORT_POSITIONS):
            position = self._position_pair(p1, p2)
            ports[position] = Port(self.board_points[p1], self.board_points[p2], port_order[i])

        return ports

    @staticmethod
    def _build_hexes(hex_order: List[HexType]) -> List[Hex]:
        if len(hex_order) - 1 != len(DICE_TOKEN_SEQUENCE):
            raise RuntimeError('Should have an equivalent number of dice to resource types')

        ring = 2
        dice_token_stack = DiceTokenStack()
        hex_seq_counter = 0

        hexes = []
        while ring > 0:
            row = 5.5 - ring * 2
            col = 5 - ring

            # increments by (0, 2) going horizontally
            # for each side length, we don't add last tile, as we assume
            # it will be in the top next side of the board
            # except the center (fencepost, as that would have side length of 0)
            side_increments = [
                (0, 2),
                (2, 1),
                (2, -1),
                (0, -2),
                (-2, -1),
                (-2, 1)
            ]
            curr_row = row
            curr_col = col
            for row_increment, col_increment in side_increments:
                for _ in range(ring):
                    position = HexPosition(
                        curr_row,
                        curr_col
                    )

                    hex_type = hex_order[hex_seq_counter]
                    hex_seq_counter += 1

                    dice_roll = dice_token_stack.get_token(hex_type)

                    hexes.append(
                        HexFactory()
                            .position(position)
                            .hex_type(hex_type)
                            .dice_roll(dice_roll)
                            .build()
                    )

                    curr_row += row_increment
                    curr_col += col_increment

            ring -= 1

        # fencepost -- central hex
        hex_type = hex_order[hex_seq_counter]
        dice_roll = dice_token_stack.get_token(hex_type)

        hexes.append(
            HexFactory()
                .position(HexPosition(5.5, 5))
                .hex_type(hex_type)
                .dice_roll(dice_roll)
                .build()
        )

        return hexes
