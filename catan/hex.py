from dataclasses import dataclass
from abc import ABC

from catan.enums import HexType

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
