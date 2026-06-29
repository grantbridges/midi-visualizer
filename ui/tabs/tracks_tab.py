from dataclasses import dataclass
from typing import List
from uuid import UUID
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QStyle,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QHeaderView,
)
from models import VisConfig
from utility import MidiUtil, Util, QUtil

import logging
logger = logging.getLogger("TracksTab")

class TracksTab(QWidget):
    def __init__(self, vis_config: VisConfig, on_changes_callback: object, parent=None):
        super().__init__(parent)

        self.on_changes_callback = on_changes_callback
        self.vis_config = vis_config

        # create controls
        self.sort_by_group_btn = QPushButton("Sort by Group")
        self.sort_by_group_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.sort_by_group_btn.clicked.connect(self._on_sort_by_group)

        self.track_columns = ["", "", "Name", "Group", "Pitch Min", "Pitch Max", "Start (sec)", "End (sec)", "Vel. Min", "Vel. Max", "Vel. Avg"]
        self.table = QTableWidget(0, len(self.track_columns))
        self.table.setHorizontalHeaderLabels(self.track_columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # set button columns to shrink
        for col in [0, 1]:
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)

    def shutdown(self):
        pass

    def layout_controls(self):
        # layout controls
        v_layout = QVBoxLayout(self)
        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.sort_by_group_btn)
        btns_layout.addStretch()
        v_layout.addLayout(btns_layout)
        v_layout.addWidget(self.table)

    def refresh_ui(self):
        # prevent callbacks while populating
        self.table.blockSignals(True)

        self.table.setRowCount(len(self.vis_config.tracks))
        style = self.style()

        for row, track in enumerate(self.vis_config.tracks):
            col = 0

            group = self.vis_config.get_track_group_by_id(track.group_id)

            # move up button
            up_btn = QPushButton()
            up_btn.setIcon(style.standardIcon(QStyle.SP_ArrowUp))
            up_btn.setFixedSize(32, 24)
            up_btn.setDisabled(row == 0)
            up_btn.clicked.connect(lambda _, row=row: self._on_move_track_up(row))
            self.table.setCellWidget(row, col, up_btn)
            col += 1

            # move down button
            down_btn = QPushButton()
            down_btn.setIcon(style.standardIcon(QStyle.SP_ArrowDown))
            down_btn.setFixedSize(32, 24)
            down_btn.setDisabled(row == len(self.vis_config.tracks) - 1)
            down_btn.clicked.connect(lambda _, row=row: self._on_move_track_down(row))
            self.table.setCellWidget(row, col, down_btn)
            col += 1

            # name
            name_item = QTableWidgetItem(track.name)
            if group is not None:
                # color by group color
                name_item.setBackground(QBrush(QUtil.rgb_to_qcolor(group.color)))
                name_item.setForeground(QBrush(QUtil.rgb_to_qcolor(Util.contrast_color(group.color))))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, col, name_item)
            col += 1

            # groups dropdown
            combo = QComboBox()
            combo.addItem("None", None)
            for group in self.vis_config.track_groups:
                combo.addItem(group.name, str(group.group_id))

            if track.group_id is not None:
                index = combo.findData(str(track.group_id)) 
                if index >= 0:
                    combo.setCurrentIndex(index)
            combo.currentIndexChanged.connect(lambda index, row=row: self._on_group_changed(row, index))
            self.table.setCellWidget(row, col, combo)
            col += 1

            # pitch min
            pitch_min_item = QTableWidgetItem(f"{track.pitch_min} ({MidiUtil.midi_pitch_to_note(track.pitch_min)})")
            pitch_min_item.setFlags(pitch_min_item.flags() & ~Qt.ItemIsEditable)
            pitch_min_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, pitch_min_item)
            col += 1

            # pitch max
            pitch_max_item = QTableWidgetItem(f"{track.pitch_max} ({MidiUtil.midi_pitch_to_note(track.pitch_max)})")
            pitch_max_item.setFlags(pitch_max_item.flags() & ~Qt.ItemIsEditable)
            pitch_max_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, pitch_max_item)
            col += 1

            # time min
            time_min_item = QTableWidgetItem(f"{track.time_min:.2f}")
            time_min_item.setFlags(time_min_item.flags() & ~Qt.ItemIsEditable)
            time_min_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, time_min_item)
            col += 1

            # time max
            time_max_item = QTableWidgetItem(f"{track.time_max:.2f}")
            time_max_item.setFlags(time_max_item.flags() & ~Qt.ItemIsEditable)
            time_max_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, time_max_item)
            col += 1

            # velocity min
            velocity_min_item = QTableWidgetItem(f"{track.velocity_min:.2f}")
            velocity_min_item.setFlags(velocity_min_item.flags() & ~Qt.ItemIsEditable)
            velocity_min_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, velocity_min_item)
            col += 1

            # velocity max
            velocity_max_item = QTableWidgetItem(f"{track.velocity_max:.2f}")
            velocity_max_item.setFlags(velocity_max_item.flags() & ~Qt.ItemIsEditable)
            velocity_max_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, velocity_max_item)
            col += 1

            # velocity avg
            velocity_avg_item = QTableWidgetItem(f"{track.velocity_avg:.2f}")
            velocity_avg_item.setFlags(velocity_avg_item.flags() & ~Qt.ItemIsEditable)
            velocity_avg_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, velocity_avg_item)
            col += 1

        # resume callbacks
        self.table.blockSignals(False)

    def update_model(self):
        # No work here - we update vis_config tracks directly on changes
        pass

    def _on_move_track_up(self, row: int):
        if row == 0:
            Util.swap(self.vis_config.tracks, row, row-1)
            
            self.refresh_ui()
            self.on_changes_callback()

    def _on_move_track_down(self, row: int):
        if row < len(self.vis_config.tracks) - 1:
            Util.swap(self.vis_config.tracks, row, row+1)
            
            self.refresh_ui()
            self.on_changes_callback()

    def _on_group_changed(self, row: int, col: int):
        # get selected value from this row
        group_combo: QComboBox = self.table.cellWidget(row, self.track_columns.index("Group"))
        group = group_combo.currentData()
        group_id = UUID(group) if group is not None else None

        # get all selected rows, plus the row this group was changed on
        # so we can apply a bulk change
        rows = set([row] + self._get_selected_rows())
        for row in rows:
            track = self.vis_config.tracks[row]
            track.group_id = group_id

        self.refresh_ui()
        self.on_changes_callback()

    def _on_sort_by_group(self):
        # reorder tracks to be alongside others in their group
        # while maintaining their original relative order
        group_order = {
            group.group_id: index
            for index, group in enumerate(self.vis_config.track_groups)
        }

        # sort tracks with no group (or invalid group) to the end
        none_index = len(self.vis_config.track_groups)

        self.vis_config.tracks.sort(
            key=lambda track: group_order.get(track.group_id, none_index)
        )

        self.refresh_ui()
        self.on_changes_callback()

    # Getters
    def _get_selected_rows(self):
        selected_rows: set[int] = set()

        for selection_range in self.table.selectedRanges():
            for row in range(selection_range.topRow(), selection_range.bottomRow() + 1):
                selected_rows.add(row)

        return sorted(selected_rows)