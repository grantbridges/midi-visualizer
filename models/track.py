from typing import List, Tuple
from dataclasses import dataclass, field
import pretty_midi
from common import Color, RGB
from models.note import Note
from uuid import UUID

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
    
    # group reference
    group_id: UUID | None = None

    # properties
    visible: bool = True
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    bar_height_ratio: float = .05 # 0 - 1, ratio of screen height
    bar_sec_across_screen: float = 2 # seconds for bar to fully cross screen

    # computed props
    pitch_min: int = 0
    pitch_max: int = 1
    time_min: float = 0.0
    time_max: float = 1.0

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
            "groupId": str(self.group_id) if self.group_id else None,
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
    def load(data: dict, schema_version: int) -> Track:
        track = Track()

        track.name = data["name"]
        track.visible = data["visible"]
        track.color = tuple(data["color"])
        track.alpha = data["alpha"]
        track.bar_height_ratio = data["barHeightRatio"]
        track.bar_sec_across_screen = data["barSecAcrossScreen"]

        track.notes = [
            Note.load(note_data, schema_version)
            for note_data in data["notes"]
        ]

        if schema_version >= 4:
            group_id = data["groupId"]
            track.group_id = UUID(group_id) if group_id else None

        return track
    
    def init(self):
        # (note: shouldn't actually have empty notes here - track would be
        # deleted before being initialized if so)
        note_pitches = [note.pitch for note in self.notes]
        self.pitch_min = min(note_pitches) if note_pitches else 0
        self.pitch_max = max(note_pitches) if note_pitches else 1
        
        note_starts = [note.start for note in self.notes]
        self.time_min = min(note_starts) if note_starts else 0.0
        note_ends = [note.end for note in self.notes]
        self.time_max = max(note_ends) if note_ends else 1.0