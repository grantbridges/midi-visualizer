from uuid import UUID

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QComboBox,
    QHeaderView,
)

from common.types import RGB
from models import VisConfig
from utility import MidiUtil
from ui.common import ColorButton, TableCheckbox, TableSpinbox
import copy

class TracksTab(QWidget):
    def __init__(self, on_changes_callback: object, vis_config: VisConfig):
        super().__init__()

        self.on_changes_callback = on_changes_callback
        self.vis_config = vis_config

        # create controls
        self.track_columns = ["Name", "Group", "Pitch Min", "Pitch Max", "Start (sec)", "End (sec)"]
        self.table = QTableWidget(0, len(self.track_columns))
        self.table.setHorizontalHeaderLabels(self.track_columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # layout controls
        v_layout = QVBoxLayout(self)
        v_layout.addWidget(self.table)

    def refresh_ui(self):
        # prevent callbacks while populating
        self.table.blockSignals(True)

        self.table.setRowCount(len(self.vis_config.tracks))

        for row, track in enumerate(self.vis_config.tracks):
            col = 0

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
            name_item = self.table.item(row, 0)
            name = name_item.text()

            track = self.vis_config.get_track_by_name(name)
            if track is not None:
                group_combo: QComboBox = self.table.cellWidget(row, 1)
                group = group_combo.currentData()
                track.group_id = UUID(group) if group is not None else None
            else:
                print(f"Warning: Unknown track row \"{name}\"")

    def _on_group_changed(self):
        self.on_changes_callback()
        self.refresh_ui()