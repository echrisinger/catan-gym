from dataclasses import dataclass

from catan import Board
from catan.bank import Bank
from catan.board_point import BoardPoint
from catan.enums import Action, PlayerColor, BuildingType
from catan.hand import ResourceHand, DevCardHand

_STARTING_CITIES = 5
_STARTING_SETTLEMENTS = 5
_STARTING_ROADS = 20

class Player:
    def __init__(self, color: PlayerColor, board: Board, bank: Bank, turn_position: int):
        self.color = color

        self.board = board
        self.bank = bank

        self.turn_position = turn_position

        self.other_players = []

        self.resource_cards: ResourceHand = ResourceHand()
        self.dev_cards: DevCardHand = DevCardHand()

        self.cities = _STARTING_CITIES
        self.settlements = _STARTING_SETTLEMENTS
        self.roads = _STARTING_ROADS

        self.has_largest_army = False
        self.has_longest_road = False

    def add_other_players(self, *other_players: "Player"):
        self.other_players.extend(other_players)

    def victory_points(self):
        points = 0
        if self.has_largest_army:
            points += 2

        if self.has_longest_road:
            points += 2

        points += (_STARTING_CITIES - self.cities) * 2
        points += (_STARTING_SETTLEMENTS - self.settlements)
        points += self.dev_cards.victory_points

        return points

    def has_won(self):
        return self.victory_points() >= 10

    def has_road_materials(self) -> bool:
        return self.resource_cards.wood > 0 and \
            self.resource_cards.brick > 0

    def has_road_spot(self) -> bool:
        # need to index roads by board points
        pass

    def place_road(self):
        self.resource_cards.wood -= 1
        self.resource_cards.brick -= 1

        self.bank.wood += 1
        self.bank.brick += 1

        # todo - road connecting two points logic
        pass

    def has_settlement_materials(self) -> bool:
        return self.resource_cards.wood > 0 and \
            self.resource_cards.brick > 0 and \
            self.resource_cards.sheep > 0 and \
            self.resource_cards.wheat > 0

    def has_settlement_spot(self) -> bool:
        # need to maintain a set of all settleable points
        # which will utilize BoardPoint to Road to BoardPoint connection
        # and union that with points roads are connected with
        pass

    def has_settlement(self):
        return self.settlements != 5

    def place_settlement(self, point: BoardPoint):
        point.color = self.color
        point.building = BuildingType.SETTLEMENT

        self.settlements -= 1

        self.resource_cards.wood -= 1
        self.resource_cards.brick -= 1
        self.resource_cards.wheat -= 1
        self.resource_cards.sheep -= 1

        self.bank.wood += 1
        self.bank.brick += 1
        self.bank.wheat += 1
        self.bank.sheep += 1

    def has_city_materials(self) -> bool:
        return self.resource_cards.wheat > 2 and \
            self.resource_cards.ore > 3

    def place_city(self, point: BoardPoint):
        point.building = BuildingType.CITY

        self.cities -= 1
        self.settlements += 1

        self.resource_cards.wheat -= 2
        self.resource_cards.ore -= 3

        self.bank.wheat += 2
        self.bank.ore += 3

    def has_dev_card_materials(self) -> bool:
        return self.resource_cards.wheat > 0 and \
            self.resource_cards.ore > 0 and \
            self.resource_cards.sheep > 0

    def execute_turn(self):
        next_action = self.plan_next_action()
        while next_action:
            self.execute_action(next_action)
            next_action = self.plan_next_action()

    def plan_next_action(self) -> Action | None:
        # TODO - need to turn this into returning dataclass w/ positions
        if self.has_city_materials() and self.has_settlement():
            return Action.BUILD_CITY
        elif self.has_settlement_materials() and self.has_settlement_spot():
            return Action.BUILD_SETTLEMENT
        elif self.has_road_materials() and self.has_road_spot():
            return Action.BUILD_ROAD
        elif self.has_dev_card_materials() and self.bank.has_dev_card():
            return Action.BUILD_DEV_CARD
        return None

    def execute_action(self, action: Action):
        """TODO - build naive policy of building cities, whenever possible, then settlements, then roads"""
        pass
