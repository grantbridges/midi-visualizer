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
from common import Color, RGB
from ui.common import WidgetUtil, Icons, LayoutUtil, ColorButton, TableCheckBox
from models import presets_config, TrackGroup, TrackGroupPreset, VisConfig
from utility import QUtil, Util

# UI Model for metadata about current track groups
@dataclass
class UICurrentTrackGroup:
    name: str = ''
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    bar_height_ratio: float = .02
    bar_sec_across_screen: float = 7.1
    pitch_offset: int = 0 # -127 - 127
    note_sparks_enabled: bool = True
    note_bounce_enabled: bool = False
    note_velocity_fx_enabled: bool = True
    selected_for_add: bool = False

    @staticmethod
    def create(track_group: TrackGroup):
        return UICurrentTrackGroup(
            name = track_group.name,
            color = track_group.color,
            alpha = track_group.alpha,
            bar_height_ratio = track_group.bar_height_ratio,
            bar_sec_across_screen = track_group.bar_sec_across_screen,
            pitch_offset = track_group.pitch_offset,
            note_sparks_enabled = track_group.note_sparks_enabled,
            note_bounce_enabled = track_group.note_bounce_enabled,
            note_velocity_fx_enabled = track_group.note_velocity_fx_enabled,
            selected_for_add = False
        )

# Table model for current track groups
@dataclass
class TableCurrentTrackGroup:
    name: str = ''
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    bar_height_ratio: float = .02
    bar_sec_across_screen: float = 7.1
    pitch_offset: int = 0 # -127 - 127
    note_sparks_enabled: bool = True
    note_bounce_enabled: bool = False
    note_velocity_fx_enabled: bool = True

    @staticmethod
    def create(track_group: UICurrentTrackGroup):
        return TableCurrentTrackGroup(
            name = track_group.name,
            color = track_group.color,
            alpha = track_group.alpha,
            bar_height_ratio = track_group.bar_height_ratio,
            bar_sec_across_screen = track_group.bar_sec_across_screen,
            pitch_offset = track_group.pitch_offset,
            note_sparks_enabled = track_group.note_sparks_enabled,
            note_bounce_enabled = track_group.note_bounce_enabled,
            note_velocity_fx_enabled = track_group.note_velocity_fx_enabled
        )

# UI Model for metadata about existing presets
@dataclass
class UITrackGroupPreset:
    name: str = ''
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    bar_height_ratio: float = .02
    bar_sec_across_screen: float = 7.1
    pitch_offset: int = 0 # -127 - 127
    note_sparks_enabled: bool = True
    note_bounce_enabled: bool = False
    note_velocity_fx_enabled: bool = True
    selected_for_delete: bool = False

    @staticmethod
    def create(preset: TrackGroupPreset):
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
            selected_for_delete = False
        )

class TableTrackGroupPresetState(StrEnum):
    DEFAULT = "Default", # existing preset, no changes
    NEW = "New", # newly added from current track groups
    UPDATED = "Updated", # replaced from current track groups
    DELETED = "Deleted", # marked for deletion from presets

# Table model for presets table
@dataclass
class TableTrackGroupPreset:
    name: str = ''
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    bar_height_ratio: float = .02
    bar_sec_across_screen: float = 7.1
    pitch_offset: int = 0 # -127 - 127
    note_sparks_enabled: bool = True
    note_bounce_enabled: bool = False
    note_velocity_fx_enabled: bool = True
    state: TableTrackGroupPresetState = TableTrackGroupPresetState.DEFAULT

    @staticmethod
    def create_from_track_group(track_group: UICurrentTrackGroup, is_existing: bool):
        return TableTrackGroupPreset(
            name = track_group.name, 
            color = track_group.color,
            alpha = track_group.alpha,
            bar_height_ratio = track_group.bar_height_ratio,
            bar_sec_across_screen = track_group.bar_sec_across_screen,
            pitch_offset = track_group.pitch_offset,
            note_sparks_enabled = track_group.note_sparks_enabled,
            note_bounce_enabled = track_group.note_bounce_enabled,
            note_velocity_fx_enabled = track_group.note_velocity_fx_enabled,
            state = TableTrackGroupPresetState.UPDATED if is_existing else TableTrackGroupPresetState.NEW
        )
    
    @staticmethod
    def create_from_preset(preset: UITrackGroupPreset):
        return TableTrackGroupPreset(
            name = preset.name, 
            color = preset.color,
            alpha = preset.alpha,
            bar_height_ratio = preset.bar_height_ratio,
            bar_sec_across_screen = preset.bar_sec_across_screen,
            pitch_offset = preset.pitch_offset,
            note_sparks_enabled = preset.note_sparks_enabled,
            note_bounce_enabled = preset.note_bounce_enabled,
            note_velocity_fx_enabled = preset.note_velocity_fx_enabled,
            state = TableTrackGroupPresetState.DELETED if preset.selected_for_delete else TableTrackGroupPresetState.DEFAULT
        )

