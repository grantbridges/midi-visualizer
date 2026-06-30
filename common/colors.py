from enum import Enum

from common.types import RGB

class Color(tuple, Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    LIGHTISH_GRAY = (109, 109, 109)
    LIGHT_GRAY = (180, 180, 180)
    DARK_GRAY = (52, 52, 52)
    DARKER_GRAY = (30, 30, 30)
    DARKEST_GRAY = (20, 20, 20)
    RED = (255, 0, 0)
    DELETE_RED = (170, 51, 51)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    KAYLA_1 = (50, 131, 168)
    KAYLA_2 = (179, 139, 46)