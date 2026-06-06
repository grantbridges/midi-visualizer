import json
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
  7 - Bg details, play audio flag, & time overrides
'''
VIS_CONFIG_SCHEMA_VERSION = 7

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

    # -- Audio --
    play_audio: bool = True
    audio_filepath: str = ""

    # -- Export Props --
    export_dir: str = ""
    export_filename: str = ""
    export_format: RenderFormat = RenderFormat.MP4
    export_resolution: Resolution = Resolution.FullHD

    # -- Display Props --
    show_playhead: bool = True
    # ratio of view area width playhead's located at - 0 to 1 (0 is far left, 1 is far right)
    playhead_pos_ratio: float = 0.5 
    playhead_color: RGB = Color.LIGHT_GRAY
    # ratio of vertical compression of midi area - 0 to 1 (1 is maximally crunched)
    vertical_padding_ratio = 0.15 
    # ratio of vertical offset positioning - -1 to 1 (-1 is top, 0 center, 1 bottom)
    vertical_offset_ratio = 0
    # Ratio of distance from playhead to left edge that note will fade out over - 0.01 to 1
    # 1 means fade out over full distance to left edge, 0.5 means fade out to 
    # halfway from playhead to left edge, etc. It makes sense, trust me.
    note_fadeout_ratio: float = 0.5
    note_play_color: RGB = Color.WHITE

    # -- Pitch Range --
    auto_calc_pitch_bounds: bool = True
    manual_pitch_min: int = 0
    manual_pitch_max: int = 127

    # -- Time Range --
    auto_calc_time_range: bool = True
    manual_start_time: float = 0.0
    manual_end_time: float = 1.0

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
            "schemaVersion": VIS_CONFIG_SCHEMA_VERSION,
            "trackName": self.track_name,
            "fps": self.fps,

            "bgMode": self.bg_mode.name,
            "bgColor": list(self.bg_color),
            "bgImageFilepath": self.bg_image_filepath,
            "bgVideoFilepath": self.bg_video_filepath,

            "playAudio": self.play_audio,
            "audioFilepath": self.audio_filepath,

            "exportDir": self.export_dir,
            "exportFilename": self.export_filename,
            "exportFormat": self.export_format.name,
            "exportResolution": self.export_resolution.name,

            "showPlayhead": self.show_playhead,
            "playheadPosRatio": self.playhead_pos_ratio,
            "playheadColor": list(self.playhead_color),
            "verticalPaddingRatio": self.vertical_padding_ratio,
            "verticalOffsetRatio": self.vertical_offset_ratio,
            "noteFadeoutRatio": self.note_fadeout_ratio,
            "notePlayColor": list(self.note_play_color),
            "autoCalcPitchBounds": self.auto_calc_pitch_bounds,
            "manualPitchMin": self.manual_pitch_min,
            "manualPitchMax": self.manual_pitch_max,
            "autoCalcTimeRange": self.auto_calc_time_range,
            "manualStartTime": self.manual_start_time,
            "manualEndTime": self.manual_end_time,

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
            print(f'VisConfig | Loading config from "{path}"')

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            schema_version = data["schemaVersion"]

            config = VisConfig()

            config.track_name = data["trackName"]
            config.fps = data["fps"]

            config.bg_color = tuple(data["bgColor"])
            
            config.audio_filepath = data["audioFilepath"]

            config.export_dir = data["exportDir"]
            config.export_filename = data["exportFilename"]
            config.export_format = RenderFormat[data["exportFormat"]]
            config.export_resolution = Resolution[data["exportResolution"]]

            config.vertical_padding_ratio = data["verticalPaddingRatio"]
            config.vertical_offset_ratio = data["verticalOffsetRatio"]
            config.playhead_pos_ratio = data["playheadPosRatio"]

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

            if schema_version >= 6:
                config.auto_calc_pitch_bounds = data["autoCalcPitchBounds"]
                config.manual_pitch_min = data["manualPitchMin"]
                config.manual_pitch_max = data["manualPitchMax"]

            if schema_version >= 7:
                config.bg_mode = BackgroundMode[data["bgMode"]]
                config.bg_image_filepath = tuple(data["bgImageFilepath"])
                config.bg_video_filepath = tuple(data["bgVideoFilepath"])

                config.play_audio = data["playAudio"]

                config.auto_calc_time_range = data["autoCalcTimeRange"]
                config.manual_start_time = data["manualStartTime"]
                config.manual_end_time = data["manualEndTime"]

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
        if not self.auto_calc_time_range:
            return self.manual_start_time
        
        return self.get_calculated_min_time()
    
    def get_calculated_min_time(self) -> float:
        values = [
            track.time_min
            for track in self.get_visible_tracks()
        ]
        return min(values) if values else 0.0
    
    def get_max_time(self) -> float:
        if not self.auto_calc_time_range:
            return self.manual_end_time
        
        return self.get_calculated_max_time()

    def get_calculated_max_time(self) -> float:
        values = [
            track.time_max
            for track in self.get_visible_tracks()
        ]
        return max(values) if values else 1.0

    def get_max_sec_across_screen(self) -> float:
        values = [
            tg.bar_sec_across_screen
            for tg in self.track_groups
            if tg.visible
        ]
        return max(values) if values else 0.0

    # Helpers

    def _build_track_groups_cache(self):
        self._track_groups_dict = {
            group.group_id: group
            for group in self.track_groups
        }