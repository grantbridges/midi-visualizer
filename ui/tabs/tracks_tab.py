from dataclasses import dataclass
from typing import List
from uuid import UUID

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QPushButton,
    QStyle,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QHeaderView,
)
from models import VisConfig
from utility import MidiUtil

import logging
logger = logging.getLogger("TracksTab")

class TracksTab(QWidget):
    def __init__(self, vis_config: VisConfig, on_changes_callback: object, parent=None):
        super().__init__(parent)

        self.on_changes_callback = on_changes_callback
        self.vis_config = vis_config

        # create controls
        self.track_columns = ["", "", "Name", "Group", "Pitch Min", "Pitch Max", "Start (sec)", "End (sec)"]
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
        v_layout.addWidget(self.table)

    def refresh_ui(self):
        # prevent callbacks while populating
        self.table.blockSignals(True)

        self.table.setRowCount(len(self.vis_config.tracks))
        style = self.style()

        for row, track in enumerate(self.vis_config.tracks):
            col = 0

            # move up button
            up_btn = QPushButton()
            up_btn.setIcon(style.standardIcon(QStyle.SP_ArrowUp))
            up_btn.setFixedSize(32, 24)
            up_btn.clicked.connect(lambda _, row=row: self._on_move_track_up(row))
            self.table.setCellWidget(row, col, up_btn)
            col += 1

            # move down button
            down_btn = QPushButton()
            down_btn.setIcon(style.standardIcon(QStyle.SP_ArrowDown))
            down_btn.setFixedSize(32, 24)
            down_btn.clicked.connect(lambda _, row=row: self._on_move_track_down(row))
            self.table.setCellWidget(row, col, down_btn)
            col += 1

            # name
            name_item = QTableWidgetItem(track.name)
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
            combo.currentIndexChanged.connect(self._on_group_changed)
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

        # resume callbacks
        self.table.blockSignals(False)

    def update_model(self):
        # update track props from table
        for row in range(self.table.rowCount()):
            track = self.vis_config.tracks[row]
            group_combo: QComboBox = self.table.cellWidget(row, self.track_columns.index("Group"))
            group = group_combo.currentData()
            track.group_id = UUID(group) if group is not None else None

    def _on_move_track_up(self, row: int):
        if row > 0:
            # swap
            self.vis_config.tracks[row-1], self.vis_config.tracks[row] = self.vis_config.tracks[row], self.vis_config.tracks[row-1]
            self.refresh_ui()

            self.on_changes_callback()

    def _on_move_track_down(self, row: int):
        if row < len(self.vis_config.tracks) - 1:
            # swap
            self.vis_config.tracks[row+1], self.vis_config.tracks[row] = self.vis_config.tracks[row], self.vis_config.tracks[row+1]
            self.refresh_ui()

            self.on_changes_callback()

    def _on_group_changed(self):
        self.on_changes_callback()
        self.refresh_ui()