from enum import Enum

class Resolution(tuple, Enum):
    HD = (1280, 720)
    FullHD = (1920, 1080)
    QuadHD = (2560, 1440)
    UltraHD = (3840, 2160)