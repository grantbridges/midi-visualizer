from dataclasses import dataclass, field
from uuid import UUID, uuid4
from common import Color, RGB

# ----

'''
A Track Group holds a group of midi tracks for bulk formatting.
'''
@dataclass
class TrackGroup:
    group_id: UUID = field(default_factory=uuid4)
    name: str = 'Group 1'
    visible: bool = True
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    # 0 - 1, ratio of screen height
    bar_height_ratio: float = .05 
    # seconds for bar to fully cross screen
    bar_sec_across_screen: float = 2 
    # ratio of vertical compression of midi area - 0 to 1 (1 is maximally crunched)
    vertical_padding_ratio: float = 0.15 
    # ratio of vertical offset positioning - -1 to 1 (-1 is top, 0 center, 1 bottom)
    vertical_offset_ratio: float = 0.0

    def save(self) -> dict:
        return {
            "id": str(self.group_id),
            "name": self.name,
            "visible": self.visible,
            "color": list(self.color),
            "alpha": self.alpha,
            "barHeightRatio": self.bar_height_ratio,
            "barSecAcrossScreen": self.bar_sec_across_screen,
            "verticalPaddingRatio": self.vertical_padding_ratio,
            "verticalOffsetRatio": self.vertical_offset_ratio,
        }
    
    @staticmethod
    def load(data: dict, schema_version: int) -> TrackGroup:
        track_group = TrackGroup()

        track_group.group_id = UUID(data["id"])
        track_group.name = data["name"]
        track_group.visible = data["visible"]
        track_group.color = tuple(data["color"])
        track_group.alpha = data["alpha"]
        track_group.bar_height_ratio = data["barHeightRatio"]
        track_group.bar_sec_across_screen = data["barSecAcrossScreen"]
        track_group.vertical_padding_ratio = data["verticalPaddingRatio"]
        track_group.vertical_offset_ratio = data["verticalOffsetRatio"]

        return track_group
