import pytest

from catan.board_point import BoardPoint


# -- is_right_edge --

@pytest.mark.parametrize("row, col", [
    (1, 8),
    (3, 9),
    (5, 10),
    (6, 10),
    (8, 9),
    (10, 8),
])
def test_right_edge_points(row, col):
    assert BoardPoint(row, col).is_right_edge() is True


@pytest.mark.parametrize("row, col", [
    # interior points
    (5, 4),
    (6, 6),
    (3, 5),
    # leftmost points
    (5, 0),
    (3, 1),
    (0, 3),
    # one column inside the right edge
    (1, 6),
    (3, 7),
    (5, 8),
    (8, 7),
    (10, 6),
])
def test_non_right_edge_points(row, col):
    assert BoardPoint(row, col).is_right_edge() is False


def test_right_edge_symmetry_top_and_bottom():
    """Rows equidistant from center should have the same threshold."""
    assert BoardPoint(1, 8).is_right_edge() is True
    assert BoardPoint(10, 8).is_right_edge() is True
    assert BoardPoint(0, 7).is_right_edge() is False
    assert BoardPoint(11, 7).is_right_edge() is False


# -- is_bottom_edge --

@pytest.mark.parametrize("row, col", [
    (10, 2),
    (10, 4),
    (10, 6),
    (10, 8),
    (11, 3),
    (11, 5),
    (11, 7),
])
def test_bottom_edge_points(row, col):
    assert BoardPoint(row, col).is_bottom_edge() is True


@pytest.mark.parametrize("row, col", [
    # interior points
    (5, 4),
    (6, 6),
    (3, 5),
    # top row
    (0, 3),
    (0, 5),
    # middle rows
    (9, 4),
    (9, 6),
    (8, 5),
])
def test_non_bottom_edge_points(row, col):
    assert BoardPoint(row, col).is_bottom_edge() is False


def test_outermost_columns_never_bottom_edge():
    """Cols 0, 1, 9, 10 are side edges, not bottom edges."""
    assert BoardPoint(5, 0).is_bottom_edge() is False
    assert BoardPoint(6, 0).is_bottom_edge() is False
    assert BoardPoint(6, 10).is_bottom_edge() is False
    assert BoardPoint(5, 10).is_bottom_edge() is False
    assert BoardPoint(7, 1).is_bottom_edge() is False
    assert BoardPoint(8, 1).is_bottom_edge() is False
    assert BoardPoint(7, 9).is_bottom_edge() is False
    assert BoardPoint(8, 9).is_bottom_edge() is False


def test_row_9_is_not_bottom_edge():
    """Row 9 is just above the bottom edge threshold of 10."""
    for col in (2, 4, 6, 8):
        assert BoardPoint(9, col).is_bottom_edge() is False


# -- __hash__ --

def test_all_board_points_hash_uniquely():
    """Every valid board point should have a distinct hash."""
    points = []
    for row in range(12):
        if row in {0, 11}:
            cols = [3, 5, 7]
        elif row in {1, 2, 9, 10}:
            cols = [2, 4, 6, 8]
        elif row in {3, 4, 7, 8}:
            cols = [1, 3, 5, 7, 9]
        else:
            cols = [0, 2, 4, 6, 8, 10]
        points.extend(BoardPoint(row, c) for c in cols)

    hashes = [hash(p) for p in points]
    assert len(set(hashes)) == len(points)


def test_all_grid_positions_hash_uniquely():
    """Every (row, col) in the full 12x11 grid should have a distinct hash."""
    points = [BoardPoint(r, c) for r in range(12) for c in range(11)]
    hashes = [hash(p) for p in points]
    assert len(set(hashes)) == len(points)


def test_equal_points_hash_equally():
    assert hash(BoardPoint(3, 5)) == hash(BoardPoint(3, 5))


def test_different_points_hash_differently():
    assert hash(BoardPoint(1, 0)) != hash(BoardPoint(0, 10))