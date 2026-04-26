from typing import List, Tuple
from dataclasses import dataclass, field
import pretty_midi
from common import Color, RGB
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
    
    def save(self, tracks_el: ET.SubElement) -> None:
        el = ET.SubElement(tracks_el, "Track")

        el.set("name", self.name)
        el.set("visible", FileUtil.bool_to_str(self.visible))
        el.set("color", FileUtil.tuple_to_str(self.color))
        el.set("alpha", str(self.alpha))
        el.set("barHeightRatio", str(self.bar_height_ratio))
        el.set("barSecAcrossScreen", str(self.bar_sec_across_screen))

        notes_el = ET.SubElement(el, "Notes")
        for note in self.notes:
            note.save(notes_el)
    
    @staticmethod
    def load(track_el: ET.Element[str], schema_version: int) -> Track:
        track = Track()

        track.name=track_el.get("name")
        track.visible=FileUtil.str_to_bool(track_el.get("visible"))
        track.color=FileUtil.str_to_tuple(track_el.get("color"))
        if schema_version >= 2:
            track.alpha=int(track_el.get("alpha"))
        
        if schema_version >= 4:
            track.bar_height_ratio = float(track_el.get("barHeightRatio"))
            track.bar_sec_across_screen = float(track_el.get("barSecAcrossScreen"))

        for note_el in track_el.find("Notes").findall("Note"):
            note = Note.load(note_el, schema_version)
            track.notes.append(note)

        return track