# ----

class ManageTrackGroupPresetsDialog(QDialog):
    def __init__(self, vis_config: VisConfig, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"Manage Track Group Presets")

        self.setModal(True)
        min_width, min_height = 800, 500
        self.setMinimumSize(min_width, min_height)
        self.resize(min_width, min_height)

        # -- Initialize UI Models --
        self.current_track_groups: list[UICurrentTrackGroup] = [
            UICurrentTrackGroup.create(t) 
            for t in vis_config.track_groups
        ]

        self.existing_track_group_presets: list[UITrackGroupPreset] = [
            UITrackGroupPreset.create(p)
            for p in presets_config.track_group_presets
        ]
        self.existing_track_group_presets.sort(key=lambda p: p.name)

        # table data - recomputed any time user changes occur in _compute_table_data
        self.table_current_track_groups: list[TableCurrentTrackGroup] = []
        self.table_track_group_presets: list[TableTrackGroupPreset] = []

        self._compute_table_data()

        # -- Create Controls --

        info_label = WidgetUtil.info_text(f"Select track groups to save to track group presets.")

        # current track groups table
        current_track_groups_label = QLabel("Current Track Groups")
        self.current_track_groups_columns = ["Name", "Opacity", "Note\nSparks", "Note\nBounce", "Note\nVel. Fx", "Bar\nHeight", "Speed", "Pitch\nOffset"]
        self.current_track_groups_table = QTableWidget(0, len(self.current_track_groups_columns))
        self.current_track_groups_table.setHorizontalHeaderLabels(self.current_track_groups_columns)
        self.current_track_groups_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.current_track_groups_table.itemSelectionChanged.connect(self._on_current_track_groups_selection_changed)
        self.current_track_groups_table.verticalHeader().setVisible(False) # hide row numbers
        # set whole-row multi-select
        self.current_track_groups_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.current_track_groups_table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # copy buttons
        self.copy_right_btn = WidgetUtil.icon_btn(Icons.chevron_right(), "Copy selected track group(s) to presets")
        self.copy_right_btn.clicked.connect(self._copy_right)
        self.copy_all_btn = QPushButton() 
        self.copy_all_btn = WidgetUtil.icon_btn(Icons.chevron_double_right(), "Copy all track groups to presets")
        self.copy_all_btn.clicked.connect(self._copy_all_right)

        # track presets table
        track_group_presets_label = QLabel("Track Group Presets")
        self.track_presets_columns = ["", "", "Name", "Opacity", "Note\nSparks", "Note\nBounce", "Note\nVel. Fx", "Bar\nHeight", "Speed", "Pitch\nOffset"]
        self.track_group_presets_table = QTableWidget(0, len(self.track_presets_columns))
        self.track_group_presets_table.setHorizontalHeaderLabels(self.track_presets_columns)
        self.track_group_presets_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.track_group_presets_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.track_group_presets_table.horizontalHeader().resizeSection(1, 40) # status column
        self.track_group_presets_table.itemSelectionChanged.connect(self._on_track_group_presets_selection_changed)
        self.track_group_presets_table.verticalHeader().setVisible(False) # hide row numbers
        # set whole-row multi-select
        self.track_group_presets_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.track_group_presets_table.setSelectionMode(QAbstractItemView.ExtendedSelection)

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
        main_layout.addSpacing(5)

        # current track groups table
        current_track_groups_layout = QVBoxLayout()
        current_track_groups_layout.addWidget(current_track_groups_label)
        current_track_groups_layout.addWidget(self.current_track_groups_table)

        # copy buttons
        copy_buttons_layout = QVBoxLayout()
        copy_buttons_layout.addStretch()
        copy_buttons_layout.addWidget(self.copy_right_btn)
        copy_buttons_layout.addWidget(self.copy_all_btn)
        copy_buttons_layout.addStretch()

        # track group presets table
        track_group_presets_layout = QVBoxLayout()
        track_group_presets_layout.addWidget(track_group_presets_label)
        track_group_presets_layout.addWidget(self.track_group_presets_table)

        panels_layout = QHBoxLayout()
        panels_layout.addLayout(current_track_groups_layout)
        panels_layout.addLayout(copy_buttons_layout)
        panels_layout.addLayout(track_group_presets_layout)

        main_layout.addLayout(panels_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.changes_label, 1)
        bottom_layout.addWidget(button_box)

        main_layout.addLayout(bottom_layout)

        self._refresh_ui()

    def _compute_table_data(self):
        # current track grouops - any that aren't selected for add (since those
        # are over on the presets table now)
        self.table_current_track_groups = [
            TableCurrentTrackGroup.create(t)
            for t in self.current_track_groups if not t.selected_for_add
        ]

        # track group presets library table order:
        #   1. newly added
        #   2. updated
        #   3. existing (including marked for deletion)

        # append new & updated from current track groups
        self.table_track_group_presets = []
        for tg in self.current_track_groups:
            if tg.selected_for_add:
                existing_preset_by_name = any(p.name == tg.name for p in self.existing_track_group_presets)
                self.table_track_group_presets.append(
                    TableTrackGroupPreset.create_from_track_group(tg, existing_preset_by_name)
                )

        # append existing & deleted from existing presets
        for p in self.existing_track_group_presets:
            # skip any already in list (due to being added or updated from current track groups)
            already_in_list = any(x.name == p.name for x in self.table_track_group_presets)
            if already_in_list:
                continue

            self.table_track_group_presets.append(
                TableTrackGroupPreset.create_from_preset(p)
            )

    def _refresh_buttons(self):
        enabled = len(self._get_selected_current_track_group_rows()) > 0
        self.copy_right_btn.setEnabled(enabled)

    def _refresh_changes_label(self):
        changes = []
        added_count = sum(
            1 for t in self.current_track_groups 
            if t.selected_for_add and not any(t.name == p.name for p in self.existing_track_group_presets)
        )
        updated_count = sum(
            1 for t in self.current_track_groups 
            if t.selected_for_add and any(t.name == p.name for p in self.existing_track_group_presets)
        )
        deleted_count = sum(
            1 for p in self.existing_track_group_presets
            if p.selected_for_delete
        )

        if added_count > 0:
            changes.append(f"{added_count} added")
        if updated_count > 0:
            changes.append(f"{updated_count} updated")
        if deleted_count > 0:
            changes.append(f"{deleted_count} deleted")

        self.changes_label.setText(", ".join(changes))

    def _refresh_ui(self):
        # prevent callbacks while populating table rows
        self.current_track_groups_table.blockSignals(True)
        self.track_group_presets_table.blockSignals(True)

        # current track groups table
        self.current_track_groups_table.setRowCount(len(self.table_current_track_groups))
        for row, track_group in enumerate(self.table_current_track_groups):
            col = 0

            # name (double up with color to save space)
            color_btn = ColorButton(
                color=track_group.color, 
                read_only=True, 
                override_text=track_group.name
            )
            r, g, b = track_group.color
            color_btn.setToolTip(f"{r}, {g}, {b}")
            self.current_track_groups_table.setCellWidget(row, col, color_btn)
            col += 1

            # opacity
            opacity = Util.int_internal_to_display(
                internal_value=track_group.alpha,
                display_min=0, 
                display_max=100, 
                internal_min=0, 
                internal_max=255
            )
            opacity_item = QTableWidgetItem(f"{opacity}")
            opacity_item.setFlags(opacity_item.flags() & ~Qt.ItemIsEditable)
            opacity_item.setTextAlignment(Qt.AlignCenter)
            self.current_track_groups_table.setItem(row, col, opacity_item)
            col += 1

            # sparks
            checkbox = TableCheckBox(track_group.note_sparks_enabled)
            checkbox.setReadOnly(True)
            self.current_track_groups_table.setCellWidget(row, col, checkbox)
            col += 1
    
            # bounce
            checkbox = TableCheckBox(track_group.note_bounce_enabled)
            checkbox.setReadOnly(True)
            self.current_track_groups_table.setCellWidget(row, col, checkbox)
            col += 1
    
            # velocity fx
            checkbox = TableCheckBox(track_group.note_velocity_fx_enabled)
            checkbox.setReadOnly(True)
            self.current_track_groups_table.setCellWidget(row, col, checkbox)
            col += 1
    
            # bar height ratio
            bar_height = Util.float_internal_to_display(
                internal_value=track_group.bar_height_ratio,
                internal_min=0.001, 
                internal_max=1.000, 
                display_min=1.0, 
                display_max=10.0
            )
            bar_height_item = QTableWidgetItem(f"{bar_height:.2f}")
            bar_height_item.setFlags(bar_height_item.flags() & ~Qt.ItemIsEditable)
            bar_height_item.setTextAlignment(Qt.AlignCenter)
            self.current_track_groups_table.setItem(row, col, bar_height_item)
            col += 1
    
            # pixels/sec
            sec_across_screen = Util.float_internal_to_display(
                internal_value=track_group.bar_sec_across_screen,
                internal_min=10.0,
                internal_max=0.1,
                display_min=0.1,
                display_max=10.0
            )
            sec_across_screen_item = QTableWidgetItem(f"{sec_across_screen:.1f}")
            sec_across_screen_item.setFlags(sec_across_screen_item.flags() & ~Qt.ItemIsEditable)
            sec_across_screen_item.setTextAlignment(Qt.AlignCenter)
            self.current_track_groups_table.setItem(row, col, sec_across_screen_item)
            col += 1
    
            # pitch offset
            pitch_offset_item = QTableWidgetItem(f"{track_group.pitch_offset}")
            pitch_offset_item.setFlags(pitch_offset_item.flags() & ~Qt.ItemIsEditable)
            pitch_offset_item.setTextAlignment(Qt.AlignCenter)
            self.current_track_groups_table.setItem(row, col, pitch_offset_item)
            col += 1

        # track group presets table
        self.track_group_presets_table.setRowCount(len(self.table_track_group_presets))
        for row, preset in enumerate(self.table_track_group_presets):
            col = 0

            font = QFont()
            color = QUtil.rgb_to_qcolor(Color.WHITE)
            del_icon = Icons.trash_can()
            if preset.state in [TableTrackGroupPresetState.NEW, TableTrackGroupPresetState.UPDATED]:
                font.setBold(True)
                del_icon = Icons.chevron_left()
            if preset.state == TableTrackGroupPresetState.DELETED:
                font.setStrikeOut(True)
                color = QUtil.rgb_to_qcolor(Color.LIGHT_GRAY)

            # delete button
            delete_btn = WidgetUtil.icon_btn(del_icon)
            delete_btn.clicked.connect(lambda _, row=row: self._on_delete_preset(row))
            self.track_group_presets_table.setCellWidget(row, col, LayoutUtil.center(delete_btn))
            col += 1

            # status
            status_font = QFont()
            status_font.setPointSizeF(font.pointSizeF() * 0.6)
            status_name = ""
            match preset.state:
                case TableTrackGroupPresetState.NEW:
                    status_name = "New"
                case TableTrackGroupPresetState.UPDATED:
                    status_name = "Update"
                case TableTrackGroupPresetState.DELETED:
                    status_name = "Delete"
            status_item = QTableWidgetItem(status_name)
            status_item.setFont(status_font)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            self.track_group_presets_table.setItem(row, col, status_item)
            col += 1
            
            # name (double up with color to save space)
            color_btn = ColorButton(
                color=preset.color, 
                read_only=True, 
                override_text=preset.name
            )
            r, g, b = preset.color
            color_btn.setToolTip(f"{r}, {g}, {b}")
            color_btn.setFont(font)
            color_btn.setEnabled(preset.state != TableTrackGroupPresetState.DELETED)
            self.track_group_presets_table.setCellWidget(row, col, color_btn)
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
            opacity_item.setForeground(color)
            opacity_item.setFlags(opacity_item.flags() & ~Qt.ItemIsEditable)
            opacity_item.setTextAlignment(Qt.AlignCenter)
            self.track_group_presets_table.setItem(row, col, opacity_item)
            col += 1

            # sparks
            checkbox = TableCheckBox(preset.note_sparks_enabled)
            checkbox.setReadOnly(True)
            checkbox.setEnabled(preset.state != TableTrackGroupPresetState.DELETED)
            self.track_group_presets_table.setCellWidget(row, col, checkbox)
            col += 1

            # bounce
            checkbox = TableCheckBox(preset.note_bounce_enabled)
            checkbox.setReadOnly(True)
            checkbox.setEnabled(preset.state != TableTrackGroupPresetState.DELETED)
            self.track_group_presets_table.setCellWidget(row, col, checkbox)
            col += 1

            # velocity fx
            checkbox = TableCheckBox(preset.note_velocity_fx_enabled)
            checkbox.setReadOnly(True)
            checkbox.setEnabled(preset.state != TableTrackGroupPresetState.DELETED)
            self.track_group_presets_table.setCellWidget(row, col, checkbox)
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
            bar_height_item.setForeground(color)
            bar_height_item.setFlags(bar_height_item.flags() & ~Qt.ItemIsEditable)
            bar_height_item.setTextAlignment(Qt.AlignCenter)
            self.track_group_presets_table.setItem(row, col, bar_height_item)
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
            sec_across_screen_item.setForeground(color)
            sec_across_screen_item.setFlags(sec_across_screen_item.flags() & ~Qt.ItemIsEditable)
            sec_across_screen_item.setTextAlignment(Qt.AlignCenter)
            self.track_group_presets_table.setItem(row, col, sec_across_screen_item)
            col += 1

            # pitch offset
            pitch_offset_item = QTableWidgetItem(f"{preset.pitch_offset}")
            pitch_offset_item.setFont(font)
            pitch_offset_item.setForeground(color)
            pitch_offset_item.setFlags(pitch_offset_item.flags() & ~Qt.ItemIsEditable)
            pitch_offset_item.setTextAlignment(Qt.AlignCenter)
            self.track_group_presets_table.setItem(row, col, pitch_offset_item)
            col += 1

        # resume callbacks
        self.current_track_groups_table.blockSignals(False)
        self.track_group_presets_table.blockSignals(False)

        self._refresh_buttons()
        self._refresh_changes_label()

    def _on_current_track_groups_selection_changed(self):
        # clear selection on track group presets table, if exists
        self.track_group_presets_table.blockSignals(True)
        self.track_group_presets_table.clearSelection()
        self.track_group_presets_table.blockSignals(False)

        self._refresh_buttons()

    def _on_track_group_presets_selection_changed(self):
        # clear selection on current track groups table, if exists
        self.current_track_groups_table.blockSignals(True)
        self.current_track_groups_table.clearSelection()
        self.current_track_groups_table.blockSignals(False)

        self._refresh_buttons()

    def _copy_right(self):
        # get selected current track groups and mark for add
        track_groups = self._get_selected_current_track_groups()
        if len(track_groups) == 0:
            return
        
        for t in track_groups:
            t.selected_for_add = True

            # if this will overlap an existing preset, undo
            # its mark for deletion, if present
            existing_preset = next((
                p for p in self.existing_track_group_presets 
                if p.name == t.name
            ), None)
            if existing_preset:
                existing_preset.selected_for_delete = False

        self._compute_table_data()
        self._refresh_ui()

    def _copy_all_right(self):
        # mark all current track groups for add
        for t in self.current_track_groups:
            t.selected_for_add = True

            # if this will overlap an existing preset, undo
            # its mark for deletion, if present
            existing_preset = next((
                p for p in self.existing_track_group_presets 
                if p.name == t.name
            ), None)
            if existing_preset:
                existing_preset.selected_for_delete = False

        self._compute_table_data()
        self._refresh_ui()

    def _on_delete_preset(self, row: int):
        # get all selected rows
        rows = self._get_selected_track_group_preset_rows()
        if len(rows) == 1:
            # if only one other row is selected, ignore
            rows = []

        if row not in rows:
            rows.append(row)

        presets = [self.table_track_group_presets[row] for row in rows]

        # Special case - if, across the selection, there's a mix of Default and Deleted states
        # on existing presets, then we'll force all of these to Deleted. Makes a cleaner UX.
        default_present = any(x.state == TableTrackGroupPresetState.DEFAULT for x in presets)
        deleted_present = any(x.state == TableTrackGroupPresetState.DELETED for x in presets)
        force_existing_to_deleted = default_present and deleted_present

        for selected_preset in presets:
            if selected_preset.state in [TableTrackGroupPresetState.NEW, TableTrackGroupPresetState.UPDATED]:
                # this is a current track marked for adding - un-add it
                track = next((
                    t for t in self.current_track_groups 
                    if t.name == selected_preset.name
                ), None)
                if track:
                    track.selected_for_add = False
            else:
                # this is an existing preset - toggle its deleted state
                preset = next((
                    p for p in self.existing_track_group_presets
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
        presets: list[TrackGroupPreset] = []

        # add any added or updated from current track groups
        for tg in self.current_track_groups:
            if tg.selected_for_add:
                presets.append(TrackGroupPreset(
                    name = tg.name,
                    color = tg.color,
                    alpha = tg.alpha,
                    bar_height_ratio = tg.bar_height_ratio,
                    bar_sec_across_screen = tg.bar_sec_across_screen,
                    pitch_offset = tg.pitch_offset,
                    note_sparks_enabled = tg.note_sparks_enabled,
                    note_bounce_enabled = tg.note_bounce_enabled,
                    note_velocity_fx_enabled = tg.note_velocity_fx_enabled
                ))

        # add any existing track groups not marked for delete or copied over
        for p in self.existing_track_group_presets:
            if not p.selected_for_delete and not any(x.name == p.name for x in presets):
                presets.append(TrackGroupPreset(
                    name = p.name,
                    color = p.color,
                    alpha = p.alpha,
                    bar_height_ratio = p.bar_height_ratio,
                    bar_sec_across_screen = p.bar_sec_across_screen,
                    pitch_offset = p.pitch_offset,
                    note_sparks_enabled = p.note_sparks_enabled,
                    note_bounce_enabled = p.note_bounce_enabled,
                    note_velocity_fx_enabled = p.note_velocity_fx_enabled
                ))

        presets.sort(key=lambda p: p.name)

        presets_config.track_group_presets = presets
        presets_config.save()

        self.accept()

    # Getters
    def _get_selected_current_track_group_rows(self) -> list[int]:
        selected_rows: set[int] = set()

        for selection_range in self.current_track_groups_table.selectedRanges():
            for row in range(selection_range.topRow(), selection_range.bottomRow() + 1):
                selected_rows.add(row)

        return sorted(selected_rows)

    def _get_selected_current_track_groups(self) -> list[UICurrentTrackGroup]:
        rows = self._get_selected_current_track_group_rows()
        track_groups = []
        for row in rows:
            if row >= 0 and row < len(self.table_current_track_groups):
                # get actual UI model track by name of this row
                track = next((
                    t for t in self.current_track_groups 
                    if t.name == self.table_current_track_groups[row].name
                ), None)
                if track:
                    track_groups.append(track)
        return track_groups

    def _get_selected_track_group_preset_rows(self) -> list[int]:
        selected_rows: set[int] = set()

        for selection_range in self.track_group_presets_table.selectedRanges():
            for row in range(selection_range.topRow(), selection_range.bottomRow() + 1):
                selected_rows.add(row)

        return sorted(selected_rows)