from typing import List, Set
from dataclasses import dataclass
from random import shuffle

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

PORT_POSITIONS = [
    (BoardPoint(1, 2), BoardPoint(0, 3)),
    (BoardPoint(0, 5), BoardPoint(1, 6)),
    (BoardPoint(3, 1), BoardPoint(4, 1)),
    (BoardPoint(2, 8), BoardPoint(3, 9)),
    (BoardPoint(5, 10), BoardPoint(6, 10)),
    (BoardPoint(7, 1), BoardPoint(8, 1)),
    (BoardPoint(8, 9), BoardPoint(9, 8)),
    (BoardPoint(10, 2), BoardPoint(11, 3)),
    (BoardPoint(11, 5), BoardPoint(12, 6))
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
        self.stack = DICE_TOKEN_SEQUENCE.copy()

    def get_token(self, hex_type: HexType) -> int:
        dice_roll = None

        if hex_type != HexType.DESERT:
            dice_roll = self.stack.pop()

        return dice_roll

def shuffle_hexes() -> List[HexType]:
    return copy_and_shuffle(HEX_AMOUNTS)

def shuffle_ports() -> List[PortType]:
    return copy_and_shuffle(PORT_AMOUNTS)

class Road:
    def __init__(self, point1: BoardPoint, point2: BoardPoint):
        self.color = None
        self.point1 = point1
        self.point2 = point2

    def build(self, color: PlayerColor):
        if self.color is not None:
            raise RuntimeError('Road is already occupied')

        self.color = color

@dataclass
class Port:
    point1: BoardPoint
    point2: BoardPoint

    resource: PortType

class Board:
    def __init__(self, hex_order: List[HexType], port_order: List[PortType]):
        self.hexes = self._build_hexes(hex_order)
        self.ports = self._build_ports(port_order)
        self.board_points = self._build_board_points()

    @staticmethod
    def _build_board_points() -> Set[BoardPoint]:
        res = []
        for row in range(0, 12):
            if row in {0, 11}:
                res += {BoardPoint(row, 3), BoardPoint(row, 5), BoardPoint(row, 7)}
            elif row in {1, 2, 9, 10}:
                res += {BoardPoint(row, 2), BoardPoint(row, 4), BoardPoint(row, 6), BoardPoint(row, 8)}
            elif row in {3, 4, 7, 8}:
                res += {BoardPoint(row, 1), BoardPoint(row, 3), BoardPoint(row, 5), BoardPoint(row, 7), BoardPoint(row, 9)}
            else:
                res += {BoardPoint(row, 0), BoardPoint(row, 2), BoardPoint(row, 4), BoardPoint(row, 6), BoardPoint(row, 8), BoardPoint(row, 10)}

        return res


    @staticmethod
    def _build_ports(port_order: List[PortType]) -> List[Port]:
        if len(port_order) != len(PORT_POSITIONS):
            raise RuntimeError('Cannot construct board with number of ports: %s, versus port positions: %s'.format(len(port_order), len(PORT_POSITIONS)))

        return [
            Port(port[0], port[1], port_order[i])
            for i, port in enumerate(PORT_POSITIONS)
        ]

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
