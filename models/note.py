from dataclasses import dataclass
import pretty_midi

# ----

'''
A Note corresponds to a single midi note value.
It contains relevant MIDI note data.
'''
@dataclass
class Note:
    # midi data
    pitch: int = 50
    velocity: int = 70 # 0-127
    start: float = 0.0 # note start in seconds
    end: float = 1.0 # note end in seconds

    # properties
    # (none)

    @property
    def duration(self):
        return self.end - self.start
    
    @staticmethod
    def create_from_midi_data(data: pretty_midi.Note) -> Note:
        note = Note()

        note.pitch = data.pitch
        note.velocity = data.velocity
        note.start = data.start
        note.end = data.end

        return note

    def save(self) -> dict:
        return {
            "pitch": self.pitch,
            "velocity": self.velocity,
            "start": self.start,
            "end": self.end,
        }
    
    @staticmethod
    def load(data: dict, schema_version: int) -> Note:
        note = Note()

        note.pitch = data["pitch"]
        note.velocity = data["velocity"]
        note.start = data["start"]
        note.end = data["end"]

        return note
    
    def init(self):
        pass
