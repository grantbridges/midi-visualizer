from enum import Enum

from common.types import RGB

class Color(tuple, Enum):
    WHITE = (255, 255, 255)
    SPLASH_SCREEN_TEXT = (224, 224, 224)
    BLACK = (0, 0, 0)
    LIGHTISH_GRAY = (109, 109, 109)
    LIGHT_GRAY = (180, 180, 180)
    DARK_GRAY = (52, 52, 52)
    DARKER_GRAY = (30, 30, 30)
    DARKEST_GRAY = (20, 20, 20)
    RED = (255, 0, 0)
    ERROR_RED = (170, 51, 51)
    PREVIEW_ERROR = (255, 130, 130)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    KAYLA_1 = (50, 131, 168)
    KAYLA_2 = (179, 139, 46)

    # branding colors
    ILLUSTRI_TEXT = (156, 226, 255)
    SPLASH_BG_BLUE = (2, 0, 40)
    SPLASH_BG_GRAY = (74, 74, 74)
    ICON_LIGHT = (105, 157, 224)
    ICON_DARK = (1, 20, 59)