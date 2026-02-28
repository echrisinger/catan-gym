import pytest

from catan import (
    Board, HexType, HexPosition, PortType, BoardPoint, Position,
    ResourceHex, DesertHex,
)


# -- Fixtures --

@pytest.fixture
def default_hex_order():
    return [
        HexType.ORE, HexType.WHEAT, HexType.WOOD,
        HexType.ORE, HexType.WHEAT, HexType.SHEEP,
        HexType.WHEAT, HexType.SHEEP, HexType.WOOD,
        HexType.BRICK, HexType.DESERT, HexType.BRICK,
        HexType.SHEEP, HexType.SHEEP, HexType.WOOD,
        HexType.BRICK, HexType.ORE, HexType.WOOD,
        HexType.WHEAT,
    ]

@pytest.fixture
def default_port_order():
    return [
        PortType.ANY, PortType.WOOD, PortType.BRICK,
        PortType.ANY, PortType.ANY, PortType.SHEEP,
        PortType.ANY, PortType.ORE, PortType.WHEAT,
    ]

@pytest.fixture
def board(default_hex_order, default_port_order):
    return Board(default_hex_order, default_port_order)


# -- Hex tests --

# Expected hex layout after clockwise ring traversal (outer → inner → center).
# Ring 2 starts at top-left (1.5, 3) and walks all 6 sides of the hexagon.
# Ring 1 starts at (3.5, 4). Center is (5.5, 5).
EXPECTED_HEXES = [
    # --- ring 2 (outer, 12 hexes) ---
    # top row, left to right
    (HexPosition(1.5, 3), HexType.ORE,    5),
    (HexPosition(1.5, 5), HexType.WHEAT,  2),
    # down-right edge
    (HexPosition(1.5, 7), HexType.WOOD,   6),
    (HexPosition(3.5, 8), HexType.ORE,    3),
    # down-left edge
    (HexPosition(5.5, 9), HexType.WHEAT,  8),
    (HexPosition(7.5, 8), HexType.SHEEP, 10),
    # bottom row, right to left
    (HexPosition(9.5, 7), HexType.WHEAT,  9),
    (HexPosition(9.5, 5), HexType.SHEEP, 12),
    # up-left edge
    (HexPosition(9.5, 3), HexType.WOOD,  11),
    (HexPosition(7.5, 2), HexType.BRICK,  4),
    # up-right edge
    (HexPosition(5.5, 1), HexType.DESERT, None),
    (HexPosition(3.5, 2), HexType.BRICK,  8),
    # --- ring 1 (inner, 6 hexes) ---
    (HexPosition(3.5, 4), HexType.SHEEP, 10),
    (HexPosition(3.5, 6), HexType.SHEEP,  9),
    (HexPosition(5.5, 7), HexType.WOOD,   4),
    (HexPosition(7.5, 6), HexType.BRICK,  5),
    (HexPosition(7.5, 4), HexType.ORE,    6),
    (HexPosition(5.5, 3), HexType.WOOD,   3),
    # --- center ---
    (HexPosition(5.5, 5), HexType.WHEAT, 11),
]


def test_board_has_19_hexes(board):
    assert len(board.hexes) == 19


def test_board_hexes_built_with_correct_hexes(board):
    """Each hex should be at the expected position with the expected type."""
    for i, (pos, hex_type, _) in enumerate(EXPECTED_HEXES):
        h = board.hexes[i]
        assert h.position == pos, (
            f"hex {i}: expected position {pos}, got {h.position}"
        )
        assert h.hex_type == hex_type, (
            f"hex {i}: expected type {hex_type}, got {h.hex_type}"
        )


def test_board_hexes_built_with_correct_dice_rolls(board):
    """Resource hexes get sequential tokens from DICE_TOKEN_SEQUENCE; desert gets none."""
    for i, (_, hex_type, expected_roll) in enumerate(EXPECTED_HEXES):
        h = board.hexes[i]
        if expected_roll is None:
            assert isinstance(h, DesertHex), f"hex {i}: expected DesertHex"
        else:
            assert isinstance(h, ResourceHex), f"hex {i}: expected ResourceHex"
            assert h.dice_roll == expected_roll, (
                f"hex {i}: expected dice roll {expected_roll}, got {h.dice_roll}"
            )


def test_desert_hex_is_blocked(board):
    desert = [h for h in board.hexes if h.hex_type == HexType.DESERT]
    assert len(desert) == 1
    assert desert[0].is_blocked is True


