from copy import copy
from dataclasses import dataclass, field
from typing import DefaultDict, List

from catan import Board
from catan.board_point import BoardPoint
from catan.enums import ResourceType, DevCardType, PlayerColor, BuildingType
from catan.hand import ResourceHand, DevCardHand

_STARTING_CITIES = 5
_STARTING_SETTLEMENTS = 5
_STARTING_ROADS = 20

class Player:
    def __init__(self, color: PlayerColor, board: Board, turn_position: int):
        self.color = color

        self.board = board
        self.turn_position = turn_position

        self.other_players = []

        self.resource_cards: ResourceHand = ResourceHand()
        self.dev_cards: DevCardHand = DevCardHand()

        self.cities = _STARTING_CITIES
        self.settlements = _STARTING_SETTLEMENTS
        self.roads = _STARTING_ROADS

        self.has_largest_army = 0
        self.has_longest_road = 0

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

    def place_settlement(self, point: BoardPoint):
        point.color = self.color
        point.building = BuildingType.SETTLEMENT

        self.settlements -= 1

        self.resource_cards.wood -= 1
        self.resource_cards.brick -= 1
        self.resource_cards.wheat -= 1
        self.resource_cards.sheep -= 1
        self.resource_cards.ore -= 1

    def place_city(self, point: BoardPoint):
        point.building = BuildingType.CITY

        self.cities -= 1
        self.settlements += 1

        self.resource_cards.wheat -= 2
        self.resource_cards.ore -= 3

    def execute_turn(self):
        # TODO trade logic
        next_action = self.plan_next_action()
        while next_action:
            self.execute_action(next_action)
            next_action = self.plan_next_action()

    def plan_next_action(self):
        pass

    def execute_action(self):
        pass

    def plan_trades(self) -> List["TradeOffer"]:
        return []

    def offer_trades(self, offers: List["TradeOffer"]) -> List["TradeOffer"]:
        for player in self.other_players:
            player.receive_trade_offers(offers)

    def receive_trade_offers(self, offers: List["TradeOffer"]) -> "TradeOffer":
        for offer in offers:
            if self.prompt_model_for_trade_policy(offer):
                offer.inactive_players_agreed.append(self)

    def prompt_model_for_trade_policy(self, _: "TradeOffer") -> bool:
        """TODO -- need to implement trade policy"""
        return False

    def execute_trade(self, active_hand: DevCardHand, inactive_hand: DevCardHand):
        pass

@dataclass
class TradeOffer:
    active_hand: DevCardHand
    inactive_hand: DevCardHand

    active_player_agreed: bool = False
    inactive_players_agreed: List[Player] = field(default_factory=list)
