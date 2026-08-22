
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QSizePolicy,
    QAbstractItemView
)
from common import RGB
from models import VisConfig
from utility import Util
from ui.common import (
    ColorButton, 
    TableCheckBox, 
    TableSpinBox,
    LayoutUtil, 
    Icons, 
    ScaledSpinBox, 
    ScaledDoubleSpinBox
)
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

        self.track_columns = ["", "", "Name", "Tracks", "Solo", "Visible", "Color", "Opacity", "Note\nSparks", "Note\nBounce", "Note\nVel. Fx", "Bar Height", "Speed", "Pitch Offset", ""]
        self.table = QTableWidget(0, len(self.track_columns))
        self.table.setHorizontalHeaderLabels(self.track_columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
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
        self._refresh_buttons()

        self.table.setRowCount(len(self.vis_config.track_groups))
        for row in range(len(self.vis_config.track_groups)):
            self._refresh_row(row)

    def _refresh_row(self, row: int):
        # prevent callbacks while populating table row
        self.table.blockSignals(True)

        track_group = self.vis_config.track_groups[row]

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
        checkbox = TableCheckBox(track_group.solo)
        checkbox.valueChanged.connect(lambda checked, row=row: self._on_solo_changed(row, checked))
        self.table.setCellWidget(row, col, checkbox)
        col += 1

        # visible
        checkbox = TableCheckBox(track_group.visible)
        checkbox.valueChanged.connect(lambda checked, row=row: self._on_visible_changed(row, checked))
        self.table.setCellWidget(row, col, checkbox)
        col += 1

        # color button
        color_btn = ColorButton(color=track_group.color)
        color_btn.valueChanged.connect(lambda color, row=row: self._on_color_changed(row, color))
        self.table.setCellWidget(row, col, color_btn)
        col += 1

        # opacity
        opacity = ScaledSpinBox(
            internal_value=track_group.alpha, 
            display_min=0, 
            display_max=100, 
            internal_min=0, 
            internal_max=255,
            disable_mouse_wheel=True
        )
        opacity.valueChanged.connect(lambda _, row=row, widget=opacity: self._on_opacity_changed(row, widget.getInternalValue()))
        self.table.setCellWidget(row, col, opacity)
        col += 1

        # sparks
        checkbox = TableCheckBox(track_group.note_sparks_enabled)
        checkbox.valueChanged.connect(lambda checked, row=row: self._on_sparks_changed(row, checked))
        self.table.setCellWidget(row, col, checkbox)
        col += 1

        # bounce
        checkbox = TableCheckBox(track_group.note_bounce_enabled)
        checkbox.valueChanged.connect(lambda checked, row=row: self._on_bounce_changed(row, checked))
        self.table.setCellWidget(row, col, checkbox)
        col += 1

        # velocity fx
        checkbox = TableCheckBox(track_group.note_velocity_fx_enabled)
        checkbox.valueChanged.connect(lambda checked, row=row: self._on_velocity_fx_changed(row, checked))
        self.table.setCellWidget(row, col, checkbox)
        col += 1

        # bar height ratio
        bar_height = ScaledDoubleSpinBox(
            decimals=2, 
            singleStep=0.01, 
            display_min=1.0, 
            display_max=10.0, 
            internal_min=0.001, 
            internal_max=1.000, 
            internal_value=track_group.bar_height_ratio,
            disable_mouse_wheel=True
        )
        bar_height.valueChanged.connect(lambda _, row=row, widget=bar_height: self._on_bar_height_changed(row, widget.getInternalValue()))
        self.table.setCellWidget(row, col, bar_height)
        col += 1

        # pixels/sec
        sec_across_screen = ScaledDoubleSpinBox(
            decimals=1,
            singleStep=0.1,
            display_min=0.1,
            display_max=10.0,
            internal_min=10.0,
            internal_max=0.1,
            internal_value=track_group.bar_sec_across_screen,
            disable_mouse_wheel=True
        )
        sec_across_screen.valueChanged.connect(lambda _, row=row, widget=sec_across_screen: self._on_bar_speed_changed(row, widget.getInternalValue()))
        self.table.setCellWidget(row, col, sec_across_screen)
        col += 1

        # pitch offset
        group_pitch_min = self.vis_config.get_min_pitch_for_track_group(track_group.group_id, True)
        group_pitch_max = self.vis_config.get_max_pitch_for_track_group(track_group.group_id, True)
        pitch_offset = TableSpinBox()
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

    def _refresh_buttons(self):
        row = self.table.currentRow()
        self.clear_selection_btn.setDisabled(row == -1)

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

        self.refresh_ui()
        self.on_changes_callback()

    def _on_clear_selection(self):
        self.table.clearSelection()
        self.table.setCurrentCell(-1, -1)

        self._refresh_buttons()

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
            self.on_changes_callback()

    def _on_cell_changed(self, row: int, col: int, prev_row: int, prev_col: int):
        if row >= 0 and row < len(self.vis_config.track_groups):
            track_group = self.vis_config.track_groups[row]
            self.on_track_group_selected_callback(track_group.group_id)
        else:
            self.on_track_group_selected_callback(None)

        self._refresh_buttons()
        
    def _on_solo_changed(self, row: int, checked: bool):
        if self.table.signalsBlocked():
            return

        for r in self._get_rows_for_bulk_edit(row):
            track_group = self.vis_config.track_groups[r]
            track_group.solo = checked

            if track_group.solo:
                # require visible if solo
                track_group.visible = True

            self._refresh_row(r)

        self._refresh_buttons()
        self.on_changes_callback()
        
    def _on_visible_changed(self, row: int, checked: bool):
        if self.table.signalsBlocked():
            return

        for r in self._get_rows_for_bulk_edit(row):
            track_group = self.vis_config.track_groups[r]
            track_group.visible = checked

            if not track_group.visible:
                # can't be solo if not visible
                track_group.solo = False

            self._refresh_row(r)

        self._refresh_buttons()
        self.on_changes_callback()

    def _on_color_changed(self, row: int, color: RGB):
        if self.table.signalsBlocked():
            return
        
        track_group = self.vis_config.track_groups[row]
        track_group.color = color
        self.on_changes_callback()

    def _on_opacity_changed(self, row: int, opacity: int):
        if self.table.signalsBlocked():
            return
        
        track_group = self.vis_config.track_groups[row]
        track_group.alpha = opacity
        self.on_changes_callback()
    
    def _on_sparks_changed(self, row: int, checked: bool):
        if self.table.signalsBlocked():
            return

        for r in self._get_rows_for_bulk_edit(row):
            track_group = self.vis_config.track_groups[r]
            track_group.note_sparks_enabled = checked

            self._refresh_row(r)
        
        self.on_changes_callback()
    
    def _on_bounce_changed(self, row: int, checked: bool):
        if self.table.signalsBlocked():
            return

        for r in self._get_rows_for_bulk_edit(row):
            track_group = self.vis_config.track_groups[r]
            track_group.note_bounce_enabled = checked

            self._refresh_row(r)
        
        self.on_changes_callback()
    
    def _on_velocity_fx_changed(self, row: int, checked: bool):
        if self.table.signalsBlocked():
            return

        for r in self._get_rows_for_bulk_edit(row):
            track_group = self.vis_config.track_groups[r]
            track_group.note_velocity_fx_enabled = checked

            self._refresh_row(r)
        
        self.on_changes_callback()

    def _on_bar_height_changed(self, row: int, value: float):
        if self.table.signalsBlocked():
            return
        
        track_group = self.vis_config.track_groups[row]
        track_group.bar_height_ratio = value
        self.on_changes_callback()

    def _on_bar_speed_changed(self, row: int, value: float):
        if self.table.signalsBlocked():
            return
        
        track_group = self.vis_config.track_groups[row]
        track_group.bar_sec_across_screen = value
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