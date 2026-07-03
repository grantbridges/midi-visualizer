from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDialogButtonBox,
)
from common.colors import Color
from models import Track, TrackGroup
from ui.common import LayoutUtil, ColorButton, WidgetUtil

class CreateGroupDialog(QDialog):
    def __init__(self, tracks: List[Track], parent=None):
        super().__init__(parent)

        self.tracks = tracks

        self.setWindowTitle("Create Group")
        self.setModal(True)

        # -- Create Controls --

        track_names = ", ".join(track.name for track in self.tracks)
        description = WidgetUtil.hint_label(f"Create group for selected tracks ({track_names}).")

        self.name_input = QLineEdit(text="New Group")
        self.color_input = ColorButton(Color.KAYLA_1)

        button_box = QDialogButtonBox()
        cancel_button = button_box.addButton("Cancel", QDialogButtonBox.RejectRole)
        create_button = button_box.addButton("Create", QDialogButtonBox.AcceptRole)
        create_button.setDefault(True)
        create_button.setAutoDefault(True)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # -- Layout Controls --

        column = QVBoxLayout(self)
        LayoutUtil.label(column, description)
        LayoutUtil.line_edit(column, "Name", self.name_input)
        LayoutUtil.button(column, "Color", self.color_input)
        LayoutUtil.dialog_button_box(column, button_box)

    def get_track_group(self) -> TrackGroup:
        return TrackGroup(
            name = self.name_input.text().strip(),
            color = self.color_input.getColor()
        )