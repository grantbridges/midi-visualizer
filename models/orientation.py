from enum import Enum

class Orientation(tuple, Enum):
    Landscape = (16, 9)
    Vertical = (9, 16)
    Square = (1, 1)
    Portrait = (4, 5)

    def __str__(self) -> str:
        w, h = self.value
        return f"{self.name} ({w}:{h})"