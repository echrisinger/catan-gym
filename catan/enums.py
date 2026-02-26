from enum import StrEnum

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

class BuildingType(StrEnum):
    SETTLEMENT = 'Settlement'
    CITY = 'City'
