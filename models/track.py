from typing import List, Tuple
from dataclasses import dataclass, field
import pretty_midi
from common import Color, RGB
from models.note import Note

# ----

'''
A Track corresponds to a single track from a MIDI file.
It contains MIDI note data.
'''
@dataclass
class Track:
    # midi data
    name: str = 'Track'
    notes: List[Note] = field(default_factory=list)
    
    # properties
    visible: bool = True
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    bar_height_ratio: float = .05 # 0 - 1, ratio of screen height
    bar_sec_across_screen: float = 2 # seconds for bar to fully cross screen

    @staticmethod
    def create_from_midi_data(inst: pretty_midi.Instrument) -> Track:
        track = Track()

        track.name = inst.name

        for note in inst.notes:
            note = Note.create_from_midi_data(note)
            track.notes.append(note)

        return track

    def save(self) -> dict:
        return {
            "name": self.name,
            "visible": self.visible,
            "color": list(self.color),
            "alpha": self.alpha,
            "barHeightRatio": self.bar_height_ratio,
            "barSecAcrossScreen": self.bar_sec_across_screen,

            "notes": [
                note.save()
                for note in self.notes
            ]
        }
    
    @staticmethod
    def load(data: dict) -> Track:
        track = Track()

        track.name = data.get("name", "Track")
        track.visible = data.get("visible", True)
        track.color = tuple(data.get("color", [255, 255, 255]))
        track.alpha = data.get("alpha", 255)
        track.bar_height_ratio = data.get("barHeightRatio", 0.02)
        track.bar_sec_across_screen = data.get("barSecAcrossScreen", 8.0)

        track.notes = [
            Note.load(note_data)
            for note_data in data.get("notes", [])
        ]

        return track