# -- Port tests --

EXPECTED_PORTS = [
    (BoardPoint(1, 2),  BoardPoint(0, 3),   PortType.ANY),
    (BoardPoint(0, 5),  BoardPoint(1, 6),   PortType.WOOD),
    (BoardPoint(3, 1),  BoardPoint(4, 1),   PortType.BRICK),
    (BoardPoint(2, 8),  BoardPoint(3, 9),   PortType.ANY),
    (BoardPoint(5, 10), BoardPoint(6, 10),  PortType.ANY),
    (BoardPoint(7, 1),  BoardPoint(8, 1),   PortType.SHEEP),
    (BoardPoint(8, 9),  BoardPoint(9, 8),   PortType.ANY),
    (BoardPoint(10, 2), BoardPoint(11, 3),  PortType.ORE),
    (BoardPoint(11, 5), BoardPoint(12, 6),  PortType.WHEAT),
]


def test_board_has_9_ports(board):
    assert len(board.ports) == 9


def test_board_hexes_built_with_correct_ports(board):
    """Each port should connect the expected pair of board points with the expected type."""
    for i, (p1, p2, port_type) in enumerate(EXPECTED_PORTS):
        port = board.ports[i]
        assert port.point1 == p1, (
            f"port {i}: expected point1 ({p1.row}, {p1.col}), "
            f"got ({port.point1.row}, {port.point1.col})"
        )
        assert port.point2 == p2, (
            f"port {i}: expected point2 ({p2.row}, {p2.col}), "
            f"got ({port.point2.row}, {port.point2.col})"
        )
        assert port.resource == port_type, (
            f"port {i}: expected {port_type}, got {port.resource}"
        )


# -- Road tests --

def test_board_adheres_to_eulers_formula(board):
    assert len(board.board_points) - len(board.roads) + (len(board.hexes) + 1) == 2
    assert len(board.hexes) == 19
    assert len(board.board_points) == 54
    assert len(board.roads) == 72


@pytest.mark.parametrize("p1, p2", [
    # top-left corner
    (Position(0, 3), Position(1, 4)),   # descending right-down
    # vertical road between rows 1-2
    (Position(1, 2), Position(2, 2)),   # ascending down
    # ascending right-up from widest row
    (Position(5, 0), Position(4, 1)),
    # descending right-down from widest row
    (Position(6, 0), Position(7, 1)),
    # center of board
    (Position(5, 4), Position(6, 4)),   # ascending down
    (Position(5, 4), Position(4, 5)),   # ascending right-up
    (Position(6, 4), Position(7, 5)),   # descending right-down
    # bottom-left corner
    (Position(10, 2), Position(11, 3)), # descending right-down
])
def test_specific_roads_exist(board, p1, p2):
    key = (min(p1, p2), max(p1, p2))
    assert key in board.roads, f"road {p1}-{p2} not found"


def test_road_key_order_is_normalized(board):
    """Looking up a road with either endpoint order should find the same road."""
    p1, p2 = Position(0, 3), Position(1, 4)
    key_forward = (min(p1, p2), max(p1, p2))
    key_reverse = (min(p2, p1), max(p2, p1))
    assert key_forward == key_reverse
    assert key_forward in board.roads


def test_road_endpoints_are_board_point_instances(board):
    """Each road's point1/point2 should be the actual BoardPoint from board_points."""
    for (pos1, pos2), road in board.roads.items():
        assert road.point1 is board.board_points[pos1] or road.point1 is board.board_points[pos2]
        assert road.point2 is board.board_points[pos1] or road.point2 is board.board_points[pos2]


@pytest.mark.parametrize("p1, p2", [
    # right edge: ascending right-up should not exist
    (Position(1, 8), Position(0, 9)),
    (Position(3, 9), Position(2, 10)),
    (Position(5, 10), Position(4, 11)),
    # right edge: descending right-down should not exist
    (Position(6, 10), Position(7, 11)),
    (Position(8, 9), Position(9, 10)),
    (Position(10, 8), Position(11, 9)),
    # bottom edge: ascending down should not exist
    (Position(11, 3), Position(12, 3)),
    (Position(11, 5), Position(12, 5)),
    (Position(11, 7), Position(12, 7)),
])
def test_roads_off_right_and_bottom_edges_do_not_exist(board, p1, p2):
    key = (min(p1, p2), max(p1, p2))
    assert key not in board.roads, f"road {p1}-{p2} should not exist"