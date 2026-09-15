from dataclasses import dataclass

import logging
logger = logging.getLogger("TrackPreset")

# ----

@dataclass
class TrackPreset:
    '''
    A Track Preset holds common track configuration for copying
    between projects
    '''

    name: str = ''
    pitch_min: int = 1
    pitch_max: int = 127

    def save(self) -> dict:
        return {
            "name": self.name,
            "pitch_min": self.pitch_min,
            "pitch_max": self.pitch_max,
        }
    
    @staticmethod
    def load(data: dict, schema_version: int) -> TrackPreset:
        track_preset = TrackPreset()

        track_preset.name = data["name"]
        track_preset.pitch_min = data["pitch_min"]
        track_preset.pitch_max = data["pitch_max"]

        return track_preset