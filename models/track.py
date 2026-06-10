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
    
    def update_notes_from_midi_data(self, inst: pretty_midi.Instrument):
        self.notes.clear()
        for note in inst.notes:
            note = Note.create_from_midi_data(note)
            self.notes.append(note)

    def save(self) -> dict:
        return {
            "name": self.name,
            "group_id": str(self.group_id) if self.group_id else None,
            "notes": {
                # break down note data into comma separated strings for tighter storage
                "pitches": ",".join(str(note.pitch) for note in self.notes),
                "velocities": ",".join(str(note.velocity) for note in self.notes),
                "starts": ",".join(str(note.start) for note in self.notes),
                "ends": ",".join(str(note.end) for note in self.notes)
            }
        }
    
    @staticmethod
    def load(data: dict, schema_version: int) -> Track:
        track = Track()

        track.name = data["name"]

        # deserialize comma separated string data into Note objects
        notes_data = data["notes"]
        pitches = notes_data["pitches"].split(",")
        velocities = notes_data["velocities"].split(",")
        starts = notes_data["starts"].split(",")
        ends = notes_data["ends"].split(",")

        track.notes = [
            Note(
                pitch=int(pitch),
                velocity=int(velocity),
                start=float(start),
                end=float(end),
            )
            for pitch, velocity, start, end in zip(
                pitches,
                velocities,
                starts,
                ends,
                strict=True,
            )
        ]

        if schema_version >= 4:
            group_id = data["group_id"]
            track.group_id = UUID(group_id) if group_id else None

        return track
    
    def init(self):
        if len(self.notes) == 0:
            # shouldn't actually get here - track should've been removed already
            print(f"Track | Init | Warning: Attempted initialization on track \"{self.name}\" with no notes")
            return
        
        note_pitches = [note.pitch for note in self.notes]
        self.pitch_min = min(note_pitches)
        self.pitch_max = max(note_pitches)
        
        note_starts = [note.start for note in self.notes]
        self.time_min = min(note_starts)
        note_ends = [note.end for note in self.notes]
        self.time_max = max(note_ends)