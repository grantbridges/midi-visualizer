from typing import List

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QDialogButtonBox,
)

from common.colors import Color
from models import Track, TrackGroup, VisConfig
from ui.common import LayoutUtil, ColorButton, WidgetUtil
from utility import Util

class GroupTracksDialog(QDialog):
    def __init__(self, selected_tracks: List[Track], vis_config: VisConfig, parent=None):
        super().__init__(parent)

        self.tracks = selected_tracks
        self.vis_config = vis_config

        self.setWindowTitle("Create Track Group")

        self.setModal(True)

        self.setFixedSize(360, 160)

        # -- Create Controls --

        track_names = ", ".join(track.name for track in self.tracks)
        track_names = Util.truncate(track_names, 100)
        description = WidgetUtil.hint_label(f"Create track group for {track_names}")

        # for a new group
        self.name_input = QLineEdit(text="New Group")
        self.color_input = ColorButton(Color.KAYLA_1)

        button_box = QDialogButtonBox()
        button_box.addButton("Cancel", QDialogButtonBox.RejectRole)
        apply_button = button_box.addButton("Create", QDialogButtonBox.AcceptRole)
        apply_button.setDefault(True)
        apply_button.setAutoDefault(True)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # -- Layout Controls --

        column = QVBoxLayout(self)

        LayoutUtil.label(column, description)

        LayoutUtil.line_edit(column, "Name", self.name_input)
        LayoutUtil.button(column, "Color", self.color_input)

        LayoutUtil.dialog_button_box(column, button_box)

        self.name_input.setFocus()

    # getters

    def get_track_group(self) -> TrackGroup:
        name = self.name_input.text().strip() or "New Group"

        return TrackGroup(
            name=name,
            color=self.color_input.getColor(),
        )