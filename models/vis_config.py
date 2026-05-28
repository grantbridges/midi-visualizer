import json
from typing import List
from dataclasses import dataclass, field
import pretty_midi
from common import Color, RGB
from models.track_group import TrackGroup
from models.track import Track
from models.note import Note
from models.render_format import RenderFormat
from models.resolution import Resolution

# ----

'''
History
  1 - Initial version
  2 - Playhead props
  3 - Note playing props
  4 - Track groups
'''
VIS_CONFIG_SCHEMA_VERSION = 4

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

    # properties
    track_name: str = ""
    bg_color: RGB = Color.DARKEST_GRAY
    show_playhead: bool = True
    # ratio of view area width playhead's located at - 0 to 1 (0 is far left, 1 is far right)
    playhead_pos_ratio: float = 0.5 
    playhead_color: RGB = Color.LIGHT_GRAY
    # ratio of vertical compression of midi area - 0 to 1 (1 is maximally crunched)
    vertical_padding_ratio = 0.15 
    # ratio of vertical offset positioning - -1 to 1 (-1 is top, 0 center, 1 bottom)
    vertical_offset_ratio = 0
    fps: int = 60

    # Ratio of distance from playhead to left edge that note will fade out over - 0.01 to 1
    # 1 means fade out over full distance to left edge, 0.5 means fade out to 
    # halfway from playhead to left edge, etc. It makes sense, trust me.
    note_fadeout_ratio: float = 0.5
    note_play_color: RGB = Color.WHITE

    # children
    tracks: List[Track] = field(default_factory=list)
    track_groups: List[TrackGroup] = field(default_factory=list)
    
    @staticmethod
    def create_from_midi_data(track_name: str, midi_data: pretty_midi.PrettyMIDI) -> None:
        vis_config = VisConfig(track_name=track_name)

        instruments: List[pretty_midi.Instrument] = midi_data.instruments

        vis_config.track_groups = []

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
            "showPlayhead": self.show_playhead,
            "playheadPosRatio": self.playhead_pos_ratio,
            "playheadColor": list(self.playhead_color),
            "noteFadeoutRatio": self.note_fadeout_ratio,
            "notePlayColor": list(self.note_play_color),
            "fps": self.fps,

            "trackGroups": [
                track_group.save()
                for track_group in self.track_groups
            ],

            "tracks": [
                track.save()
                for track in self.tracks
            ]
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load(path: str) -> VisConfig:
        try:
            print(f'VisConfig | Loading config at "{path}"')

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            schema_version = data["schemaVersion"]

            config = VisConfig()

            config.audio_filepath = data["audioFilepath"]
            config.export_dir = data["exportDir"]
            config.export_filename = data["exportFilename"]
            config.export_format = RenderFormat[data["exportFormat"]]
            config.export_resolution = Resolution[data["exportResolution"]]

            config.track_name = data["trackName"]
            config.bg_color = tuple(data["bgColor"])
            config.vertical_padding_ratio = data["verticalPaddingRatio"]
            config.vertical_offset_ratio = data["verticalOffsetRatio"]
            config.playhead_pos_ratio = data["playheadPosRatio"]
            config.fps = data["fps"]

            config.tracks = [
                Track.load(track_data, schema_version)
                for track_data in data["tracks"]
            ]

            if schema_version >= 2:
                config.show_playhead = data["showPlayhead"]
                config.playhead_color = data["playheadColor"]

            if schema_version >= 3:
                config.note_fadeout_ratio = data["noteFadeoutRatio"]
                config.note_play_color = data["notePlayColor"]

            if schema_version >= 4:
                config.track_groups = [
                    TrackGroup.load(track_data, schema_version)
                    for track_data in data["trackGroups"]
                ]

            return config
        except Exception as ex:
            print(f"VisConfig | Error while loading config: {str(ex)}")
            return None

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
