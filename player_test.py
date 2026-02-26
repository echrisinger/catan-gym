import pytest

from catan import Player, PlayerColor


@pytest.fixture
def player():
    return Player(PlayerColor.RED)


def test_new_player_has_zero_points(player):
    assert player.victory_points() == 0


def test_settlement_awards_one_point(player):
    player.settlements = 4
    assert player.victory_points() == 1


def test_city_awards_two_points(player):
    player.cities = 4
    assert player.victory_points() == 2


def test_all_sources_combined(player):
    player.settlements = 3       # 2 settlements = 2 pts
    player.cities = 3            # 2 cities = 4 pts
    player.has_largest_army = 1  # 2 pts
    player.has_longest_road = 1  # 2 pts
    player.dev_cards.victory_points = 1  # 1 pt
    assert player.victory_points() == 11


def test_has_won_at_ten_points(player):
    player.settlements = 0       # 5 settlements = 5 pts
    player.cities = 3            # 2 cities = 4 pts
    player.dev_cards.victory_points = 1  # 1 pt = 10 total
    assert player.has_won() is True


def test_has_not_won_below_ten(player):
    player.settlements = 1       # 4 settlements = 4 pts
    player.cities = 3            # 2 cities = 4 pts
    player.dev_cards.victory_points = 1  # 1 pt = 9 total
    assert player.has_won() is False