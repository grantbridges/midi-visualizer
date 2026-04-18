from dataclasses import dataclass
import pretty_midi
import xml.etree.ElementTree as ET

from utility.file_util import FileUtil

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
    start: float = 0 # note start in seconds
    end: float = 1 # note end in seconds

    # properties
    # (none)

    # current draw values
    alpha: int = 180

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
    
    def save(self, notes_el: ET.SubElement) -> None:
        el = ET.SubElement(notes_el, "Note")

        el.set("pitch", str(self.pitch))
        el.set("velocity", str(self.velocity))
        el.set("start", str(self.start))
        el.set("end", str(self.end))
    
    @staticmethod
    def load(note_el: ET.Element[str], schema_version: int) -> Note:
        note = Note()

        note.pitch=int(note_el.get("pitch"))
        note.velocity=int(note_el.get("velocity"))
        note.start=float(note_el.get("start"))
        note.end=float(note_el.get("end"))

        return note
