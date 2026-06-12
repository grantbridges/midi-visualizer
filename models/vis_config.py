import json
from pathlib import Path
from typing import List
from dataclasses import dataclass, field
from uuid import UUID
import pretty_midi
from common import Color, RGB
from models.track_group import TrackGroup
from models.track import Track
from models.note import Note
from models.render_format import RenderFormat
from models.resolution import Resolution
from models.bg_mode import BackgroundMode

# ----

'''
History
  1 - Initial version
  2 - Playhead props
  3 - Note playing props
  4 - Track groups
  5 - Track group pitch offsets
  6 - Auto-calc pitch bounds & manual values
  7 - BG details, play audio flag, & time offsets
  8 - BG video props
  9 - Fade In/Out; Playhead thickness and alpha
  10 - Note glow
  11 - Note highlight
'''
VIS_CONFIG_SCHEMA_VERSION = 11

'''
Top level construct containing all visualizing info
'''
@dataclass
class VisConfig:
    # -- Track Props --
    track_name: str = ""
    fps: int = 60

    # -- Background Props --
    bg_mode: BackgroundMode = BackgroundMode.Color
    bg_color: RGB = Color.DARKEST_GRAY
    bg_image_filepath: str = ""
    bg_video_filepath: str = ""

    # -- Video Props --
    bg_video_time_offset: float = 0.0
    bg_video_loop: bool = False

    # -- Audio --
    play_audio: bool = True
    audio_filepath: str = ""

    # -- Export Props --
    export_dir: str = ""
    export_filename: str = ""
    export_format: RenderFormat = RenderFormat.MP4
    export_resolution: Resolution = Resolution.FullHD

    # -- Playhead Props --
    show_playhead: bool = True
    # ratio of view area width playhead's located at - 0 to 1 (0 is far left, 1 is far right)
    playhead_pos_ratio: float = 0.5 
    playhead_color: RGB = Color.LIGHT_GRAY
    playhead_alpha: int = 255
    playhead_thickness_ratio: float = .001
    # ratio of vertical compression of midi area - 0 to 1 (1 is maximally crunched)
    vertical_padding_ratio = 0.15 
    # ratio of vertical offset positioning - -1 to 1 (-1 is top, 0 center, 1 bottom)
    vertical_offset_ratio = 0
    # Ratio of distance from playhead to left edge that note will fade out over - 0.01 to 1
    # 1 means fade out over full distance to left edge, 0.5 means fade out to 
    # halfway from playhead to left edge, etc. It makes sense, trust me.
    note_fadeout_ratio: float = 0.5

    # -- Note Glow --
    note_glow_enabled: bool = True
    note_glow_size: float = 0.8 # ratio of computed bar height - applies to y padding
    note_glow_intensity: float = 0.33

    # -- Note Highlight --
    note_highlight_enabled: bool = True
    note_highlight_intensity: float = 0.75 # ratio on alpha

    # -- Fade In --
    fade_in_enabled: bool = False
    fade_in_color: bool = Color.BLACK
    fade_in_time: float = 1.0 # sec
    fade_out_enabled: bool = False
    fade_out_color: bool = Color.BLACK
    fade_out_time: float = 1.0 # sec

    # -- Pitch Range --
    auto_calc_pitch_bounds: bool = True
    manual_pitch_min: int = 0
    manual_pitch_max: int = 127

    # -- Time Range --
    apply_time_offsets: bool = True
    start_time_offset: float = 0.0
    end_time_offset: float = 1.0

    # children
    tracks: List[Track] = field(default_factory=list)
    track_groups: List[TrackGroup] = field(default_factory=list)

    # cache of track groups for quick lookup
    _track_groups_dict: dict[UUID, TrackGroup] = field(default_factory=dict)
    
    @staticmethod
    def create_from_midi_data(track_name: str, midi_data: pretty_midi.PrettyMIDI) -> None:
        vis_config = VisConfig(track_name=track_name)

        instruments: List[pretty_midi.Instrument] = midi_data.instruments

        # seed initial track group
        track_group = TrackGroup()
        vis_config.track_groups = [track_group]

        inst_names = set()
        for inst in instruments:
            if not inst.name:
                print("VisConfig | Warning: Loaded track from MIDI data with no name - skipping")
                continue

            if inst.name in inst_names:
                print(f"VisConfig | Warning: Loaded track with duplicate name \"{inst.name}\" - skipping")
                continue

            track = Track.create_from_midi_data(inst)
            if len(track.notes) == 0:
                print(f"VisConfig | Warning: Loaded track with no notes \"{inst.name}\" - skipping")
                continue

            track.group_id = track_group.group_id
            vis_config.tracks.append(track)
            inst_names.add(inst.name)

        return vis_config

    def save(self, path: str) -> None:
        print(f'VisConfig | Saving config to "{path}"')

        data = {
            "schema_version": VIS_CONFIG_SCHEMA_VERSION,
            "track_name": self.track_name,
            "fps": self.fps,

            "bg_mode": self.bg_mode.name,
            "bg_color": list(self.bg_color),
            "bg_image_filepath": self.bg_image_filepath,
            "bg_video_filepath": self.bg_video_filepath,

            "bg_video_time_offset": self.bg_video_time_offset,
            "bg_video_loop": self.bg_video_loop,

            "play_audio": self.play_audio,
            "audio_filepath": self.audio_filepath,

            "export_dir": self.export_dir,
            "export_filename": self.export_filename,
            "export_format": self.export_format.name,
            "export_resolution": self.export_resolution.name,

            "show_playhead": self.show_playhead,
            "playhead_pos_ratio": self.playhead_pos_ratio,
            "playhead_color": list(self.playhead_color),
            "playhead_alpha": self.playhead_alpha,
            "playhead_thickness_ratio": self.playhead_thickness_ratio,

            "vertical_padding_ratio": self.vertical_padding_ratio,
            "vertical_offset_ratio": self.vertical_offset_ratio,
            "note_fadeout_ratio": self.note_fadeout_ratio,

            "note_glow_enabled": self.note_glow_enabled,
            "note_glow_size": self.note_glow_size,
            "note_glow_intensity": self.note_glow_intensity,
            "note_highlight_enabled": self.note_highlight_enabled,
            "note_highlight_intensity": self.note_highlight_intensity,

            "fade_in_enabled": self.fade_in_enabled,
            "fade_in_color": list(self.fade_in_color),
            "fade_in_time": self.fade_in_time,
            "fade_out_enabled": self.fade_out_enabled,
            "fade_out_color": list(self.fade_out_color),
            "fade_out_time": self.fade_out_time,

            "auto_calc_pitch_bounds": self.auto_calc_pitch_bounds,
            "manual_pitch_min": self.manual_pitch_min,
            "manual_pitch_max": self.manual_pitch_max,
            "apply_time_offsets": self.apply_time_offsets,
            "start_time_offset": self.start_time_offset,
            "end_time_offset": self.end_time_offset,

            "track_groups": [
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
            print(f'VisConfig | Loading config from "{path}"')

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            schema_version = data["schema_version"]

            config = VisConfig()

            config.track_name = data["track_name"]
            config.fps = data["fps"]

            config.bg_color = tuple(data["bg_color"])
            
            config.audio_filepath = data["audio_filepath"]

            config.export_dir = data["export_dir"]
            config.export_filename = data["export_filename"]
            config.export_format = RenderFormat[data["export_format"]]
            config.export_resolution = Resolution[data["export_resolution"]]

            config.vertical_padding_ratio = data["vertical_padding_ratio"]
            config.vertical_offset_ratio = data["vertical_offset_ratio"]
            config.playhead_pos_ratio = data["playhead_pos_ratio"]

            config.tracks = [
                Track.load(track_data, schema_version)
                for track_data in data["tracks"]
            ]

            if schema_version >= 2:
                config.show_playhead = data["show_playhead"]
                config.playhead_color = data["playhead_color"]

            if schema_version >= 3:
                config.note_fadeout_ratio = data["note_fadeout_ratio"]

            if schema_version >= 4:
                config.track_groups = [
                    TrackGroup.load(track_data, schema_version)
                    for track_data in data["track_groups"]
                ]

            if schema_version >= 6:
                config.auto_calc_pitch_bounds = data["auto_calc_pitch_bounds"]
                config.manual_pitch_min = data["manual_pitch_min"]
                config.manual_pitch_max = data["manual_pitch_max"]

            if schema_version >= 7:
                config.bg_mode = BackgroundMode[data["bg_mode"]]
                config.bg_image_filepath = data["bg_image_filepath"]
                config.bg_video_filepath = data["bg_video_filepath"]

                config.play_audio = data["play_audio"]

                config.apply_time_offsets = data["apply_time_offsets"]
                config.start_time_offset = data["start_time_offset"]
                config.end_time_offset = data["end_time_offset"]

            if schema_version >= 8:
                config.bg_video_time_offset = data["bg_video_time_offset"]
                config.bg_video_loop = data["bg_video_loop"]

            if schema_version >= 9:
                config.playhead_alpha = data["playhead_alpha"]
                config.playhead_thickness_ratio = data["playhead_thickness_ratio"]
                config.fade_in_enabled = data["fade_in_enabled"]
                config.fade_in_color = tuple(data["fade_in_color"])
                config.fade_in_time = data["fade_in_time"]
                config.fade_out_enabled = data["fade_out_enabled"]
                config.fade_out_color = tuple(data["fade_out_color"])
                config.fade_out_time = data["fade_out_time"]

            if schema_version >= 10:
                config.note_glow_enabled = data["note_glow_enabled"]
                config.note_glow_size = data["note_glow_size"]
                config.note_glow_intensity = data["note_glow_intensity"]

            if schema_version >= 11:
                config.note_highlight_enabled = data["note_highlight_enabled"]
                config.note_highlight_intensity = data["note_highlight_intensity"]

            return config
        except Exception as ex:
            print(f"VisConfig | Error while loading config: {str(ex)}")
            return None
        
    def init(self):
        for tg in self.track_groups:
            tg.init()

        self._build_track_groups_cache()

        # remove loaded tracks that have no notes
        for i in reversed(range(len(self.tracks))):
            track = self.tracks[i]
            if len(track.notes) == 0:
                print(f"VisConfig | Init | Track \"{track.name}\" has no notes - removing from config")
                self.tracks.pop(i)
        
        for t in self.tracks:
            t.init()

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


    def update_track_groups(self, new_groups: List[TrackGroup]):
        # copy our ui model back to vis config
        self.track_groups = new_groups

        self._build_track_groups_cache()

        # if any tracks are using removed group ids, clear them out
        for t in self.tracks:
            if t.group_id is not None:
                group = self.get_track_group_by_id(t.group_id)
                if group is None:
                    t.group_id = None
    # Getters

    def get_track_group_by_id(self, group_id: UUID) -> TrackGroup | None:
        return self._track_groups_dict.get(group_id)
    
    def get_tracks_by_group_id(self, group_id: UUID) -> List[Track]:
        return [track for track in self.tracks if track.group_id == group_id]

    def get_track_by_name(self, name: str) -> Track:
        return next((track for track in self.tracks if track.name == name), None)
    
    def get_visible_tracks(self) -> List[Track]:
        tracks = []
        for tg in self.track_groups:
            if tg.visible:
                tracks.extend(
                    self.get_tracks_by_group_id(tg.group_id)
                )

        return tracks
    
    def get_min_pitch(self) -> int:
        if not self.auto_calc_pitch_bounds:
            return self.manual_pitch_min

        return self.get_calculated_min_pitch()

    def get_calculated_min_pitch(self) -> int:
        values = []

        for group in self.track_groups:
            if not group.visible:
                continue

            for track in self.get_tracks_by_group_id(group.group_id):
                values.append(track.pitch_min + group.pitch_offset)

        return min(values) if values else 0
    
    def get_min_pitch_for_track_group(self, group_id: UUID, exclude_offset: int = False) -> int:
        group = self.get_track_group_by_id(group_id)
        values = [
            track.pitch_min + (group.pitch_offset if not exclude_offset else 0)
            for track in self.get_tracks_by_group_id(group_id)
        ]
        return min(values) if values else 0

    def get_max_pitch(self) -> int:
        if not self.auto_calc_pitch_bounds:
            return self.manual_pitch_max
        
        return self.get_calculated_max_pitch()

    def get_calculated_max_pitch(self) -> int:
        values = []

        for group in self.track_groups:
            if not group.visible:
                continue

            for track in self.get_tracks_by_group_id(group.group_id):
                values.append(track.pitch_max + group.pitch_offset)

        return max(values) if values else 0
    
    def get_max_pitch_for_track_group(self, group_id: UUID, exclude_offset: int = False) -> int:
        group = self.get_track_group_by_id(group_id)
        values = [
            track.pitch_max + (group.pitch_offset if not exclude_offset else 0)
            for track in self.get_tracks_by_group_id(group_id)
        ]
        return max(values) if values else 0
    
    def get_min_time(self) -> float:
        values = [
            track.time_min
            for track in self.get_visible_tracks()
        ]
        offset = self.start_time_offset if self.apply_time_offsets else 0.0
        return min(values) + offset if values else 0.0
    
    def get_max_time(self) -> float:
        values = [
            track.time_max
            for track in self.get_visible_tracks()
        ]
        offset = self.end_time_offset if self.apply_time_offsets else 0.0
        return max(values) + offset if values else 1.0

    def get_max_sec_across_screen(self) -> float:
        values = [
            tg.bar_sec_across_screen
            for tg in self.track_groups
            if tg.visible
        ]
        return max(values) if values else 0.0
    
    def get_exported_filepath(self) -> Path:
        return Path(self.export_dir) / f"{self.export_filename}.{self.export_format.value}"

    # Helpers

    def _build_track_groups_cache(self):
        self._track_groups_dict = {
            group.group_id: group
            for group in self.track_groups
        }