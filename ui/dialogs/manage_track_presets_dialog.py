from dataclasses import dataclass
from enum import StrEnum

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
    QTableWidget, 
    QTableWidgetItem, 
    QVBoxLayout
)
from common import Color
from ui.common import WidgetUtil, Icons, LayoutUtil
from models import presets_config, Track, TrackPreset, VisConfig
from utility.q_util import QUtil

# UI Model for metadata about current tracks
@dataclass
class UICurrentTrack:
    name: str = ''
    pitch_min: int = 1
    pitch_max: int = 127
    selected_for_add: bool = False

    @staticmethod
    def create(track: Track):
        return UICurrentTrack(
            name = track.name,
            pitch_min = track.manual_pitch_min,
            pitch_max = track.manual_pitch_max,
            selected_for_add = False
        )

# Table model for current tracks
@dataclass
class TableCurrentTrack:
    name: str = ''
    pitch_min: int = 1
    pitch_max: int = 127

# UI Model for metadata about existing presets
@dataclass
class UITrackPreset:
    name: str = ''
    pitch_min: int = 1
    pitch_max: int = 127
    selected_for_delete: bool = False

    @staticmethod
    def create(preset: TrackPreset):
        return UITrackPreset(
            name = preset.name,
            pitch_min = preset.pitch_min,
            pitch_max = preset.pitch_max,
            selected_for_delete = False
        )

class TableTrackPresetState(StrEnum):
    DEFAULT = "Default", # existing preset, no changes
    NEW = "New", # newly added from current tracks
    UPDATED = "Updated", # replaced from current tracks
    DELETED = "Deleted", # marked for deletion from presets

# Table model for presets table
@dataclass
class TableTrackPreset:
    name: str = ''
    pitch_min: int = 1
    pitch_max: int = 127
    state: TableTrackPresetState = TableTrackPresetState.DEFAULT

# ----

