from typing import List, Optional
from dataclasses import dataclass

'''
A Note corresponds to a single midi note value.
It contains relevant MIDI note data.
'''
@dataclass
class Note:
    pitch: int
    velocity: int
    start: float
    end: float

    @property
    def duration(self):
        return self.end - self.start
