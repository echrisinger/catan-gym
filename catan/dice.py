from catan.enums import HexType

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

    def size(self):
        return len(self.stack)