class ManageTrackPresetsDialog(QDialog):
    def __init__(self, vis_config: VisConfig, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"Manage Track Presets")

        self.setModal(True)
        self.setFixedSize(800, 600)

        # -- Initialize UI Models --
        self.current_tracks: list[UICurrentTrack] = []
        for t in vis_config.tracks:
            if not t.override_pitch_min_max:
                continue

            # check if we already have an identical preset to this track
            preset = next((
                p for p in presets_config.track_presets if p.name == t.name
            ), None)

            if preset and t.manual_pitch_min == preset.pitch_min and t.manual_pitch_max == preset.pitch_max:
                continue # skip

            self.current_tracks.append(UICurrentTrack.create(t))

        self.existing_track_presets: list[UITrackPreset] = [
            UITrackPreset.create(p)
            for p in presets_config.track_presets
        ]
        self.existing_track_presets.sort(key=lambda p: p.name)

        # table data - recomputed any time user changes occur in _compute_table_data
        self.visible_current_tracks: list[TableCurrentTrack] = []
        self.visible_track_presets: list[TableTrackPreset] = []

        self._compute_table_data()

        # -- Create Controls --

        info_label = WidgetUtil.info_text(f"Select tracks to save to track presets. Only tracks with overridden values that aren't already in presets are shown.")

        # current tracks table
        current_tracks_label = QLabel("Current Tracks")
        self.current_tracks_columns = ["Name", "Pitch Min", "Pitch Max"]
        self.current_tracks_table = QTableWidget(0, len(self.current_tracks_columns))
        self.current_tracks_table.setHorizontalHeaderLabels(self.current_tracks_columns)
        self.current_tracks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.current_tracks_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.current_tracks_table.itemSelectionChanged.connect(self._on_current_tracks_selection_changed)
        # set whole-row multi-select
        self.current_tracks_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.current_tracks_table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # copy buttons
        self.copy_right_btn = WidgetUtil.icon_btn(Icons.chevron_right(), "Copy selected track(s) to presets")
        self.copy_right_btn.clicked.connect(self._copy_right)
        self.copy_all_btn = QPushButton() 
        self.copy_all_btn = WidgetUtil.icon_btn(Icons.chevron_double_right(), "Copy all tracks to presets")
        self.copy_all_btn.clicked.connect(self._copy_all_right)

        # track presets table
        track_presets_label = QLabel("Track Presets")
        self.track_presets_columns = ["Name", "Pitch Min", "Pitch Max", ""]
        self.track_presets_table = QTableWidget(0, len(self.track_presets_columns))
        self.track_presets_table.setHorizontalHeaderLabels(self.track_presets_columns)
        self.track_presets_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.track_presets_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.track_presets_table.itemSelectionChanged.connect(self._on_track_presets_selection_changed)
        # set whole-row multi-select
        self.track_presets_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.track_presets_table.setSelectionMode(QAbstractItemView.ExtendedSelection)

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

        # current tracks table
        current_tracks_layout = QVBoxLayout()
        current_tracks_layout.addWidget(current_tracks_label)
        current_tracks_layout.addWidget(self.current_tracks_table)

        # copy buttons
        copy_buttons_layout = QVBoxLayout()
        copy_buttons_layout.addStretch()
        copy_buttons_layout.addWidget(self.copy_right_btn)
        copy_buttons_layout.addWidget(self.copy_all_btn)
        copy_buttons_layout.addStretch()

        # track presets table
        track_presets_layout = QVBoxLayout()
        track_presets_layout.addWidget(track_presets_label)
        track_presets_layout.addWidget(self.track_presets_table)

        panels_layout = QHBoxLayout()
        panels_layout.addLayout(current_tracks_layout)
        panels_layout.addLayout(copy_buttons_layout)
        panels_layout.addLayout(track_presets_layout)

        main_layout.addLayout(panels_layout)
        main_layout.addWidget(button_box)

        self._refresh_ui()

    def _compute_table_data(self):
        # current tracks - any that aren't selected for add (since those
        # are over on the presets table now)
        self.visible_current_tracks = [
            t for t in self.current_tracks
            if not t.selected_for_add
        ]

        # track presets library table order:
        #   1. newly added
        #   2. updated
        #   3. existing (including marked for deletion)
        self.visible_track_presets = []
        for t in self.current_tracks:
            if t.selected_for_add:
                existing_preset_by_name = any(p.name == t.name for p in self.existing_track_presets)
                self.visible_track_presets.append(TableTrackPreset(
                    t.name, 
                    t.pitch_min, 
                    t.pitch_max, 
                    TableTrackPresetState.UPDATED if existing_preset_by_name else TableTrackPresetState.NEW
                ))
        
        for p in self.existing_track_presets:
            # skip any already in list (due to being added or updated from current tracks)
            already_in_list = any(x.name == p.name for x in self.visible_track_presets)
            if already_in_list:
                continue

            self.visible_track_presets.append(TableTrackPreset(
                p.name, 
                p.pitch_min, 
                p.pitch_max, 
                TableTrackPresetState.DELETED if p.selected_for_delete else TableTrackPresetState.DEFAULT
            ))

    def _refresh_buttons(self):
        enabled = len(self._get_selected_current_track_rows()) > 0
        self.copy_right_btn.setEnabled(enabled)

    def _refresh_ui(self):
        # prevent callbacks while populating table rows
        self.current_tracks_table.blockSignals(True)
        self.track_presets_table.blockSignals(True)

        # current tracks table
        self.current_tracks_table.setRowCount(len(self.visible_current_tracks))
        for row, track in enumerate(self.visible_current_tracks):
            col = 0

            # name
            name_item = QTableWidgetItem(track.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.current_tracks_table.setItem(row, col, name_item)
            col += 1

            # pitch min
            pitch_min_item = QTableWidgetItem(f"{track.pitch_min}")
            pitch_min_item.setFlags(pitch_min_item.flags() & ~Qt.ItemIsEditable)
            pitch_min_item.setTextAlignment(Qt.AlignCenter)
            self.current_tracks_table.setItem(row, col, pitch_min_item)
            col += 1

            # pitch max
            pitch_max_item = QTableWidgetItem(f"{track.pitch_max}")
            pitch_max_item.setFlags(pitch_max_item.flags() & ~Qt.ItemIsEditable)
            pitch_max_item.setTextAlignment(Qt.AlignCenter)
            self.current_tracks_table.setItem(row, col, pitch_max_item)
            col += 1        

        # track presets table
        self.track_presets_table.setRowCount(len(self.visible_track_presets))
        for row, preset in enumerate(self.visible_track_presets):
            col = 0

            font = QFont()
            color = QUtil.rgb_to_qcolor(Color.WHITE)
            if preset.state in [TableTrackPresetState.NEW, TableTrackPresetState.UPDATED]:
                font.setBold(True)
            if preset.state == TableTrackPresetState.DELETED:
                font.setStrikeOut(True)
                color = QUtil.rgb_to_qcolor(Color.LIGHT_GRAY)

            # name
            preset_name = ""
            match preset.state:
                case TableTrackPresetState.NEW:
                    preset_name = "(New) "
                case TableTrackPresetState.UPDATED:
                    preset_name = "(Edit) "
            preset_name += preset.name
            name_item = QTableWidgetItem(preset_name)
            name_item.setFont(font)
            name_item.setForeground(color)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.track_presets_table.setItem(row, col, name_item)
            col += 1

            # pitch min
            pitch_min_item = QTableWidgetItem(f"{preset.pitch_min}")
            pitch_min_item.setFont(font)
            pitch_min_item.setForeground(color)
            pitch_min_item.setFlags(pitch_min_item.flags() & ~Qt.ItemIsEditable)
            pitch_min_item.setTextAlignment(Qt.AlignCenter)
            self.track_presets_table.setItem(row, col, pitch_min_item)
            col += 1

            # pitch max
            pitch_max_item = QTableWidgetItem(f"{preset.pitch_max}")
            pitch_max_item.setFont(font)
            pitch_max_item.setForeground(color)
            pitch_max_item.setFlags(pitch_max_item.flags() & ~Qt.ItemIsEditable)
            pitch_max_item.setTextAlignment(Qt.AlignCenter)
            self.track_presets_table.setItem(row, col, pitch_max_item)
            col += 1

            # delete button
            delete_btn = QPushButton()
            delete_btn.setIcon(Icons.trash_can())
            delete_btn.clicked.connect(lambda _, row=row: self._on_delete_preset(row))
            self.track_presets_table.setCellWidget(row, col, LayoutUtil.center(delete_btn))
            col += 1

        # resume callbacks
        self.current_tracks_table.blockSignals(False)
        self.track_presets_table.blockSignals(False)

        self._refresh_buttons()

    def _on_current_tracks_selection_changed(self):
        # clear selection on track presets table, if exists
        self.track_presets_table.blockSignals(True)
        self.track_presets_table.clearSelection()
        self.track_presets_table.blockSignals(False)

        self._refresh_buttons()

    def _on_track_presets_selection_changed(self):
        # clear selection on current tracks table, if exists
        self.current_tracks_table.blockSignals(True)
        self.current_tracks_table.clearSelection()
        self.current_tracks_table.blockSignals(False)

        self._refresh_buttons()

    def _copy_right(self):
        # get selected current tracks and mark for add
        tracks = self._get_selected_current_tracks()
        if len(tracks) == 0:
            return
        
        for t in tracks:
            t.selected_for_add = True

            # if this will overlap an existing preset, undo
            # its mark for deletion, if present
            existing_preset = next((
                p for p in self.existing_track_presets 
                if p.name == t.name
            ), None)
            if existing_preset:
                existing_preset.selected_for_delete = False

        self._compute_table_data()
        self._refresh_ui()

    def _copy_all_right(self):
        # mark all current tracks for add
        for t in self.current_tracks:
            t.selected_for_add = True

            # if this will overlap an existing preset, undo
            # its mark for deletion, if present
            existing_preset = next((
                p for p in self.existing_track_presets 
                if p.name == t.name
            ), None)
            if existing_preset:
                existing_preset.selected_for_delete = False

        self._compute_table_data()
        self._refresh_ui()

    def _on_delete_preset(self, row: int):
        # get all selected rows
        rows = self._get_selected_track_preset_rows()
        if row not in rows:
            rows.append(row)

        presets = [self.visible_track_presets[row] for row in rows]

        # Special case - if, across the selection, there's a mix of Default and Deleted states
        # on existing presets, then we'll force all of these to Deleted. Makes a cleaner UX.
        default_present = any(x.state == TableTrackPresetState.DEFAULT for x in presets)
        deleted_present = any(x.state == TableTrackPresetState.DELETED for x in presets)
        force_existing_to_deleted = default_present and deleted_present

        for selected_preset in presets:
            if selected_preset.state in [TableTrackPresetState.NEW, TableTrackPresetState.UPDATED]:
                # this is a current track marked for adding - un-add it
                track = next((
                    t for t in self.current_tracks 
                    if t.name == selected_preset.name
                ), None)
                if track:
                    track.selected_for_add = False
            else:
                # this is an existing preset - toggle its deleted state
                preset = next((
                    p for p in self.existing_track_presets
                    if p.name == selected_preset.name
                ), None)
                if preset:
                    if force_existing_to_deleted:
                        preset.selected_for_delete = True
                    else:
                        preset.selected_for_delete = not preset.selected_for_delete

        self._compute_table_data()
        self._refresh_ui()

    def _save(self):
        # create new track preset list and save
        presets: list[TrackPreset] = []

        # add any added or updated from current tracks
        for t in self.current_tracks:
            if t.selected_for_add:
                presets.append(TrackPreset(
                    name=t.name, 
                    pitch_min=t.pitch_min, 
                    pitch_max=t.pitch_max
                ))

        # add any existing tracks not marked for delete or copied over
        for p in self.existing_track_presets:
            if not p.selected_for_delete and not any(x.name == p.name for x in presets):
                presets.append(TrackPreset(
                    name=p.name, 
                    pitch_min=p.pitch_min, 
                    pitch_max=p.pitch_max
                ))

        presets.sort(key=lambda p: p.name)

        presets_config.track_presets = presets
        presets_config.save()

        self.accept()

    # Getters
    def _get_selected_current_track_rows(self) -> list[int]:
        selected_rows: set[int] = set()

        for selection_range in self.current_tracks_table.selectedRanges():
            for row in range(selection_range.topRow(), selection_range.bottomRow() + 1):
                selected_rows.add(row)

        return sorted(selected_rows)

    def _get_selected_current_tracks(self) -> list[UICurrentTrack]:
        rows = self._get_selected_current_track_rows()
        tracks = []
        for row in rows:
            if row >= 0 and row < len(self.visible_current_tracks):
                # get actual UI model track by name of this row
                track = next((
                    t for t in self.current_tracks 
                    if t.name == self.visible_current_tracks[row].name
                ), None)
                if track:
                    tracks.append(track)
        return tracks

    def _get_selected_track_preset_rows(self) -> list[int]:
        selected_rows: set[int] = set()

        for selection_range in self.track_presets_table.selectedRanges():
            for row in range(selection_range.topRow(), selection_range.bottomRow() + 1):
                selected_rows.add(row)

        return sorted(selected_rows)