from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QHeaderView,
    QStyle,
    QSizePolicy,
    QAbstractItemView
)
from common import RGB, Color
from models import VisConfig, TrackGroup
from utility import Util, QUtil
from ui.common import ColorButton, TableCheckbox, TableSpinbox, TableDoubleSpinbox, LayoutUtil, Icons
import copy
from uuid import uuid4

import logging
logger = logging.getLogger("TrackGroupsTab")

class TrackGroupsTab(QWidget):
    def __init__(self, vis_config: VisConfig, on_changes_callback: object, on_track_group_selected_callback: object, parent=None):
        super().__init__(parent)

        self.on_changes_callback = on_changes_callback
        self.on_track_group_selected_callback = on_track_group_selected_callback
        self.vis_config = vis_config

        # create controls
        self.add_row_btn = QPushButton("Add Group")
        self.add_row_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.add_row_btn.clicked.connect(self._on_add_group)

        self.clear_selection_btn = QPushButton("Clear Selection")
        self.clear_selection_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.clear_selection_btn.clicked.connect(self._on_clear_selection)

        self.clear_solo_btn = QPushButton("Clear Solo")
        self.clear_solo_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.clear_solo_btn.clicked.connect(self._on_clear_solo)

        self.track_columns = ["", "", "Name", "Tracks", "Solo", "Visible", "Color", "Alpha", "Note Sparks", "Note Velocity Fx", "Bar Height", "Speed", "Pitch Offset", ""]
        self.table = QTableWidget(0, len(self.track_columns))
        self.table.setHorizontalHeaderLabels(self.track_columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # set button columns to shrink
        for col in [0, 1, len(self.track_columns) - 1]:
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self.table.itemChanged.connect(self._on_item_changed)
        self.table.currentCellChanged.connect(self._on_cell_changed)
        # set whole-row multi-select
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def shutdown(self):
        pass

    def layout_controls(self):
        # layout controls
        v_layout = QVBoxLayout(self)
        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.add_row_btn)
        btns_layout.addWidget(self.clear_selection_btn)
        btns_layout.addWidget(self.clear_solo_btn)
        btns_layout.addStretch()
        v_layout.addLayout(btns_layout)
        v_layout.addWidget(self.table)

    def refresh_ui(self):
        self._refresh_clear_selection_btn()
        self._refresh_clear_solo_btn()

        # prevent callbacks while populating table
        self.table.blockSignals(True)

        self.table.setRowCount(len(self.vis_config.track_groups))
        style = self.style()

        for row, track_group in enumerate(self.vis_config.track_groups):
            col = 0

            # move up button
            up_btn = QPushButton()
            up_btn.setIcon(Icons.arrow_up_bold())
            up_btn.setDisabled(row == 0)
            up_btn.clicked.connect(lambda _, row=row: self._on_move_group_up(row))
            self.table.setCellWidget(row, col, LayoutUtil.center(up_btn))
            col += 1

            # move down button
            down_btn = QPushButton()
            down_btn.setIcon(Icons.arrow_down_bold())
            down_btn.setDisabled(row == len(self.vis_config.track_groups) - 1)
            down_btn.clicked.connect(lambda _, row=row: self._on_move_group_down(row))
            self.table.setCellWidget(row, col, LayoutUtil.center(down_btn))
            col += 1

            # name
            name_cell = QTableWidgetItem(track_group.name)
            self.table.setItem(row, col, name_cell)
            col += 1

            # tracks count
            tracks_count = len(self.vis_config.get_tracks_by_group_id(track_group.group_id))
            tracks_count_cell = QTableWidgetItem(f"{tracks_count}")
            tracks_count_cell.setFlags(tracks_count_cell.flags() & ~Qt.ItemIsEditable)
            tracks_count_cell.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, tracks_count_cell)
            col += 1

            # solo
            checkbox = TableCheckbox(track_group.solo)
            checkbox.valueChanged.connect(lambda checked, row=row: self._on_solo_changed(row, checked))
            self.table.setCellWidget(row, col, checkbox)
            col += 1

            # visible
            checkbox = TableCheckbox(track_group.visible)
            checkbox.valueChanged.connect(lambda checked, row=row: self._on_visible_changed(row, checked))
            self.table.setCellWidget(row, col, checkbox)
            col += 1

            # color button
            color_btn = ColorButton(color=track_group.color)
            color_btn.valueChanged.connect(lambda color, row=row: self._on_color_changed(row, color))
            self.table.setCellWidget(row, col, color_btn)
            col += 1

            # alpha
            alpha = TableSpinbox()
            alpha.setRange(0, 255)
            alpha.setValue(track_group.alpha)
            alpha.valueChanged.connect(lambda alpha, row=row: self._on_alpha_changed(row, alpha))
            self.table.setCellWidget(row, col, alpha)
            col += 1

            # sparks
            checkbox = TableCheckbox(track_group.note_sparks_enabled)
            checkbox.valueChanged.connect(lambda checked, row=row: self._on_sparks_changed(row, checked))
            self.table.setCellWidget(row, col, checkbox)
            col += 1

            # velocity fx
            checkbox = TableCheckbox(track_group.note_velocity_fx_enabled)
            checkbox.valueChanged.connect(lambda checked, row=row: self._on_velocity_fx_changed(row, checked))
            self.table.setCellWidget(row, col, checkbox)
            col += 1

            # bar height ratio
            bar_height = TableDoubleSpinbox()
            bar_height.setDecimals(2)
            bar_height.setRange(1.0, 10.0)
            bar_height.setSingleStep(0.01)
            bar_height_ratio_display_value = Util.internal_to_display(track_group.bar_height_ratio, 0.001, 1.000, 1.0, 10.0)
            bar_height.setValue(bar_height_ratio_display_value)
            bar_height.valueChanged.connect(lambda height, row=row: self._on_bar_height_changed(row, height))
            self.table.setCellWidget(row, col, bar_height)
            col += 1

            # pixels/sec
            sec_across_screen = TableDoubleSpinbox()
            sec_across_screen.setDecimals(1)
            sec_across_screen.setRange(0.1, 10.0)
            sec_across_screen.setSingleStep(.1)
            speed_display_value = Util.internal_to_display(track_group.bar_sec_across_screen, 0.1, 10.0, 10.0, 0.1)
            sec_across_screen.setValue(speed_display_value)
            sec_across_screen.valueChanged.connect(lambda speed, row=row: self._on_bar_speed_changed(row, speed))
            self.table.setCellWidget(row, col, sec_across_screen)
            col += 1

            # pitch offset
            group_pitch_min = self.vis_config.get_min_pitch_for_track_group(track_group.group_id, True)
            group_pitch_max = self.vis_config.get_max_pitch_for_track_group(track_group.group_id, True)
            pitch_offset = TableSpinbox()
            spinner_min = 0 - group_pitch_min
            spinner_max = 127 - group_pitch_max
            pitch_offset.setRange(spinner_min, spinner_max)
            pitch_offset.setValue(track_group.pitch_offset)
            pitch_offset.valueChanged.connect(lambda pad, row=row: self._on_pitch_offset_changed(row, pad))
            self.table.setCellWidget(row, col, pitch_offset)
            col += 1

            # delete button
            delete_btn = QPushButton()
            delete_btn.setIcon(Icons.trash_can())
            delete_btn.clicked.connect(lambda _, row=row: self._on_remove_group(row))
            self.table.setCellWidget(row, col, LayoutUtil.center(delete_btn))
            col += 1

        # resume callbacks
        self.table.blockSignals(False)

    def update_model(self):
        # No work here - we update vis_config track groups directly on changes
        pass

    def _refresh_clear_selection_btn(self):
        row = self.table.currentRow()
        self.clear_selection_btn.setDisabled(row == -1)

    def _refresh_clear_solo_btn(self):
        solo_count = sum(tg.solo for tg in self.vis_config.track_groups)
        self.clear_solo_btn.setDisabled(solo_count == 0)

    # Callbacks
    def _on_add_group(self):
        insert_index = len(self.vis_config.track_groups)
        # if we currently have rows selected, insert after end of selection
        selected_rows = self._get_selected_rows()
        if len(selected_rows) > 0:
            insert_index = selected_rows[-1] + 1

        # use sibling track group to seed properties from
        copy_from = self.vis_config.track_groups[insert_index - 1] if insert_index > 0 else self.vis_config.track_groups[0]
        track_group = copy.deepcopy(copy_from)
        
        # generate new name and Id
        track_group.name = f"Group {len(self.vis_config.track_groups)+1}"
        track_group.group_id = uuid4()
        self.vis_config.add_track_group(track_group, insert_index)

        self.on_changes_callback()
        self.refresh_ui()

    def _on_clear_selection(self):
        self.table.clearSelection()
        self.table.setCurrentCell(-1, -1)

        self._refresh_clear_selection_btn()

    def _on_clear_solo(self):
        for tg in self.vis_config.track_groups:
            tg.solo = False
        
        self.refresh_ui()
        self.on_changes_callback()

    def _on_remove_group(self, row: int):
        if 0 <= row < len(self.vis_config.track_groups):
            track_group = self.vis_config.track_groups[row]
            tracks = self.vis_config.get_tracks_by_group_id(track_group.group_id)

            if len(tracks) > 0:
                result = QMessageBox.question(
                    self,
                    "Confirm Track Group Delete",
                    f"The \"{track_group.name}\" track group is being used by {len(tracks)} track{"s" if len(tracks) > 1 else ""} ({", ".join(x.name for x in tracks)}). Are you sure you want to delete?",
                    QMessageBox.Cancel | QMessageBox.Yes,
                    QMessageBox.Cancel,
                )

                if result != QMessageBox.Yes:
                    return

            self.vis_config.remove_track_group(track_group.group_id)
            self.refresh_ui()

            self.on_changes_callback()

    def _on_move_group_up(self, row: int):
        if row > 0:
            Util.swap(self.vis_config.track_groups, row-1, row)
            self.refresh_ui()

            self.on_changes_callback()

    def _on_move_group_down(self, row: int):
        if row < len(self.vis_config.track_groups) - 1:
            # swap
            Util.swap(self.vis_config.track_groups, row+1, row)
            self.refresh_ui()

            self.on_changes_callback()

    def _on_item_changed(self, item: QTableWidgetItem):
        row = item.row()
        col = item.column()

        track_group = self.vis_config.track_groups[row]

        if col == self.track_columns.index("Name"):
            track_group.name = item.text()
        else:
            logger.warning(f"OnItemChanged for unhandled column: {self.track_columns[col]} (index: {col})")

        self.on_changes_callback()

    def _on_cell_changed(self, row: int, col: int, prev_row: int, prev_col: int):
        if row >= 0 and row < len(self.vis_config.track_groups):
            track_group = self.vis_config.track_groups[row]
            self.on_track_group_selected_callback(track_group.group_id)
        else:
            self.on_track_group_selected_callback(None)

        self._refresh_clear_selection_btn()
        
    def _on_solo_changed(self, row: int, checked: bool):
        if self.table.signalsBlocked():
            return
        
        track_group = self.vis_config.track_groups[row]
        track_group.solo = checked

        self._refresh_clear_solo_btn()

        self.on_changes_callback()
        
    def _on_visible_changed(self, row: int, checked: bool):
        if self.table.signalsBlocked():
            return
        
        track_group = self.vis_config.track_groups[row]
        track_group.visible = checked
        self.on_changes_callback()

    def _on_color_changed(self, row: int, color: RGB):
        if self.table.signalsBlocked():
            return
        
        track_group = self.vis_config.track_groups[row]
        track_group.color = color
        self.on_changes_callback()

    def _on_alpha_changed(self, row: int, alpha: int):
        if self.table.signalsBlocked():
            return
        
        track_group = self.vis_config.track_groups[row]
        track_group.alpha = alpha
        self.on_changes_callback()
    
    def _on_sparks_changed(self, row: int, checked: bool):
        if self.table.signalsBlocked():
            return
        
        track_group = self.vis_config.track_groups[row]
        track_group.note_sparks_enabled = checked
        self.on_changes_callback()
    
    def _on_velocity_fx_changed(self, row: int, checked: bool):
        if self.table.signalsBlocked():
            return
        
        track_group = self.vis_config.track_groups[row]
        track_group.note_velocity_fx_enabled = checked
        self.on_changes_callback()

    def _on_bar_height_changed(self, row: int, value: float):
        if self.table.signalsBlocked():
            return
        
        track_group = self.vis_config.track_groups[row]
        track_group.bar_height_ratio = Util.display_to_internal(value, 1.0, 10.0, 0.001, 1.0)
        self.on_changes_callback()

    def _on_bar_speed_changed(self, row: int, value: float):
        if self.table.signalsBlocked():
            return
        
        track_group = self.vis_config.track_groups[row]
        track_group.bar_sec_across_screen = Util.display_to_internal(value, 10.0, 0.1, 0.1, 10.0)
        self.on_changes_callback()

    def _on_pitch_offset_changed(self, row: int, value: int):
        if self.table.signalsBlocked():
            return
        
        track_group = self.vis_config.track_groups[row]
        track_group.pitch_offset = value
        self.on_changes_callback()

    # Getters
    def _get_selected_rows(self):
        selected_rows: set[int] = set()

        for selection_range in self.table.selectedRanges():
            for row in range(selection_range.topRow(), selection_range.bottomRow() + 1):
                selected_rows.add(row)

        return sorted(selected_rows)