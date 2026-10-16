from dataclasses import dataclass, field
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
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
from common import RGB, Color
from ui.common import WidgetUtil, Icons, LayoutUtil, ColorButton, TableCheckBox
from models import presets_config, TrackGroup, TrackGroupPreset, VisConfig
from utility import Util

import logging
logger = logging.getLogger("AddTrackGroupPresetsDialog")

# UI Model for metadata about presets
@dataclass
class UITrackGroupPreset:
    name: str = 'Default'
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    bar_height_ratio: float = .02
    bar_sec_across_screen: float = 7.1
    pitch_offset: int = 0
    note_sparks_enabled: bool = True
    note_bounce_enabled: bool = False
    note_velocity_fx_enabled: bool = True

    selected_to_add: bool = False

    @staticmethod
    def create(preset: TrackGroupPreset) -> UITrackGroupPreset:
        return UITrackGroupPreset(
            name = preset.name,
            color = preset.color,
            alpha = preset.alpha,
            bar_height_ratio = preset.bar_height_ratio,
            bar_sec_across_screen = preset.bar_sec_across_screen,
            pitch_offset = preset.pitch_offset,
            note_sparks_enabled = preset.note_sparks_enabled,
            note_bounce_enabled = preset.note_bounce_enabled,
            note_velocity_fx_enabled = preset.note_velocity_fx_enabled,
            selected_to_add = False
        )

    def to_track_group(self) -> TrackGroup:
        return TrackGroup(
            name = self.name,
            color = self.color,
            alpha = self.alpha,
            bar_height_ratio = self.bar_height_ratio,
            bar_sec_across_screen = self.bar_sec_across_screen,
            pitch_offset = self.pitch_offset,
            note_sparks_enabled = self.note_sparks_enabled,
            note_bounce_enabled = self.note_bounce_enabled,
            note_velocity_fx_enabled = self.note_velocity_fx_enabled,
        )

