from typing import List, Tuple
from dataclasses import dataclass, field
from models.note import Note

# ----

'''
A Track corresponds to a single track from a MIDI file.
It contains MIDI note data.
'''
@dataclass
class Track:
    # read from midi data
    name: str = 'Track'
    notes: List[Note] = field(default_factory=list)
    
    # visualization properties from config
    visible: bool = True
    color: Tuple[int, int, int] = (0, 0, 0)
    bar_height: int = 10
    bar_pixels_per_second: int = 200 # higher = wider, visually faster
