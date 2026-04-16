from enum import Enum

class Color(tuple, Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    LIGHT_GRAY = (180, 180, 180)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # takes an rgb tuple + alpha value and returns rgba tuple
    @staticmethod
    def rgba(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int, int]:
        return (color[0], color[1], color[2], alpha)