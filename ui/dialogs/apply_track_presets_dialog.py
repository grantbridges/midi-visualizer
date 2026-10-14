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
    QSizePolicy, 
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
    preset_to_apply: TrackPreset | None = None

    @staticmethod
    def create(track: Track):
        return UITrack(
            name = track.name,
            preset_to_apply = None
        )

class ApplyTrackPresetsDialog(QDialog):
    def __init__(self, vis_config: VisConfig, auto_apply_on_open: bool = False, parent=None):
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

        info_label = WidgetUtil.info_text(f"Select track presets to apply. Tracks with \"None\" assigned will not be affected.")

        self.auto_apply_btn = QPushButton("Auto-Assign All")
        self.auto_apply_btn.clicked.connect(self._on_auto_apply_all_presets)

        self.clear_btn = QPushButton("Clear Assignments")
        self.clear_btn.clicked.connect(self._on_clear_selections)

        # tracks table
        self.tracks_columns = ["Name", "Preset", "Pitch Min", "Pitch Max", "", ""]
        self.table = QTableWidget(0, len(self.tracks_columns))
        self.table.setHorizontalHeaderLabels(self.tracks_columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # set whole-row multi-select
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)

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

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.auto_apply_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)
        main_layout.addSpacing(5)

        # tracks table
        tracks_layout = QHBoxLayout()
        tracks_layout.addWidget(self.table)

        main_layout.addLayout(tracks_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.changes_label, 1)
        bottom_layout.addWidget(button_box)

        main_layout.addLayout(bottom_layout)

        if auto_apply_on_open:
            self._on_auto_apply_all_presets()
            # automatically refreshes after applying
        else:
            self._refresh_ui()

    def _refresh_btns(self):
        count = sum(1 for x in self.tracks if x.preset_to_apply)
        self.clear_btn.setEnabled(count > 0)

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
        self._refresh_btns()

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

        combo.currentIndexChanged.connect(lambda _, row=row: self._on_preset_changed(row))
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

        # auto-apply btn
        auto_apply_btn = QPushButton("Auto")
        auto_apply_btn.setStyleSheet("padding: 3px 6px")
        auto_apply_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        auto_apply_btn.clicked.connect(lambda _, row=row: self._on_auto_apply_preset(row))
        self.table.setCellWidget(row, col, LayoutUtil.center(auto_apply_btn))
        col += 1

        # clear button
        clear_btn = QPushButton()
        clear_btn.setIcon(Icons.close_box_outline())
        clear_btn.setEnabled(track.preset_to_apply is not None)
        clear_btn.clicked.connect(lambda _, row=row: self._on_clear_selection(row))
        self.table.setCellWidget(row, col, LayoutUtil.center(clear_btn))
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

    # Callbacks
    def _on_preset_changed(self, row: int):
        # get selected value from this row
        combo: QComboBox = self.table.cellWidget(row, self.tracks_columns.index("Preset"))
        preset = combo.currentData()

        # apply selection to all selected rows
        rows = self._get_selected_rows()
        if row not in rows:
            rows.append(row)

        for r in rows:
            track = self.tracks[r]
            track.preset_to_apply = preset
            self._refresh_row(r)
        
        self._refresh_changes_label()
        self._refresh_btns()

    def _on_auto_apply_all_presets(self):
        for row in range(len(self.tracks)):
            self._auto_apply_preset(row)

        self._refresh_ui()

    def _on_clear_selections(self):
        for track in self.tracks:
            track.preset_to_apply = None

        self._refresh_ui()

    def _on_auto_apply_preset(self, row: int):
        rows = self._get_selected_rows()
        if row not in rows:
            rows.append(row)

        for r in rows:
            self._auto_apply_preset(r)
            self._refresh_row(r)

        self._refresh_changes_label()
        self._refresh_btns()

    def _on_clear_selection(self, row: int):
        rows = self._get_selected_rows()
        if row not in rows:
            rows.append(row)

        for r in rows:
            track = self.tracks[r]
            if track.preset_to_apply:
                track.preset_to_apply = None
                self._refresh_row(r)

        self._refresh_changes_label()
        self._refresh_btns()

    # Getters
    def _get_selected_rows(self) -> list[int]:
        selected_rows: set[int] = set()

        for selection_range in self.table.selectedRanges():
            for row in range(selection_range.topRow(), selection_range.bottomRow() + 1):
                selected_rows.add(row)

        return sorted(selected_rows)

    # Helpers
    def _auto_apply_preset(self, row: int):
        track = self.tracks[row]

        matching_preset = presets_config.get_track_preset(track.name)
        if matching_preset:
            track.preset_to_apply = matching_preset