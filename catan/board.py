
from catan.board_point import BoardPoint
from catan.dice import DiceTokenStack
from catan.enums import HexType, PortType
from catan.hex import Hex, HexPosition, HexFactory
from catan.port import Port
from catan.position import Position
from catan.road import Road
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
    (Position(1, 2), Position(0, 3)),
    (Position(0, 5), Position(1, 6)),
    (Position(2, 8), Position(3, 9)),
    (Position(5, 10), Position(6, 10)),
    (Position(8, 9), Position(9, 8)),
    (Position(11, 5), Position(10, 6)),
    (Position(10, 2), Position(11, 3)),
    (Position(7, 1), Position(8, 1)),
    (Position(3, 1), Position(4, 1)),
]

HEX_AMOUNTS = (
    [HexType.DESERT] +
    [HexType.WOOD] * 4 +
    [HexType.BRICK] * 3 +
    [HexType.WHEAT] * 4 +
    [HexType.ORE] * 3 +
    [HexType.SHEEP] * 4
)

def shuffle_hexes() -> list[HexType]:
    return copy_and_shuffle(HEX_AMOUNTS)

def shuffle_ports() -> list[PortType]:
    return copy_and_shuffle(PORT_AMOUNTS)

class Board:
    def __init__(self, hex_order: list[HexType], port_order: list[PortType]):
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
                    roads[Position.pair(pos, next_pos)] = road

                if not point.is_bottom_edge():
                    next_pos = Position(point.row + 1, point.col)
                    next_point = self.board_points[next_pos]
                    road = Road(point, next_point)
                    roads[Position.pair(pos, next_pos)] = road
            elif point.is_descending() and not point.is_right_edge():
                next_pos = Position(point.row + 1, point.col + 1)
                next_point = self.board_points[next_pos]
                road = Road(point, next_point)
                roads[Position.pair(pos, next_pos)] = road

        return roads

    def _build_ports(self, port_order: list[PortType]) -> dict[tuple[Position, Position], Port]:
        if len(port_order) != len(PORT_POSITIONS):
            raise RuntimeError(f"Cannot construct board with number of ports: {len(port_order)}, versus port positions: {len(PORT_POSITIONS)}")

        ports = {}
        for i, (p1, p2) in enumerate(PORT_POSITIONS):
            key = Position.pair(p1, p2)
            ports[key] = Port(self.board_points[p1], self.board_points[p2], port_order[i])

        return ports

    # Hex ring traversal increments: (row, col) deltas for each side of the hexagon.
    # Each side is traversed for `ring` steps, skipping the last tile per side
    # (it becomes the first tile of the next side). Center is a fencepost case.
    _HEX_SIDE_INCREMENTS = [
        (0, 2),
        (2, 1),
        (2, -1),
        (0, -2),
        (-2, -1),
        (-2, 1)
    ]

    @staticmethod
    def _build_hexes(hex_order: list[HexType]) -> list[Hex]:
        ring = 2
        dice_token_stack = DiceTokenStack()
        if len(hex_order) - 1 != dice_token_stack.size():
            raise RuntimeError('Should have an equivalent number of dice to resource types')

        hex_seq_counter = 0

        hexes = []
        while ring > 0:
            row = 5.5 - ring * 2
            col = 5 - ring
            curr_row = row
            curr_col = col
            for row_increment, col_increment in Board._HEX_SIDE_INCREMENTS:
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
