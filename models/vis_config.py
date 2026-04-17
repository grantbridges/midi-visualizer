from typing import List, Tuple
from dataclasses import dataclass, field
from common.colors import Color
from models.track import Track

# ----

'''
Top level construct containing all visualizing info
'''
@dataclass
class VisConfig:
    # properties
    bg_color: Tuple[int, int, int] = Color.DARKEST_GRAY

    tracks: List[Track] = field(default_factory=list)
