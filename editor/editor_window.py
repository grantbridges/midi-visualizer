from typing import List
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from editor.common_ui import ColorButton, TableSpinbox, TableCheckbox
from models import VisConfig, Track, Note

class EditorWindow(QMainWindow):
    def __init__(self, vis_config: VisConfig, save_file_path: str):
        super().__init__()
        self.setWindowTitle("Visualizer Config Editor")
        self.resize(900, 500)

        self.vis_config = vis_config
        self.save_file_path = save_file_path

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # top controls
        top_row = QHBoxLayout()
        root.addLayout(top_row)

        top_row.addWidget(QLabel("Background:"))
        self.bg_button = ColorButton(self.vis_config.bg_color)
        top_row.addWidget(self.bg_button)

        #self.load_btn = QPushButton("Load")
        self.save_btn = QPushButton("Save")

        top_row.addStretch()
        #top_row.addWidget(self.load_btn)
        top_row.addWidget(self.save_btn)

        # track table
        track_columns = ["Name", "Visible", "Color", "Alpha", "Bar Height", "Pixels/Sec"]
        self.table = QTableWidget(0, len(track_columns))
        self.table.setHorizontalHeaderLabels(track_columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        root.addWidget(self.table)

        # signals
        #self.load_btn.clicked.connect(self.load_xml)
        self.save_btn.clicked.connect(self.save_config)
        #self.add_btn.clicked.connect(self.add_track)
        #self.remove_btn.clicked.connect(self.remove_selected_track)

        # starter data
        #self.vis_config.tracks.append(Track(name="Track 1", color=(255, 0, 0)))
        self.refresh_ui()

    def refresh_ui(self):
        self.bg_button.rgb = self.vis_config.bg_color
        self.bg_button.refresh()

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
            self.table.setCellWidget(row, col, checkbox)
            col += 1

            # color button
            color_btn = ColorButton(track.color)
            self.table.setCellWidget(row, col, color_btn)
            col += 1

            # alpha
            alpha = TableSpinbox()
            alpha.setRange(0, 255)
            alpha.setValue(track.alpha)
            self.table.setCellWidget(row, col, alpha)
            col += 1

            # bar height
            bar_height = TableSpinbox()
            bar_height.setRange(1, 500)
            bar_height.setValue(track.bar_height)
            self.table.setCellWidget(row, col, bar_height)
            col += 1

            # pixels/sec
            pps = TableSpinbox()
            pps.setRange(1, 5000)
            pps.setValue(track.bar_pixels_per_second)
            self.table.setCellWidget(row, col, pps)
            col += 1

    def load_xml(self):
        pass
    #     path, _ = QFileDialog.getOpenFileName(self, "Open Config", "", "XML Files (*.xml)")
    #     if not path:
    #         return
    #     try:
    #         self.config = VisConfig.load(path)
    #         self.refresh_ui()
    #     except Exception as e:
    #         QMessageBox.critical(self, "Load failed", str(e))

    def save_config(self):
        # path, _ = QFileDialog.getSaveFileName(self, "Save Config", "", "MIDI Visualizer Config (*.mvc)")
        # if not path:
        #     return
        
        # update top-level props
        self.vis_config.bg_color = self.bg_button.rgb

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
                pps = self.table.cellWidget(row, 5)

                track.visible = visible_checkbox.isChecked()
                track.color = color_btn.rgb
                track.alpha = alpha.value()
                track.bar_height = bar_height.value()
                track.bar_pixels_per_second = pps.value()
            else:
                print(f"Warning: Unknown track row \"{name}\"")
        
        try:
            self.vis_config.save(self.save_file_path)
            # QMessageBox.information(self, "Saved", f"Saved {self.vis_config.track_name} midi visualizer config to {self.save_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))