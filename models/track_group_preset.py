from dataclasses import dataclass

import logging

from common import RGB, Color
logger = logging.getLogger("TrackGroupPreset")

# ----

@dataclass
class TrackGroupPreset:
    '''
    A Track Group Preset holds common track group configuration for copying
    between projects
    '''

    name: str = ''
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    bar_height_ratio: float = .02
    bar_sec_across_screen: float = 7.1
    pitch_offset: int = 0 # -127 - 127
    note_sparks_enabled: bool = True
    note_bounce_enabled: bool = False
    note_velocity_fx_enabled: bool = True

    def save(self) -> dict:
        return {
            "name": self.name,
            "color": list(self.color),
            "alpha": self.alpha,
            "bar_height_ratio": self.bar_height_ratio,
            "bar_sec_across_screen": self.bar_sec_across_screen,
            "pitch_offset": self.pitch_offset,
            "note_sparks_enabled": self.note_sparks_enabled,
            "note_bounce_enabled": self.note_bounce_enabled,
            "note_velocity_fx_enabled": self.note_velocity_fx_enabled,
        }
    
    @staticmethod
    def load(data: dict, schema_version: int) -> TrackGroupPreset:
        track_group_preset = TrackGroupPreset()

        track_group_preset.name = data["name"]
        track_group_preset.color = tuple(data["color"])
        track_group_preset.alpha = data["alpha"]
        track_group_preset.bar_height_ratio = data["bar_height_ratio"]
        track_group_preset.bar_sec_across_screen = data["bar_sec_across_screen"]
        track_group_preset.pitch_offset = data["pitch_offset"]
        track_group_preset.note_sparks_enabled = data["note_sparks_enabled"]
        track_group_preset.note_bounce_enabled = data["note_bounce_enabled"]
        track_group_preset.note_velocity_fx_enabled = data["note_velocity_fx_enabled"]

        return track_group_preset