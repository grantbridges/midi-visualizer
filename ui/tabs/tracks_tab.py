from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QHeaderView,
)

from models import VisConfig
from ui.common import ColorButton, TableCheckbox, TableSpinbox

class TracksTab(QWidget):
    def __init__(self, on_changes_callback: object, vis_config: VisConfig):
        super().__init__()

        self.on_changes_callback = on_changes_callback
        self.vis_config = vis_config

        # create controls
        self.track_columns = ["Name", "Visible", "Color", "Alpha", "Bar Height", "Speed (sec)"]
        self.table = QTableWidget(0, len(self.track_columns))
        self.table.setHorizontalHeaderLabels(self.track_columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # layout controls
        v_layout = QVBoxLayout(self)
        v_layout.addWidget(self.table)

    def refresh_ui(self):
        self.table.setRowCount(len(self.vis_config.tracks))

        for row, track in enumerate(self.vis_config.tracks):
            col = 0

            # name
            name_item = QTableWidgetItem(track.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, col, name_item)
            col += 1

            # visible
            checkbox = TableCheckbox(track.visible)
            checkbox.valueChanged.connect(self.on_changes_callback)
            self.table.setCellWidget(row, col, checkbox)
            col += 1

            # color button
            color_btn = ColorButton(track.color)
            color_btn.valueChanged.connect(self.on_changes_callback)
            self.table.setCellWidget(row, col, color_btn)
            col += 1

            # alpha
            alpha = TableSpinbox()
            alpha.setRange(0, 255)
            alpha.setValue(track.alpha)
            alpha.valueChanged.connect(self.on_changes_callback)
            self.table.setCellWidget(row, col, alpha)
            col += 1

            # bar height
            bar_height = TableSpinbox()
            bar_height.setRange(1, 100)
            bar_height.setValue(track.bar_height_ratio * 100)
            bar_height.valueChanged.connect(self.on_changes_callback)
            self.table.setCellWidget(row, col, bar_height)
            col += 1

            # pixels/sec
            sec_across_screen = TableSpinbox()
            sec_across_screen.setRange(1, 5)
            sec_across_screen.setValue(track.bar_sec_across_screen)
            sec_across_screen.valueChanged.connect(self.on_changes_callback)
            self.table.setCellWidget(row, col, sec_across_screen)
            col += 1

    def update_model(self):
        # update track props
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            name = name_item.text()

            track = self.vis_config.get_track_by_name(name)
            if track is not None:
                visible_checkbox: TableCheckbox = self.table.cellWidget(row, 1)
                color_btn: ColorButton = self.table.cellWidget(row, 2)
                alpha = self.table.cellWidget(row, 3)
                bar_height = self.table.cellWidget(row, 4)
                sec_across_screen = self.table.cellWidget(row, 5)

                track.visible = visible_checkbox.isChecked()
                track.color = color_btn.rgb
                track.alpha = alpha.value()
                track.bar_height_ratio = bar_height.value() / 100
                track.bar_sec_across_screen = sec_across_screen.value()
            else:
                print(f"Warning: Unknown track row \"{name}\"")