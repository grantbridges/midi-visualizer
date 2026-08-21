from typing import List
from uuid import UUID
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QHeaderView,
    QMenu,
    QAbstractItemView
)
from models import VisConfig, Track
from ui.common import LayoutUtil, Icons, TableCheckbox, TableSpinbox
from utility import MidiUtil, Util
from ui.dialogs import GroupTracksDialog

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

        self.group_tracks_btn = QPushButton("") # set text in refresh_buttons()
        self.group_tracks_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.group_tracks_btn.clicked.connect(self._on_group_tracks)

        self.clear_selection_btn = QPushButton("Clear Selection")
        self.clear_selection_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.clear_selection_btn.clicked.connect(self._on_clear_selection)

        self.track_columns = ["", "", "Name", "Group", "Override\nPitch Range", "Pitch Min", "Pitch Max", "Notes", "Start (sec)", "End (sec)", "Vel. Min", "Vel. Max"]
        self.table = QTableWidget(0, len(self.track_columns))
        self.table.setHorizontalHeaderLabels(self.track_columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        # set up right-click handling
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_table_context_menu)

        # set whole-row multi-select
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)        

    def shutdown(self):
        pass

    def layout_controls(self):
        # layout controls
        v_layout = QVBoxLayout(self)
        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.group_tracks_btn)
        btns_layout.addWidget(self.clear_selection_btn)
        btns_layout.addWidget(self.sort_by_group_btn)
        btns_layout.addStretch()
        v_layout.addLayout(btns_layout)
        v_layout.addWidget(self.table)

    def refresh_ui(self):
        self._refresh_buttons()

        # prevent callbacks while populating table
        self.table.blockSignals(True)

        self.table.setRowCount(len(self.vis_config.tracks))

        for row in range(len(self.vis_config.tracks)):
            self._refresh_row(row)

        # resume callbacks
        self.table.blockSignals(False)

    def _clear_row(self, row: int):
        for col in range(self.table.columnCount()):
            # remove widgets/items, if either present
            self.table.removeCellWidget(row, col)
            self.table.setItem(row, col, None)

    def _refresh_row(self, row: int):
        #self._clear_row(row)

        track = self.vis_config.tracks[row]
        group = self.vis_config.get_track_group_by_id(track.group_id)

        col = 0

        # move up button
        up_btn = QPushButton()
        up_btn.setIcon(Icons.arrow_up_bold())
        up_btn.setDisabled(row == 0)
        up_btn.clicked.connect(lambda _, row=row: self._on_move_track_up(row))
        self.table.setCellWidget(row, col, LayoutUtil.center(up_btn))
        col += 1

        # move down button
        down_btn = QPushButton()
        down_btn.setIcon(Icons.arrow_down_bold())
        down_btn.setDisabled(row == len(self.vis_config.tracks) - 1)
        down_btn.clicked.connect(lambda _, row=row: self._on_move_track_down(row))
        self.table.setCellWidget(row, col, LayoutUtil.center(down_btn))
        col += 1

        # name
        name_item = QTableWidgetItem(track.name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, col, name_item)
        col += 1

        # groups dropdown
        combo = QComboBox()
        combo.addItem("None", None)
        for tg in self.vis_config.track_groups:
            combo.addItem(tg.name, str(tg.group_id))

        if track.group_id is not None:
            index = combo.findData(str(track.group_id)) 
            if index >= 0:
                combo.setCurrentIndex(index)

                r, g, b = group.color
                text_r, text_g, text_b = Util.contrast_color((r, g, b))

                # color bg + text by color
                combo.setStyleSheet(f"""
                    QComboBox {{
                        background-color: rgb({r}, {g}, {b});
                        color: rgb({text_r}, {text_g}, {text_b});
                    }}
                """)

        combo.currentIndexChanged.connect(lambda index, row=row: self._on_group_changed(row, index))
        self.table.setCellWidget(row, col, combo)
        col += 1

        # override pitch range
        override_pitch_checkbox = TableCheckbox(track.override_pitch_min_max)
        override_pitch_checkbox.valueChanged.connect(lambda checked, row=row: self._on_override_pitch_changed(row, checked))
        self.table.setCellWidget(row, col, override_pitch_checkbox)
        col += 1

        # pitch min
        pitch_min = track.manual_pitch_min if track.override_pitch_min_max else track.pitch_min
        pitch_min_input = TableSpinbox(value=pitch_min, suffix=self._pitch_suffix(pitch_min))
        pitch_min_input.setRange(1, track.manual_pitch_max)
        pitch_min_input.setEnabled(track.override_pitch_min_max)
        pitch_min_input.valueChanged.connect(lambda val, row=row: self._on_pitch_min_changed(row, val))
        self.table.setCellWidget(row, col, pitch_min_input)
        col += 1

        # pitch max
        pitch_max = track.manual_pitch_max if track.override_pitch_min_max else track.pitch_max
        pitch_max_input = TableSpinbox(value=pitch_max, suffix=self._pitch_suffix(pitch_max))
        pitch_max_input.setRange(track.manual_pitch_min, 127)
        pitch_max_input.setEnabled(track.override_pitch_min_max)
        pitch_max_input.valueChanged.connect(lambda val, row=row: self._on_pitch_max_changed(row, val))
        self.table.setCellWidget(row, col, pitch_max_input)
        col += 1

        # notes count
        notes_count_item = QTableWidgetItem(f"{len(track.notes)}")
        notes_count_item.setFlags(notes_count_item.flags() & ~Qt.ItemIsEditable)
        notes_count_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, notes_count_item)
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
        velocity_min_item = QTableWidgetItem(f"{track.velocity_min:.0f}")
        velocity_min_item.setFlags(velocity_min_item.flags() & ~Qt.ItemIsEditable)
        velocity_min_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, velocity_min_item)
        col += 1

        # velocity max
        velocity_max_item = QTableWidgetItem(f"{track.velocity_max:.0f}")
        velocity_max_item.setFlags(velocity_max_item.flags() & ~Qt.ItemIsEditable)
        velocity_max_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, velocity_max_item)
        col += 1

    def _refresh_buttons(self):
        count = len(self._get_selected_rows())

        self.group_tracks_btn.setEnabled(count > 0)
        self.group_tracks_btn.setText(f"Group {count} Track{"s" if count > 1 else ""}" if count > 0 else "Group Tracks")

        self.clear_selection_btn.setEnabled(count > 0)

    def update_model(self):
        # No work here - we update vis_config tracks directly on changes
        pass

    def _on_move_track_up(self, row: int):
        if row > 0:
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

        # get all currently selected rows (including row this group is on)
        rows = self._get_selected_rows()
        if row not in rows:
            rows.append(row)

        for r in rows:
            track = self.vis_config.tracks[r]
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

    def _on_group_tracks(self):
        self._group_from_selected_tracks()

    def _on_clear_selection(self):
        self.table.clearSelection()
        self.table.setCurrentCell(-1, -1)

        self._refresh_buttons()

    def _on_override_pitch_changed(self, row: int, checked: bool):
        if self.table.signalsBlocked():
            return
        
        track = self.vis_config.tracks[row]
        track.override_pitch_min_max = checked

        self._refresh_row(row)

        self.on_changes_callback()

    def _on_pitch_min_changed(self, row: int, value: int):
        if self.table.signalsBlocked():
            return
        
        track = self.vis_config.tracks[row]
        track.manual_pitch_min = value

        # update suffix of this cell
        col = self.track_columns.index("Pitch Min")
        pitch_min_input: TableSpinbox = self.table.cellWidget(row, col)
        pitch_min_input.setSuffix(self._pitch_suffix(value))

        # update maximum value of pitch min cell
        col = self.track_columns.index("Pitch Max")
        pitch_max_input: TableSpinbox = self.table.cellWidget(row, col)
        if pitch_max_input:
            pitch_max_input.setMinimum(track.manual_pitch_min)

        self.on_changes_callback()

    def _on_pitch_max_changed(self, row: int, value: int):
        if self.table.signalsBlocked():
            return
        
        track = self.vis_config.tracks[row]
        track.manual_pitch_max = value

        # update suffix of this cell
        col = self.track_columns.index("Pitch Max")
        pitch_max_input: TableSpinbox = self.table.cellWidget(row, col)
        pitch_max_input.setSuffix(self._pitch_suffix(value))

        # update maximum value of pitch min cell
        col = self.track_columns.index("Pitch Min")
        pitch_min_input: TableSpinbox = self.table.cellWidget(row, col)
        if pitch_min_input:
            pitch_min_input.setMaximum(track.manual_pitch_max)

        self.on_changes_callback()

    def _on_table_context_menu(self, pos: QPoint):
        rows = self._get_selected_rows()

        menu = QMenu(self)

        count = len(rows)
        group_text = "Group Track..." if count == 1 else f"Group {count} Selected Tracks..."
        create_group = menu.addAction(group_text)

        # create menu on right-click location
        action = menu.exec(self.table.viewport().mapToGlobal(pos))

        if action == create_group:
            self._group_from_selected_tracks()

    def _on_selection_changed(self):
        self._refresh_buttons()

    def _group_from_selected_tracks(self):
        selected_tracks = self._get_selected_tracks()

        dialog = GroupTracksDialog(selected_tracks, self.vis_config, self)

        if dialog.exec() != QDialog.Accepted:
            return

        group_id: UUID | None = None

        track_group = dialog.get_track_group()
        self.vis_config.add_track_group(track_group)
        group_id = track_group.group_id

        for track in selected_tracks:
            track.group_id = group_id

        self.refresh_ui()
        self.on_changes_callback()

    # Getters
    def _get_selected_rows(self) -> List[int]:
        selected_rows: set[int] = set()

        for selection_range in self.table.selectedRanges():
            for row in range(selection_range.topRow(), selection_range.bottomRow() + 1):
                selected_rows.add(row)

        return sorted(selected_rows)
    
    def _get_selected_tracks(self) -> List[Track]:
        rows = self._get_selected_rows()
        tracks = []
        for row in rows:
            if row >= 0 and row < len(self.vis_config.tracks):
                tracks.append(self.vis_config.tracks[row])
        return tracks
    
    def _pitch_suffix(self, pitch: int) -> str:
        return f" ({MidiUtil.midi_pitch_to_note(pitch)})"



