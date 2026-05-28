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
from ui.common import ColorButton, TableCheckbox, TableSpinbox
import copy

class TracksTab(QWidget):
    def __init__(self, on_changes_callback: object, vis_config: VisConfig):
        super().__init__()

        self.on_changes_callback = on_changes_callback
        self.vis_config = vis_config

        # create controls
        self.track_columns = ["Name", "Group", "Visible", "Color", "Alpha", "Bar Height", "Speed (sec)"]
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

            in_group = track.group_id is not None
            if in_group:
                index = combo.findData(str(track.group_id))
                if index >= 0:
                    combo.setCurrentIndex(index)
            combo.currentIndexChanged.connect(self._on_group_changed)
            self.table.setCellWidget(row, col, combo)
            col += 1

            # visible
            checkbox = TableCheckbox(track.visible)
            checkbox.setDisabled(in_group)
            checkbox.valueChanged.connect(self.on_changes_callback)
            self.table.setCellWidget(row, col, checkbox)
            col += 1

            # color button
            color_btn = ColorButton(track.color)
            color_btn.setDisabled(in_group)
            color_btn.valueChanged.connect(self.on_changes_callback)
            self.table.setCellWidget(row, col, color_btn)
            col += 1

            # alpha
            alpha = TableSpinbox()
            alpha.setDisabled(in_group)
            alpha.setRange(0, 255)
            alpha.setValue(track.alpha)
            alpha.valueChanged.connect(self.on_changes_callback)
            self.table.setCellWidget(row, col, alpha)
            col += 1

            # bar height
            bar_height = TableSpinbox()
            bar_height.setDisabled(in_group)
            bar_height.setRange(1, 100)
            bar_height.setValue(track.bar_height_ratio * 100)
            bar_height.valueChanged.connect(self.on_changes_callback)
            self.table.setCellWidget(row, col, bar_height)
            col += 1

            # pixels/sec
            sec_across_screen = TableSpinbox()
            sec_across_screen.setDisabled(in_group)
            sec_across_screen.setRange(1, 5)
            sec_across_screen.setValue(track.bar_sec_across_screen)
            sec_across_screen.valueChanged.connect(self.on_changes_callback)
            self.table.setCellWidget(row, col, sec_across_screen)
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
                visible_checkbox: TableCheckbox = self.table.cellWidget(row, 2)
                color_btn: ColorButton = self.table.cellWidget(row, 3)
                alpha = self.table.cellWidget(row, 4)
                bar_height = self.table.cellWidget(row, 5)
                sec_across_screen = self.table.cellWidget(row, 6)

                track.group_id = UUID(group_combo.currentData())
                track.visible = visible_checkbox.isChecked()
                track.color = color_btn.rgb
                track.alpha = alpha.value()
                track.bar_height_ratio = bar_height.value() / 100
                track.bar_sec_across_screen = sec_across_screen.value()
            else:
                print(f"Warning: Unknown track row \"{name}\"")

    def _on_group_changed(self):
        self.on_changes_callback()
        self.refresh_ui()