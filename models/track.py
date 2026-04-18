from typing import List, Tuple
from dataclasses import dataclass, field
import pretty_midi
from models.note import Note
import xml.etree.ElementTree as ET

from utility.file_util import FileUtil

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
    color: Tuple[int, int, int] = (0, 0, 0)
    bar_height: int = 10
    bar_pixels_per_second: int = 200 # higher = wider, visually faster

    # current draw values
    # (none)

    @staticmethod
    def create_from_midi_data(inst: pretty_midi.Instrument) -> Track:
        track = Track()

        track.name = inst.name

        for note in inst.notes:
            note = Note.create_from_midi_data(note)
            track.notes.append(note)

        return track
    
    def save(self, tracks_el: ET.SubElement) -> None:
        el = ET.SubElement(tracks_el, "Track")

        el.set("name", self.name)
        el.set("visible", FileUtil.bool_to_str(self.visible))
        el.set("color", FileUtil.tuple_to_str(self.color))
        el.set("barHeight", str(self.bar_height))
        el.set("pps", str(self.bar_pixels_per_second))

        notes_el = ET.SubElement(el, "Notes")
        for note in self.notes:
            note.save(notes_el)
    
    @staticmethod
    def load(track_el: ET.Element[str], schema_version: int) -> Track:
        track = Track()

        track.name=track_el.get("name")
        track.visible=FileUtil.str_to_bool(track_el.get("visible"))
        track.color=FileUtil.str_to_tuple(track_el.get("color"))
        track.bar_height=int(track_el.get("barHeight"))
        track.bar_pixels_per_second=int(track_el.get("pps"))

        for note_el in track_el.find("Notes").findall("Note"):
            note = Note.load(note_el, schema_version)
            track.notes.append(note)

        return track
