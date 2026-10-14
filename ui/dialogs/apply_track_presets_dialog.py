from dataclasses import dataclass
from enum import StrEnum

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox, 
    QDialog, 
    QDialogButtonBox, 
    QHBoxLayout, 
    QHeaderView, 
    QLabel, 
    QPushButton, 
    QTableWidget, 
    QTableWidgetItem, 
    QVBoxLayout
)
from common import Color
from ui.common import WidgetUtil, Icons, LayoutUtil, TableComboBox
from models import presets_config, Track, TrackPreset, VisConfig
from utility.q_util import QUtil

import logging
logger = logging.getLogger("ApplyTrackPresetsDialog")

# UI Model for metadata about current tracks
@dataclass
class UITrack:
    name: str = ''
    existing_preset: TrackPreset | None = None
    preset_to_apply: TrackPreset | None = None

    @staticmethod
    def create(track: Track):
        return UITrack(
            name = track.name,
            existing_preset = None,
            preset_to_apply = None
        )

class ApplyTrackPresetsDialog(QDialog):
    def __init__(self, vis_config: VisConfig, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"Apply Track Presets")

        self.vis_config = vis_config

        self.setModal(True)
        self.setFixedSize(600, 600)

        # -- Initialize UI Models --
        self.tracks: list[UITrack] = [
            UITrack.create(t) for t in vis_config.tracks
        ]

        # -- Create Controls --

        info_label = WidgetUtil.info_text(f"Select track presets to copy values from. Tracks with \"None\" selected will have no updates applied.")

        # tracks table
        self.tracks_columns = ["Name", "Preset", "Pitch Min", "Pitch Max"]
        self.table = QTableWidget(0, len(self.tracks_columns))
        self.table.setHorizontalHeaderLabels(self.tracks_columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # disable selection
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.changes_label = QLabel()
        self.changes_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        font = self.changes_label.font()
        font.setPointSizeF(font.pointSizeF() * 0.9)
        self.changes_label.setFont(font)

        button_box = QDialogButtonBox()
        button_box.addButton("Cancel", QDialogButtonBox.RejectRole)
        apply_button = button_box.addButton("Save", QDialogButtonBox.AcceptRole)
        apply_button.setDefault(True)
        apply_button.setAutoDefault(True)

        button_box.accepted.connect(self._save)
        button_box.rejected.connect(self.reject)

        # -- Layout Controls --

        main_layout = QVBoxLayout(self)

        main_layout.addWidget(info_label)
        main_layout.addSpacing(5)

        # tracks table
        tracks_layout = QHBoxLayout()
        tracks_layout.addWidget(self.table)

        main_layout.addLayout(tracks_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.changes_label, 1)
        bottom_layout.addWidget(button_box)

        main_layout.addLayout(bottom_layout)

        self._refresh_ui()

    def _refresh_changes_label(self):
        updated_count = sum(1 for t in self.tracks if t.preset_to_apply is not None)

        text = ""
        if updated_count > 0:
            text = f"{updated_count} preset{"s" if updated_count > 1 else ""} applied"

        self.changes_label.setText(text)

    def _refresh_ui(self):
        self.table.setRowCount(len(self.tracks))
        for row in range(len(self.tracks)):
            self._refresh_row(row)

        self._refresh_changes_label()

    def _refresh_row(self, row: int):
        # prevent callbacks while populating table row
        self.table.blockSignals(True)

        track = self.tracks[row]

        col = 0
        
        font = QFont()
        if track.preset_to_apply:
            font.setBold(True)

        # name
        name_item = QTableWidgetItem(track.name)
        name_item.setFont(font)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, col, name_item)
        col += 1

        # presets
        combo = TableComboBox()
        combo.addItem("None", None)
        for p in presets_config.track_presets:
            combo.addItem(p.name, p)

        if track.preset_to_apply is not None:
            index = combo.findData(track.preset_to_apply)
            if index >= 0:
                combo.setCurrentIndex(index)

        combo.currentIndexChanged.connect(lambda index, row=row: self._on_preset_changed(row, index))
        self.table.setCellWidget(row, col, combo)

        col += 1

        # pitch min
        pitch_min_text = "--" if not track.preset_to_apply else f"{track.preset_to_apply.pitch_min}"
        pitch_min_item = QTableWidgetItem(pitch_min_text)
        pitch_min_item.setFont(font)
        pitch_min_item.setFlags(pitch_min_item.flags() & ~Qt.ItemIsEditable)
        pitch_min_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, pitch_min_item)
        col += 1

        # pitch max
        pitch_max_text = "--" if not track.preset_to_apply else f"{track.preset_to_apply.pitch_max}"
        pitch_max_item = QTableWidgetItem(pitch_max_text)
        pitch_max_item.setFont(font)
        pitch_max_item.setFlags(pitch_max_item.flags() & ~Qt.ItemIsEditable)
        pitch_max_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, pitch_max_item)
        col += 1

        # resume callbacks
        self.table.blockSignals(False)

    def _save(self):
        for t in self.tracks:
            preset = t.preset_to_apply
            if not preset:
                continue

            track = self.vis_config.get_track_by_name(t.name)
            if not track:
                logger.warning(f"Unable to find track \"{t.name}\" while saving")
                continue

            track.override_pitch_min_max = True
            track.manual_pitch_min = preset.pitch_min
            track.manual_pitch_max = preset.pitch_max
        
        self.accept()

    def _on_preset_changed(self, row: int, col: int):
        # get selected value from this row
        combo: QComboBox = self.table.cellWidget(row, self.tracks_columns.index("Preset"))
        preset = combo.currentData()

        track = self.tracks[row]
        track.preset_to_apply = preset

        self._refresh_row(row)
        self._refresh_changes_label()