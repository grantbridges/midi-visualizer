from pathlib import Path
import xml.etree.ElementTree as ET
from typing import List, Tuple
from dataclasses import dataclass, field
import pretty_midi
from common.colors import Color
from models.track import Track, Note
from utility import FileUtil

# ----

'''
History
  1 - Initial version
'''
VIS_CONFIG_SCHEMA_VERSION = 1

'''
Top level construct containing all visualizing info
'''
@dataclass
class VisConfig:
    # midi data
    tracks: List[Track] = field(default_factory=list)

    # properties
    track_name: str = ""
    bg_color: Tuple[int, int, int] = Color.DARKEST_GRAY
    play_audio: bool = True
    
    @staticmethod
    def create_from_midi_data(track_name: str, midi_data: pretty_midi.PrettyMIDI):
        vis_config = VisConfig(track_name=track_name)

        instruments: List[pretty_midi.Instrument] = midi_data.instruments
        for inst in instruments:
            if not inst.name:
                print("Warning: Loaded instrument from MIDI data with no name - skipping")
                continue

            track = Track.create_from_midi_data(inst)
            vis_config.tracks.append(track)

        return vis_config
    
    def save(self, path: str) -> None:
        print(f"Saving config at \"{path}\"")

        root = ET.Element("VisConfig")
        root.set("schemaVersion", str(VIS_CONFIG_SCHEMA_VERSION))
        root.set("trackName", self.track_name)
        root.set("bgColor", FileUtil.tuple_to_str(self.bg_color))
        root.set("playAudio", FileUtil.bool_to_str(self.play_audio))

        tracks_el = ET.SubElement(root, "Tracks")
        for track in self.tracks:
            track.save(tracks_el)

        FileUtil.xml_indent(root)

        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)
    
    @staticmethod
    def load(path: str) -> VisConfig:
        if not Path(path).is_file():
            print(f"No existing config file found at \"{path}\"")
            return None
        
        print(f"Loading config from \"{path}\"")
        
        tree = ET.parse(path)
        root = tree.getroot()

        schema_version = int(root.get("schemaVersion"))

        vis_config = VisConfig()
        vis_config.track_name = root.get("trackName")
        vis_config.bg_color = FileUtil.str_to_tuple(root.get("bgColor"))
        vis_config.play_audio = FileUtil.str_to_bool(root.get("playAudio"))

        for track_el in root.find("Tracks").findall("Track"):
            track = Track.load(track_el, schema_version)
            vis_config.tracks.append(track)

        return vis_config

    # Loads in all note data from midi (assumes tracks are already defined)
    def populate_notes_from_midi_data(self, midi_data: pretty_midi.PrettyMIDI):
        instruments: List[pretty_midi.Instrument] = midi_data.instruments

        for inst in instruments:
            # ensure loaded instrument has a name - we use it for track indexing
            if not inst.name:
                print("Warning: Loaded instrument from MIDI data with no name - skipping")
                continue

            # get corresponding track by instrument name
            track = self.get_track_by_name(inst.name)
            if track == None:
                print(f"Warning: Loaded instrument {inst.name} from MIDI data with no match in VisConfig tracks - skipping")
                continue

            track.notes = []
            for note in inst.notes:
                track.notes.append(Note(note.pitch, note.velocity, note.start, note.end))

    # Getters

    def get_track_by_name(self, name: str) -> Track:
        return next((track for track in self.tracks if track.name == name), None)
    
    def get_pitch_bounds(self) -> tuple[int, int]:
        min_pitch = min(
            note.pitch
            for track in self.tracks
            for note in track.notes
        )

        max_pitch = max(
            note.pitch
            for track in self.tracks
            for note in track.notes
        )

        return (min_pitch, max_pitch)
    
    def get_time_bounds(self) -> tuple[int, int]:
        start = min(
            note.start
            for track in self.tracks
            for note in track.notes
        )

        end = max(
            note.end
            for track in self.tracks
            for note in track.notes
        )

        return (start, end)
