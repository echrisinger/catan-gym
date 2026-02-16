from enum import StrEnum
from typing import Set, List, DefaultDict
from dataclasses import dataclass
from random import shuffle
from abc import ABC

class ResourceType(StrEnum):
    WOOD = 'Wood'
    BRICK = 'Brick'
    WHEAT = 'Wheat'
    ORE = 'Ore'
    SHEEP = 'Sheep'

class DevCardType(StrEnum):
    KNIGHT = 'Knight'
    YEAR_OF_PLENTY = 'Year of Plenty'
    MONOPOLY = 'Monopoly'
    ROAD_BUILDING = 'Road Building'
    VICTORY_POINT = '+1 VP'

class HexType(StrEnum):
    WOOD = 'Wood'
    BRICK = 'Brick'
    WHEAT = 'Wheat'
    ORE = 'Ore'
    SHEEP = 'Sheep'
    DESERT = 'Desert'

class PortType(StrEnum):
    WOOD = 'Wood'
    BRICK = 'Brick'
    WHEAT = 'Wheat'
    ORE = 'Ore'
    SHEEP = 'Sheep'
    ANY = 'Any'

class PlayerColor(StrEnum):
    RED = 'Red'
    BLUE = 'Blue'
    ORANGE = 'White'
    GREEN = 'Green'

@dataclass(frozen=True)
class HexPosition:
    """
    Hex positions are identified by floats (1.5, 3.5, 5.5) as the row (as they're vertically between hash marks)
    Not the best way to identify an object, and we could just double the vertical axis, but this is probably
    conceptually easier to understand, so the board points don't have to be incremented by 2.
    """
    row: float
    col: int


class Hex(ABC):
    def __init__(self, position: HexPosition, hex_type: HexType):
        self.position = position
        self.hex_type = hex_type
        self.is_blocked = False

    def set_blocked(self, is_blocked: bool):
        if self.is_blocked:
            raise RuntimeError('Cannot block an already blocked hex')
        self.is_blocked = is_blocked

class ResourceHex(Hex):
    def __init__(self, position: HexPosition, hex_type: HexType, dice_roll: int):
        super().__init__(position, hex_type)
        self.dice_roll = dice_roll

class DesertHex(Hex):
    def __init__(self, position: HexPosition):
        super().__init__(position, HexType.DESERT)
        self.is_blocked = True

@dataclass
class HexFactory:
    _position: HexPosition
    _hex_type: HexType
    _dice_roll: int

    def __init__(self):
        pass

    def position(self, position: HexPosition):
        self._position = position

        return self

    def hex_type(self, hex_type: HexType):
        self._hex_type = hex_type

        return self

    def dice_roll(self, dice_roll: int):
        self._dice_roll = dice_roll

        return self

    def build(self) -> Hex:
        if self._hex_type == HexType.DESERT:
            return DesertHex(self._position)
        else:
            return ResourceHex(self._position, self._hex_type, self._dice_roll)

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

    def is_neighbor(self, other: "BoardPoint") -> bool:
        return max(
            abs(self.row - other.row),
            abs(self.col - other.col)
        ) <= 1

    def settle(self, color: PlayerColor):
        if self.color is not None:
            raise RuntimeError('Board point is already occupied')

        self.color = color

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
        self.counter = 0

    def get_token(self, hex_type: HexType) -> int:
        dice_roll = None

        if hex_type != HexType.DESERT:
            dice_roll = DICE_TOKEN_SEQUENCE[self.counter]
            self.counter += 1

        return dice_roll


def _copy_and_shuffle[T](l: List[T]) -> List[T]:
    res = l.copy()
    shuffle(res)
    return res

def shuffle_hexes() -> List[HexType]:
    return _copy_and_shuffle(HEX_AMOUNTS)

def shuffle_ports() -> List[PortType]:
    return _copy_and_shuffle(PORT_AMOUNTS)

class Road:
    def __init__(self, point1: BoardPoint, point2: BoardPoint):
        self.color = None
        self.point1 = point1
        self.point2 = point2

    def build(self, color: PlayerColor):
        if self.color is not None:
            raise RuntimeError('Road is already occupied')

        self.color = color

class Player:
    def __init__(self, color: PlayerColor):
        self.color = color

        self.resource_cards: DefaultDict[ResourceType, int] = DefaultDict()
        self.development_cards: DefaultDict[DevCardType, int] = DefaultDict()

        self.cities = 5
        self.settlements = 5
        self.roads = 20

@dataclass
class Port:
    point1: BoardPoint
    point2: BoardPoint

    resource: PortType

class Board:
    def __init__(self, hex_order: List[HexType], port_order: List[PortType]):
        self.hexes = self._build_hexes(hex_order)
        self.ports = self._build_ports(port_order)

    @staticmethod
    def _build_board_points() -> List[BoardPoint]:
        res = []
        for row in range(0, 12):
            if row in {0, 11}:
                res += [BoardPoint(row, 3), BoardPoint(row, 5), BoardPoint(row, 7)]
            elif row in {1, 2, 9, 10}:
                res += [BoardPoint(row, 2), BoardPoint(row, 4), BoardPoint(row, 6), BoardPoint(row, 8)]
            elif row in {3, 4, 7, 8}:
                res += [BoardPoint(row, 1), BoardPoint(row, 3), BoardPoint(row, 5), BoardPoint(row, 7), BoardPoint(row, 9)]
            else:
                res += [BoardPoint(row, 0), BoardPoint(row, 2), BoardPoint(row, 4), BoardPoint(row, 6), BoardPoint(row, 8), BoardPoint(row, 10)]

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
