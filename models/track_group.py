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
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    # 0 - 1, ratio of midi region height
    bar_height_ratio: float = .02
    # seconds for bar to fully cross screen
    bar_sec_across_screen: float = 7.0 
    pitch_offset: int = 0 # -127 - 127

    def save(self) -> dict:
        return {
            "id": str(self.group_id),
            "name": self.name,
            "visible": self.visible,
            "color": list(self.color),
            "alpha": self.alpha,
            "bar_height_ratio": self.bar_height_ratio,
            "bar_sec_across_screen": self.bar_sec_across_screen,
            "pitch_offset": self.pitch_offset,
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

        return track_group
    
    def init(self):
        pass
