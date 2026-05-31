from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QHeaderView,
    QStyle,
    QSizePolicy
)

from common.types import RGB
from models import VisConfig, TrackGroup
from ui.common import ColorButton, TableCheckbox, TableSpinbox, TableDoubleSpinbox
import copy

class TrackGroupsTab(QWidget):
    def __init__(self, on_changes_callback: object, vis_config: VisConfig):
        super().__init__()

        self.on_changes_callback = on_changes_callback
        self.vis_config = vis_config

        # working ui model
        self.track_groups = copy.deepcopy(self.vis_config.track_groups)

        # create controls
        self.add_row_btn = QPushButton("Add Group")
        self.add_row_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.add_row_btn.clicked.connect(self._on_add_group)

        self.track_columns = ["", "", "Name", "Visible", "Color", "Alpha", "Bar Height", "Speed (sec)", "Vert. Padding", "Vert. Offset", ""]
        self.table = QTableWidget(0, len(self.track_columns))
        self.table.setHorizontalHeaderLabels(self.track_columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # set button columns to shrink
        for col in [0, 1, len(self.track_columns) - 1]:
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self.table.itemChanged.connect(self._on_item_changed)

        # layout controls
        v_layout = QVBoxLayout(self)
        v_layout.addWidget(self.add_row_btn)
        v_layout.addWidget(self.table)

    def refresh_ui(self):
        # prevent callbacks while populating
        self.table.blockSignals(True)

        self.table.setRowCount(len(self.track_groups))
        style = self.style()

        for row, track_group in enumerate(self.track_groups):
            col = 0

            # move up button
            up_btn = QPushButton()
            up_btn.setIcon(style.standardIcon(QStyle.SP_ArrowUp))
            up_btn.setFixedSize(32, 24)
            up_btn.clicked.connect(lambda _, row=row: self._on_move_group_up(row))
            self.table.setCellWidget(row, col, up_btn)
            col += 1

            # move down button
            down_btn = QPushButton()
            down_btn.setIcon(style.standardIcon(QStyle.SP_ArrowDown))
            down_btn.setFixedSize(32, 24)
            down_btn.clicked.connect(lambda _, row=row: self._on_move_group_down(row))
            self.table.setCellWidget(row, col, down_btn)
            col += 1

            # name
            name_cell = QTableWidgetItem(track_group.name)
            self.table.setItem(row, col, name_cell)
            col += 1

            # visible
            checkbox = TableCheckbox(track_group.visible)
            checkbox.valueChanged.connect(lambda checked, row=row: self._on_visible_changed(row, checked))
            self.table.setCellWidget(row, col, checkbox)
            col += 1

            # color button
            color_btn = ColorButton(track_group.color)
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

            # bar height ratio
            bar_height = TableDoubleSpinbox()
            bar_height.setDecimals(3)
            bar_height.setRange(0.001, 1.000)
            bar_height.setSingleStep(.001)
            bar_height.setValue(track_group.bar_height_ratio)
            bar_height.valueChanged.connect(lambda height, row=row: self._on_bar_height_changed(row, height))
            self.table.setCellWidget(row, col, bar_height)
            col += 1

            # pixels/sec
            sec_across_screen = TableDoubleSpinbox()
            sec_across_screen.setDecimals(1)
            sec_across_screen.setRange(0.1, 5.0)
            sec_across_screen.setSingleStep(.1)
            sec_across_screen.setValue(track_group.bar_sec_across_screen)
            sec_across_screen.valueChanged.connect(lambda speed, row=row: self._on_bar_speed_changed(row, speed))
            self.table.setCellWidget(row, col, sec_across_screen)
            col += 1

            # vertical padding
            vertical_padding = TableDoubleSpinbox()
            vertical_padding.setDecimals(2)
            vertical_padding.setRange(0.00, 1.00)
            vertical_padding.setSingleStep(.01)
            vertical_padding.setValue(track_group.vertical_padding_ratio)
            vertical_padding.valueChanged.connect(lambda pad, row=row: self._on_vert_padding_changed(row, pad))
            self.table.setCellWidget(row, col, vertical_padding)
            col += 1

            # vertical offset
            vertical_offset = TableDoubleSpinbox()
            vertical_offset.setDecimals(2)
            vertical_offset.setRange(-1.00, 1.00)
            vertical_offset.setSingleStep(.01)
            vertical_offset.setValue(track_group.vertical_offset_ratio)
            vertical_offset.valueChanged.connect(lambda offset, row=row: self._on_vert_offset_changed(row, offset))
            self.table.setCellWidget(row, col, vertical_offset)
            col += 1

            # delete button
            delete_btn = QPushButton()
            delete_btn.setIcon(style.standardIcon(QStyle.SP_TrashIcon))
            delete_btn.setFixedSize(32, 24)
            delete_btn.setStyleSheet("QPushButton { background-color: #aa3333}") # red
            delete_btn.clicked.connect(lambda _, row=row: self._on_remove_group(row))

            self.table.setCellWidget(row, col, delete_btn)
            col += 1

        # resume callbacks
        self.table.blockSignals(False)

    def update_model(self):
        # copy our ui model back to vis config
        groups = copy.deepcopy(self.track_groups)
        self.vis_config.update_track_groups(groups)

    # Callbacks
    def _on_add_group(self):
        track_group = TrackGroup(name = f"Group {len(self.track_groups)+1}")
        self.track_groups.append(track_group)
        self.refresh_ui()

        self.on_changes_callback()

    def _on_remove_group(self, row: int):
        if 0 <= row < len(self.track_groups):
            self.track_groups.pop(row)
            self.refresh_ui()

            self.on_changes_callback()

    def _on_move_group_up(self, row: int):
        if row > 0:
            # swap
            self.track_groups[row-1], self.track_groups[row] = self.track_groups[row], self.track_groups[row-1]
            self.refresh_ui()

            self.on_changes_callback()

    def _on_move_group_down(self, row: int):
        if row < len(self.track_groups) - 1:
            # swap
            self.track_groups[row+1], self.track_groups[row] = self.track_groups[row], self.track_groups[row+1]
            self.refresh_ui()

            self.on_changes_callback()

    def _on_item_changed(self, item: QTableWidgetItem):
        row = item.row()
        col = item.column()

        track_group = self.track_groups[row]

        if col == 2:
            # name
            track_group.name = item.text()
        else:
            print(f"TrackGroupsTab | Warning: OnItemChanged for unhandled column: {self.track_columns[col]} (index: {col})")

        self.on_changes_callback()
        
    def _on_visible_changed(self, row: int, checked: bool):
        if self.table.signalsBlocked():
            return
        
        track_group = self.track_groups[row]
        track_group.visible = checked
        self.on_changes_callback()

    def _on_color_changed(self, row: int, color: RGB):
        if self.table.signalsBlocked():
            return
        
        track_group = self.track_groups[row]
        track_group.color = color
        self.on_changes_callback()

    def _on_alpha_changed(self, row: int, alpha: int):
        if self.table.signalsBlocked():
            return
        
        track_group = self.track_groups[row]
        track_group.alpha = alpha
        self.on_changes_callback()

    def _on_bar_height_changed(self, row: int, value: float):
        if self.table.signalsBlocked():
            return
        
        track_group = self.track_groups[row]
        track_group.bar_height_ratio = value
        self.on_changes_callback()

    def _on_bar_speed_changed(self, row: int, value: float):
        if self.table.signalsBlocked():
            return
        
        track_group = self.track_groups[row]
        track_group.bar_sec_across_screen = value
        self.on_changes_callback()

    def _on_vert_padding_changed(self, row: int, value: float):
        if self.table.signalsBlocked():
            return
        
        track_group = self.track_groups[row]
        track_group.vertical_padding_ratio = value
        self.on_changes_callback()

    def _on_vert_offset_changed(self, row: int, value: float):
        if self.table.signalsBlocked():
            return
        
        track_group = self.track_groups[row]
        track_group.vertical_offset_ratio = value
        self.on_changes_callback()
