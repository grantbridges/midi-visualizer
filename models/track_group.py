from dataclasses import dataclass, field
from uuid import UUID, uuid4
from common import Color, RGB

# ----

'''
A Track Group holds a group of midi tracks for bulk formatting
'''
@dataclass
class TrackGroup:
    group_id: UUID = field(default_factory=uuid4)
    name: str = 'Group 1'
    visible: bool = True
    solo: bool = False
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    # 0 - 1, ratio of midi region height
    bar_height_ratio: float = .02
    # seconds for bar to fully cross screen
    bar_sec_across_screen: float = 7.0 
    pitch_offset: int = 0 # -127 - 127
    note_sparks_enabled: bool = True
    note_velocity_fx_enabled: bool = True

    def save(self) -> dict:
        return {
            "id": str(self.group_id),
            "name": self.name,
            "visible": self.visible,
            "solo": self.solo,
            "color": list(self.color),
            "alpha": self.alpha,
            "bar_height_ratio": self.bar_height_ratio,
            "bar_sec_across_screen": self.bar_sec_across_screen,
            "pitch_offset": self.pitch_offset,
            "note_sparks_enabled": self.note_sparks_enabled,
            "note_velocity_fx_enabled": self.note_velocity_fx_enabled,
        }
    
    @staticmethod
    def load(data: dict, schema_version: int) -> TrackGroup:
        track_group = TrackGroup()

        track_group.group_id = UUID(data["id"])
        track_group.name = data["name"]
        track_group.visible = data["visible"]
        track_group.color = tuple(data["color"])
        track_group.alpha = data["alpha"]
        track_group.bar_height_ratio = data["bar_height_ratio"]
        track_group.bar_sec_across_screen = data["bar_sec_across_screen"]

        if schema_version >= 5:
            track_group.pitch_offset = data["pitch_offset"]

        if schema_version >= 12:
            track_group.solo = data["solo"]
            track_group.note_sparks_enabled = data["note_sparks_enabled"]

        if schema_version >= 15:
            track_group.note_velocity_fx_enabled = data["note_velocity_fx_enabled"]

        return track_group
    
    def init(self):
        pass
