from typing import List
from uuid import UUID

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
    QCheckBox,
    QComboBox,
)

from common.colors import Color
from models import Track, TrackGroup, VisConfig
from ui.common import LayoutUtil, ColorButton, WidgetUtil

class GroupTracksDialog(QDialog):
    def __init__(self, selected_tracks: List[Track], vis_config: VisConfig, parent=None):
        super().__init__(parent)

        self.tracks = selected_tracks
        self.vis_config = vis_config

        self.setWindowTitle("Group Tracks")

        self.setModal(True)

        self.setFixedSize(400, 240)

        # -- Create Controls --

        track_names = ", ".join(track.name for track in self.tracks)
        description = WidgetUtil.hint_label(f"Set group for {track_names}.")

        self.create_new_group_checkbox = QCheckBox()
        self.create_new_group_checkbox.setChecked(True)
        self.create_new_group_checkbox.toggled.connect(lambda _: self._refresh_ui())

        # for a new group
        self.name_input = QLineEdit(text="New Group")
        self.color_input = ColorButton(Color.KAYLA_1)

        # for an existing group
        self.existing_group_combo = QComboBox()
        self.existing_group_combo.addItem("None", None)
        for group in self.vis_config.track_groups:
            self.existing_group_combo.addItem(group.name, str(group.group_id))

        button_box = QDialogButtonBox()
        button_box.addButton("Cancel", QDialogButtonBox.RejectRole)
        apply_button = button_box.addButton("Apply", QDialogButtonBox.AcceptRole)
        apply_button.setDefault(True)
        apply_button.setAutoDefault(True)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # -- Layout Controls --

        column = QVBoxLayout(self)

        LayoutUtil.label(column, description)

        LayoutUtil.checkbox(column, "Create New Group", self.create_new_group_checkbox)
        LayoutUtil.line_edit(column, "Name", self.name_input)
        LayoutUtil.button(column, "Color", self.color_input)
        LayoutUtil.combobox(column, "Existing Group", self.existing_group_combo)

        LayoutUtil.dialog_button_box(column, button_box)

        self._refresh_ui()

    def _refresh_ui(self):
        create_new_group = self.get_create_new_group()

        self.name_input.setEnabled(create_new_group)
        self.color_input.setEnabled(create_new_group)
        self.existing_group_combo.setEnabled(not create_new_group)

    # getters

    def get_create_new_group(self) -> bool:
        return self.create_new_group_checkbox.isChecked()

    def get_track_group(self) -> TrackGroup:
        name = self.name_input.text().strip() or "New Group"

        return TrackGroup(
            name=name,
            color=self.color_input.getColor(),
        )

    def get_selected_group_id(self) -> UUID | None:
        group_id = self.existing_group_combo.currentData()
        return UUID(group_id) if group_id is not None else None