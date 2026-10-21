from typing import List
from uuid import UUID
from PySide6.QtCore import QItemSelection, QItemSelectionModel, QPoint, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMenu,
    QAbstractItemView
)
from models import VisConfig, Track
from ui.common import (
    LayoutUtil, 
    Icons, 
    TableCheckBox, 
    TableSpinBox,
    TableComboBox,
    WidgetUtil
)
from utility import MidiUtil, Util
from ui.dialogs import GroupTracksDialog, ManageTrackPresetsDialog, ApplyTrackPresetsDialog

import logging
logger = logging.getLogger("TracksTab")

class TracksTab(QWidget):
    def __init__(self, vis_config: VisConfig, on_changes_callback: object, parent=None):
        super().__init__(parent)

        self.on_changes_callback = on_changes_callback
        self.vis_config = vis_config

        # create controls
        self.group_tracks_btn = QPushButton("") # set text in refresh_buttons()
        self.group_tracks_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.group_tracks_btn.clicked.connect(self._on_group_tracks)

        self.sort_by_group_btn = QPushButton("Sort by Group")
        self.sort_by_group_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.sort_by_group_btn.clicked.connect(self._on_sort_by_group)

        self.clear_selection_btn = QPushButton("Clear Selection")
        self.clear_selection_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.clear_selection_btn.clicked.connect(self._on_clear_selection)

        self.clear_solo_btn = QPushButton("Clear Solo")
        self.clear_solo_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.clear_solo_btn.clicked.connect(self._on_clear_solo)

        self.manage_presets_btn = WidgetUtil.icon_btn(Icons.format_list_group(), "Manage track presets")
        self.manage_presets_btn.clicked.connect(self._on_manage_presets)

        self.apply_presets_btn = WidgetUtil.icon_btn(Icons.format_list_group_plus(), "Apply track presets")
        self.apply_presets_btn.clicked.connect(self._on_apply_presets)

        self.move_top_btn = WidgetUtil.icon_btn(Icons.chevron_double_up(), "Move to top")
        self.move_top_btn.clicked.connect(self._on_move_track_top)

        self.move_up_btn = WidgetUtil.icon_btn(Icons.chevron_up(), "Move up")
        self.move_up_btn.clicked.connect(self._on_move_track_up)

        self.move_down_btn = WidgetUtil.icon_btn(Icons.chevron_down(), "Move down")
        self.move_down_btn.clicked.connect(self._on_move_track_down)

        self.move_bottom_btn = WidgetUtil.icon_btn(Icons.chevron_double_down(), "Move to bottom")
        self.move_bottom_btn.clicked.connect(self._on_move_track_bottom)

        self.track_columns = ["Name", "Group", "Solo", "Override\nPitches", "Pitch Min", "Pitch Max", "Notes", "Start (sec)", "End (sec)", "Vel. Min", "Vel. Max", ""]
        self.table = QTableWidget(0, len(self.track_columns))
        self.table.setHorizontalHeaderLabels(self.track_columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch) # name
        self.table.verticalHeader().setVisible(False) # hide row numbers
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
        btns_layout.addWidget(self.clear_solo_btn)
        btns_layout.addStretch()
        btns_layout.addWidget(self.manage_presets_btn)
        btns_layout.addWidget(self.apply_presets_btn)
        v_layout.addLayout(btns_layout)

        move_layout = QVBoxLayout()
        move_layout.addSpacing(30)
        move_layout.addWidget(self.move_top_btn)
        move_layout.addWidget(self.move_up_btn)
        move_layout.addWidget(self.move_down_btn)
        move_layout.addWidget(self.move_bottom_btn)
        move_layout.addStretch()

        table_layout = QHBoxLayout()
        table_layout.addLayout(move_layout)
        table_layout.addWidget(self.table)
        v_layout.addLayout(table_layout)

    def refresh_ui(self):
        self._refresh_buttons()

        self.table.setRowCount(len(self.vis_config.tracks))
        for row in range(len(self.vis_config.tracks)):
            self._refresh_row(row)
    
    def _refresh_row(self, row: int):
        # prevent callbacks while populating table row
        self.table.blockSignals(True)

        track = self.vis_config.tracks[row]
        group = self.vis_config.get_track_group_by_id(track.group_id)

        col = 0

        # name
        name_item = QTableWidgetItem(track.name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, col, name_item)
        col += 1

        # groups dropdown
        combo = TableComboBox()
        # allow opening while preserving selected table rows
        combo.setFocusPolicy(Qt.FocusPolicy.NoFocus) 
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

        # solo
        solo_checkbox = TableCheckBox(track.solo)
        solo_checkbox.valueChanged.connect(lambda checked, row=row: self._on_solo_changed(row, checked))
        self.table.setCellWidget(row, col, solo_checkbox)
        col += 1

        # override pitch range
        override_pitch_checkbox = TableCheckBox(track.override_pitch_min_max)
        override_pitch_checkbox.valueChanged.connect(lambda checked, row=row: self._on_override_pitch_changed(row, checked))
        self.table.setCellWidget(row, col, override_pitch_checkbox)
        col += 1

        # pitch min
        pitch_min = track.get_min_pitch()
        pitch_min_input = TableSpinBox(value=pitch_min, suffix=self._pitch_suffix(pitch_min))
        pitch_min_input.setFixedWidth(80)
        pitch_min_input.setRange(1, track.manual_pitch_max)
        pitch_min_input.setEnabled(track.override_pitch_min_max)
        pitch_min_input.valueChanged.connect(lambda val, row=row: self._on_pitch_min_changed(row, val))
        self.table.setCellWidget(row, col, pitch_min_input)
        col += 1

        # pitch max
        pitch_max = track.get_max_pitch()
        pitch_max_input = TableSpinBox(value=pitch_max, suffix=self._pitch_suffix(pitch_max))
        pitch_max_input.setFixedWidth(80)
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

        # delete button
        delete_btn = WidgetUtil.icon_btn(Icons.trash_can(), "Delete track")
        delete_btn.clicked.connect(lambda _, row=row: self._on_remove_track(row))
        self.table.setCellWidget(row, col, LayoutUtil.center(delete_btn))
        col += 1

        # resume callbacks
        self.table.blockSignals(False)

    def _refresh_buttons(self):
        selected_rows = self._get_selected_rows()
        selected_rows_count = len(selected_rows)

        self.group_tracks_btn.setEnabled(selected_rows_count > 0)
        self.group_tracks_btn.setText(f"Group {selected_rows_count} Track{"s" if selected_rows_count > 1 else ""}" if selected_rows_count > 0 else "Group Tracks")

        self.clear_selection_btn.setEnabled(selected_rows_count > 0)

        tracks_count = len(self.vis_config.tracks)
        self.move_top_btn.setEnabled(selected_rows_count > 0 and 0 not in selected_rows)
        self.move_up_btn.setEnabled(selected_rows_count > 0 and 0 not in selected_rows)
        self.move_down_btn.setEnabled(selected_rows_count > 0 and (tracks_count - 1) not in selected_rows)
        self.move_bottom_btn.setEnabled(selected_rows_count > 0 and (tracks_count - 1) not in selected_rows)

        any_solo = any(x.solo for x in self.vis_config.tracks)
        self.clear_solo_btn.setEnabled(any_solo)

    def update_model(self):
        # No work here - we update vis_config tracks directly on changes
        pass

    def _on_move_track_up(self):
        self._move_selected_tracks(-1)

    def _on_move_track_down(self):
        self._move_selected_tracks(1)

    def _on_move_track_top(self):
        self._move_selected_tracks(-len(self.vis_config.tracks))

    def _on_move_track_bottom(self):
        self._move_selected_tracks(len(self.vis_config.tracks))

    def _on_group_changed(self, row: int, col: int):
        # get selected value from this row
        group_combo: QComboBox = self.table.cellWidget(row, self.track_columns.index("Group"))
        group = group_combo.currentData()
        group_id = UUID(group) if group is not None else None

        for r in self._get_rows_for_bulk_edit(row):
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

    def _on_clear_solo(self):
        for t in self.vis_config.tracks:
            t.solo = False
        
        self.refresh_ui()
        self.on_changes_callback()

    def _on_manage_presets(self):
        dialog = ManageTrackPresetsDialog(vis_config=self.vis_config, parent=self)
        dialog.exec()

    def _on_apply_presets(self):
        dialog = ApplyTrackPresetsDialog(vis_config=self.vis_config, auto_apply_on_open=False, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_ui()
            self.on_changes_callback()

    def _on_solo_changed(self, row: int, checked: bool):
        if self.table.signalsBlocked():
            return

        for r in self._get_rows_for_bulk_edit(row):
            track = self.vis_config.tracks[r]
            track.solo = checked

        self.refresh_ui()
        self.on_changes_callback()

    def _on_override_pitch_changed(self, row: int, checked: bool):
        if self.table.signalsBlocked():
            return

        for r in self._get_rows_for_bulk_edit(row):
            track = self.vis_config.tracks[r]
            track.override_pitch_min_max = checked

        self.refresh_ui()
        self.on_changes_callback()

    def _on_pitch_min_changed(self, row: int, value: int):
        if self.table.signalsBlocked():
            return
        
        track = self.vis_config.tracks[row]
        track.manual_pitch_min = value

        # update suffix of this cell
        col = self.track_columns.index("Pitch Min")
        pitch_min_input: TableSpinBox = self.table.cellWidget(row, col)
        pitch_min_input.setSuffix(self._pitch_suffix(value))

        # update maximum value of pitch min cell
        col = self.track_columns.index("Pitch Max")
        pitch_max_input: TableSpinBox = self.table.cellWidget(row, col)
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
        pitch_max_input: TableSpinBox = self.table.cellWidget(row, col)
        pitch_max_input.setSuffix(self._pitch_suffix(value))

        # update maximum value of pitch min cell
        col = self.track_columns.index("Pitch Min")
        pitch_min_input: TableSpinBox = self.table.cellWidget(row, col)
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

    def _on_remove_track(self, row: int):
        rows = self._get_rows_for_bulk_edit(row)

        prompt = ""
        if len(rows) == 1:
            track_name = self.vis_config.tracks[rows[0]].name
            prompt = f"Are you sure you want to delete \"{track_name}\"?"
        else:
            prompt = f"Are you sure you want to delete the {len(rows)} selected tracks?"

        result = QMessageBox.question(
            self,
            "Confirm Track Delete",
            prompt,
            QMessageBox.Cancel | QMessageBox.Yes,
            QMessageBox.Cancel,
        )

        if result != QMessageBox.Yes:
            return

        for i in sorted(rows, reverse=True):
            del self.vis_config.tracks[i]
        
        self.refresh_ui()
        self.on_changes_callback()

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
    
    def _pitch_suffix(self, pitch: int) -> str:
        return f" ({MidiUtil.midi_pitch_to_note(pitch)})"

    # Helpers
    def _move_selected_tracks(self, delta: int):
        rows = sorted(self._get_selected_rows())
        if not rows:
            return

        tracks = self.vis_config.tracks
        n = len(tracks)

        # clamp so the whole selection stays in range (gaps between rows are preserved)
        delta = max(-rows[0], min(delta, n - 1 - rows[-1]))
        if delta == 0:
            return

        # reorder tracks based on move
        row_set = set(rows)
        targets = {r + delta: tracks[r] for r in rows}
        remaining = iter(t for i, t in enumerate(tracks) if i not in row_set)
        tracks[:] = [targets[i] if i in targets else next(remaining) for i in range(n)]

        # update table selection
        self._select_rows([r + delta for r in rows])

        # refresh UI and notify parent
        self.refresh_ui()
        self.on_changes_callback()

        # scroll table to ensure selection is in view
        # (after refresh UI so we don't fight the rebuild)
        new_rows = [r + delta for r in rows]
        edge_row = new_rows[-1] if delta > 0 else new_rows[0]
        self.table.scrollTo(
            self.table.model().index(edge_row, 0),
            QAbstractItemView.EnsureVisible,
        )

    def _select_rows(self, rows: list[int]):
        model = self.table.model()
        selection = QItemSelection()
        for row in rows:
            idx = model.index(row, 0)
            selection.select(idx, idx)

        self.table.selectionModel().select(
            selection,
            QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows,
        )


