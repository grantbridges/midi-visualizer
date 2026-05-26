import json
from typing import List
from dataclasses import dataclass, field
import pretty_midi
from common import Color, RGB
from models.track import Track
from models.note import Note
from models.render_format import RenderFormat
from models.resolution import Resolution

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
    # filepaths
    audio_filepath: str = ""

    # export details
    export_dir: str = ""
    export_filename: str = ""
    export_format: RenderFormat | None = None
    export_resolution: Resolution | None = None

    # midi data
    tracks: List[Track] = field(default_factory=list)

    # properties
    track_name: str = ""
    bg_color: RGB = Color.DARKEST_GRAY
    playhead_pos: float = 0.5 # % of screen width playhead's located at - 0 to 1
    vertical_padding_ratio = 0.15 # ratio of vertical compression of midi area - 0 to 1 (1 is maximally crunched)
    vertical_offset_ratio = 0 # ratio of vertical offset positioning - -1 to 1 (-1 is top, 0 center, 1 bottom)
    fps: int = 60
    
    @staticmethod
    def create_from_midi_data(track_name: str, midi_data: pretty_midi.PrettyMIDI) -> None:
        vis_config = VisConfig(track_name=track_name)

        instruments: List[pretty_midi.Instrument] = midi_data.instruments

        inst_names = set()
        for inst in instruments:
            if not inst.name:
                print("VisConfig | Warning: Loaded instrument from MIDI data with no name - skipping")
                continue

            if inst.name in inst_names:
                print(f"VisConfig | Warning: Loaded instrument with duplicate name \"{inst.name}\" - skipping")
                continue

            track = Track.create_from_midi_data(inst)
            vis_config.tracks.append(track)
            inst_names.add(inst.name)

        return vis_config
    
    @staticmethod
    def update_from_midi_data(midi_data: pretty_midi.PrettyMIDI) -> None:
        # TODO
        # Updates an existing config's track and note data from a provided
        # midi track - useful for updating underlying midi data for a track 
        # without losing existing config settings.
        # 1) Remove any tracks that don't exist in update
        # 2) Add any new tracks that only exist in update
        # 3) Update existing tracks that still exist with refreshed note data
        pass

    def save(self, path: str) -> None:
        print(f'VisConfig | Saving config at "{path}"')

        data = {
            "schemaVersion": VIS_CONFIG_SCHEMA_VERSION,
            "audioFilepath": self.audio_filepath,

            "exportDir": self.export_dir,
            "exportFilename": self.export_filename,
            "exportFormat": self.export_format.name if self.export_format else None,
            "exportResolution": self.export_resolution.name if self.export_resolution else None,

            "trackName": self.track_name,
            "bgColor": list(self.bg_color),
            "verticalPaddingRatio": self.vertical_padding_ratio,
            "verticalOffsetRatio": self.vertical_offset_ratio,
            "playheadPos": self.playhead_pos,
            "fps": self.fps,

            "tracks": [
                track.save()
                for track in self.tracks
            ]
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load(path: str) -> VisConfig:
        print(f'VisConfig | Loading config at "{path}"')

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema_version = data.get("schemaVersion", 1)

        config = VisConfig()

        config.audio_filepath = data.get("audioFilepath", "")
        config.export_dir = data.get("exportDir", "")
        config.export_filename = data.get("exportFilename", "")

        export_format = data.get("exportFormat")
        config.export_format = (RenderFormat[export_format] if export_format else None)

        export_resolution = data.get("exportResolution")
        config.export_resolution = (Resolution[export_resolution] if export_resolution else None )

        config.track_name = data.get("trackName", "")
        config.bg_color = tuple(data.get("bgColor", [0, 0, 0]))
        config.vertical_padding_ratio = data.get("verticalPaddingRatio", 0.0)
        config.vertical_offset_ratio = data.get("verticalOffsetRatio", 0.0)
        config.playhead_pos = data.get("playheadPos", 0.5)
        config.fps = data.get("fps", 60)

        config.tracks = [
            Track.load(track_data)
            for track_data in data.get("tracks", [])
        ]

        return config

    # Loads in all note data from midi (assumes tracks are already defined)
    def populate_notes_from_midi_data(self, midi_data: pretty_midi.PrettyMIDI):
        instruments: List[pretty_midi.Instrument] = midi_data.instruments

        for inst in instruments:
            # ensure loaded instrument has a name - we use it for track indexing
            if not inst.name:
                print("VisConfig | Warning: Loaded instrument from MIDI data with no name - skipping")
                continue

            # get corresponding track by instrument name
            track = self.get_track_by_name(inst.name)
            if track == None:
                print(f"VisConfig | Warning: Loaded instrument {inst.name} from MIDI data with no match in VisConfig tracks - skipping")
                continue

            track.notes = []
            for note in inst.notes:
                track.notes.append(Note(note.pitch, note.velocity, note.start, note.end))

    # Getters

    def get_track_by_name(self, name: str) -> Track:
        return next((track for track in self.tracks if track.name == name), None)
    
    def get_min_pitch(self) -> int:
        values = [
            note.pitch
            for track in self.tracks
            if track.visible and track.notes
            for note in track.notes
        ]
        return min(values) if values else 0.0

    def get_max_pitch(self) -> int:
        values = [
            note.pitch
            for track in self.tracks
            if track.visible and track.notes
            for note in track.notes
        ]
        return max(values) if values else 0.0
    
    def get_min_time(self) -> float:
        values = [
            note.start
            for track in self.tracks
            if track.visible and track.notes
            for note in track.notes
        ]
        return min(values) if values else 0.0
    
    def get_max_time(self) -> float:
        values = [
            note.end
            for track in self.tracks
            if track.visible and track.notes
            for note in track.notes
        ]
        return max(values) if values else 0.0

    def get_max_sec_across_screen(self) -> float:
        values = [
            track.bar_sec_across_screen
            for track in self.tracks
            if track.visible and track.notes
        ]
        return max(values) if values else 0.0