class AddTrackGroupPresetsDialog(QDialog):
    def __init__(self, vis_config: VisConfig, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"Add Track Groups from Presets")

        self.vis_config = vis_config

        self.setModal(True)
        min_width, min_height = 600, 400
        self.setMinimumSize(min_width, min_height)
        self.resize(min_width, min_height)

        # -- Initialize UI Models --
        self.track_group_presets: list[UITrackGroupPreset] = [
            UITrackGroupPreset.create(p) for p in presets_config.track_group_presets
        ]

        # -- Create Controls --

        info_label = WidgetUtil.info_text(f"Select track groups to create from presets.")

        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self._on_select_all)

        self.clear_btn = QPushButton("Clear Selections")
        self.clear_btn.clicked.connect(self._on_clear_selections)

        # tracks group presets table
        self.columns = ["", "", "Name", "Color", "Opacity", "Note\nSparks", "Note\nBounce", "Note\nVel. Fx", "Bar\nHeight", "Speed", "Pitch\nOffset"]
        self.table = QTableWidget(0, len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().resizeSection(1, 40) # status column
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch) # name column
        self.table.verticalHeader().setVisible(False) # hide row numbers
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
        self.apply_button = button_box.addButton("Add", QDialogButtonBox.AcceptRole)
        self.apply_button.setDefault(True)
        self.apply_button.setAutoDefault(True)

        button_box.accepted.connect(self._save)
        button_box.rejected.connect(self.reject)

        # -- Layout Controls --

        main_layout = QVBoxLayout(self)

        main_layout.addWidget(info_label)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.select_all_btn)
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

        self._refresh_ui()

    def _refresh_btns(self):
        count = sum(1 for tg in self.track_group_presets if tg.selected_to_add)
        self.select_all_btn.setEnabled(count < len(self.track_group_presets))
        self.clear_btn.setEnabled(count > 0)
        self.apply_button.setEnabled(count > 0)

    def _refresh_changes_label(self):
        added_count = sum(1 for tg in self.track_group_presets if tg.selected_to_add)

        text = ""
        if added_count > 0:
            text = f"{added_count} preset{"s" if added_count > 1 else ""} selected"

        self.changes_label.setText(text)

    def _refresh_ui(self):
        self.table.setRowCount(len(self.track_group_presets))
        for row in range(len(self.track_group_presets)):
            self._refresh_row(row)

        self._refresh_changes_label()
        self._refresh_btns()

    def _refresh_row(self, row: int):
        # prevent callbacks while populating table row
        self.table.blockSignals(True)

        preset = self.track_group_presets[row]

        col = 0
        
        font = QFont()
        if preset.selected_to_add:
            font.setBold(True)

        # add/remove button
        add_remove_btn = QPushButton()
        add_remove_btn.setIcon(Icons.minus_box_outline() if preset.selected_to_add else Icons.plus_box_outline())
        add_remove_btn.setStyleSheet("padding: 3px 3px")
        add_remove_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        add_remove_btn.clicked.connect(lambda _, row=row: self._on_toggle_add(row))
        self.table.setCellWidget(row, col, LayoutUtil.center(add_remove_btn))
        col += 1

        # status
        status_font = QFont()
        status_font.setPointSizeF(font.pointSizeF() * 0.6)
        status_item = QTableWidgetItem("Add" if preset.selected_to_add else "")
        status_item.setFont(status_font)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, col, status_item)
        col += 1

        # name
        name_item = QTableWidgetItem(preset.name)
        name_item.setFont(font)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, col, name_item)
        col += 1

        # color
        color_btn = ColorButton(color=preset.color, read_only=True)
        color_btn.setFont(font)
        self.table.setCellWidget(row, col, color_btn)
        col += 1

        # opacity
        opacity = Util.int_internal_to_display(
            internal_value=preset.alpha,
            display_min=0, 
            display_max=100, 
            internal_min=0, 
            internal_max=255
        )
        opacity_item = QTableWidgetItem(f"{opacity}")
        opacity_item.setFont(font)
        opacity_item.setFlags(opacity_item.flags() & ~Qt.ItemIsEditable)
        opacity_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, opacity_item)
        col += 1

        # sparks
        checkbox = TableCheckBox(preset.note_sparks_enabled)
        checkbox.setReadOnly(True)
        self.table.setCellWidget(row, col, checkbox)
        col += 1

        # bounce
        checkbox = TableCheckBox(preset.note_bounce_enabled)
        checkbox.setReadOnly(True)
        self.table.setCellWidget(row, col, checkbox)
        col += 1

        # velocity fx
        checkbox = TableCheckBox(preset.note_velocity_fx_enabled)
        checkbox.setReadOnly(True)
        self.table.setCellWidget(row, col, checkbox)
        col += 1

        # bar height ratio
        bar_height = Util.float_internal_to_display(
            internal_value=preset.bar_height_ratio,
            internal_min=0.001, 
            internal_max=1.000, 
            display_min=1.0, 
            display_max=10.0
        )
        bar_height_item = QTableWidgetItem(f"{bar_height:.2f}")
        bar_height_item.setFont(font)
        bar_height_item.setFlags(bar_height_item.flags() & ~Qt.ItemIsEditable)
        bar_height_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, bar_height_item)
        col += 1

        # pixels/sec
        sec_across_screen = Util.float_internal_to_display(
            internal_value=preset.bar_sec_across_screen,
            internal_min=10.0,
            internal_max=0.1,
            display_min=0.1,
            display_max=10.0
        )
        sec_across_screen_item = QTableWidgetItem(f"{sec_across_screen:.1f}")
        sec_across_screen_item.setFont(font)
        sec_across_screen_item.setFlags(sec_across_screen_item.flags() & ~Qt.ItemIsEditable)
        sec_across_screen_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, sec_across_screen_item)
        col += 1

        # pitch offset
        pitch_offset_item = QTableWidgetItem(f"{preset.pitch_offset}")
        pitch_offset_item.setFont(font)
        pitch_offset_item.setFlags(pitch_offset_item.flags() & ~Qt.ItemIsEditable)
        pitch_offset_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, pitch_offset_item)
        col += 1

        # resume callbacks
        self.table.blockSignals(False)

    def _save(self):
        for p in self.track_group_presets:
            if not p.selected_to_add:
                continue

            self.vis_config.add_track_group(p.to_track_group())
        
        self.accept()

    # Callbacks
    
    def _on_select_all(self):
        for preset in self.track_group_presets:
            preset.selected_to_add = True

        self._refresh_ui()
    
    def _on_clear_selections(self):
        for preset in self.track_group_presets:
            preset.selected_to_add = False

        self._refresh_ui()


    def _on_toggle_add(self, row: int):
        rows = self._get_rows_for_bulk_edit(row)

        presets = [self.track_group_presets[r] for r in rows]

        presets_count = len(presets)
        selected_to_add_count = sum(1 for p in presets if p.selected_to_add)

        # if none or some of the selected rows are "selected to add", then make
        # all of the selection "selected to add"
        to_value = True if selected_to_add_count < presets_count else False
        for p in presets:
            p.selected_to_add = to_value

        self._refresh_ui()

    # Getters
    def _get_selected_rows(self) -> list[int]:
        selected_rows: set[int] = set()

        for selection_range in self.table.selectedRanges():
            for row in range(selection_range.topRow(), selection_range.bottomRow() + 1):
                selected_rows.add(row)

        return sorted(selected_rows)

    def _get_rows_for_bulk_edit(self, changed_row: int):
        # get all currently selected rows (including changed row)
        rows = self._get_selected_rows()
        if len(rows) == 1:
            # if only one other row is selected, exclude it - it 
            # feels a bit jarring otherwise
            rows = []

        if changed_row not in rows:
            rows.append(changed_row)
        return rows