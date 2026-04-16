from typing import List
from dataclasses import dataclass
from models.note import Note

# ----

'''
A Track corresponds to a single track from a MIDI file.
It contains MIDI note data.
'''
@dataclass
class Track:
    name: str
    notes: List[Note]
    color: tuple[int, int, int]