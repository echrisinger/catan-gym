from catan import DevCardType
from shuffle import copy_and_shuffle

DEV_CARD_AMOUNTS = (
    [DevCardType.KNIGHT * 14] +
    [DevCardType.ROAD_BUILDING * 2] +
    [DevCardType.YEAR_OF_PLENTY * 2] +
    [DevCardType.MONOPOLY * 2] +
    [DevCardType.VICTORY_POINT * 5]
)

class Bank:
    def __init__(self):
        self.wood = 19
        self.brick = 19
        self.wheat = 19
        self.sheep = 19
        self.ore = 19
        self.dev_cards: list[DevCardType] = copy_and_shuffle(DEV_CARD_AMOUNTS)

    def has_dev_card(self):
        return self.dev_cards != 0