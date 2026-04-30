from enum import Enum

class Resolution(tuple, Enum):
    HD = (1280, 720) # HD (720p)
    FullHD = (1920, 1080) # Full HD (1080p)
    QuadHD = (2560, 1440) # Quad HD (1440p)
    UltraHD = (3840, 2160) # 4k (2160p)