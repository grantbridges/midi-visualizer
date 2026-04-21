import sys
import pretty_midi
from models import VisConfig
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QCheckBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from ui.common_ui import (
    ColorButton, 
    TableSpinbox, 
    TableCheckbox, 
    PreviewWidget
)
from models import VisConfig

# ----

TRACK_NAME = 'Puppet Master'
#TRACK_NAME = 'MIDI Test'
INPUT_MIDI_FILE = f'input/{TRACK_NAME}.midi'
INPUT_MP3_FILE = f'input/{TRACK_NAME}.mp3'
INPUT_CONFIG_FILE = f'input/{TRACK_NAME}.mvc'

START_TIME_OFFSET = 0 # seconds

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        print(f"Starting MIDI Visualizer app")

        # 1) Check if we already have a .mvc (midi visual config) file for this track
        self.vis_config = VisConfig.load(INPUT_CONFIG_FILE)

        if self.vis_config is None:
            # 2) Generate new vis_config from midi file
            print(f"Generating new config for \"{TRACK_NAME}\"")
            midi_data = pretty_midi.PrettyMIDI(INPUT_MIDI_FILE)
            self.vis_config = VisConfig.create_from_midi_data(TRACK_NAME, midi_data)

            # 2.1) Save out as initial generated file
            self.vis_config.save(INPUT_CONFIG_FILE)

        self.setWindowTitle("MIDI Visualizer Config Editor")
        self.resize(1200, 900)

        # Layout
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # top controls
        top_row = QHBoxLayout()
        root.addLayout(top_row)

        self.create_btn = QPushButton("Create from MIDI")
        self.load_btn = QPushButton("Load Config")
        self.save_btn = QPushButton("Save")

        top_row.addWidget(self.create_btn)
        top_row.addWidget(self.load_btn)
        top_row.addStretch()
        top_row.addWidget(self.save_btn)

        # tabs control
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        # --- Config Tab ---
        config_tab = QWidget()
        config_tab_layout = QVBoxLayout(config_tab)

        # vis config layout
        vis_config_layout = QHBoxLayout()
        config_tab_layout.addLayout(vis_config_layout)

        vis_config_layout.addWidget(QLabel("Background:"))
        self.bg_button = ColorButton(self.vis_config.bg_color)
        vis_config_layout.addWidget(self.bg_button)
        vis_config_layout.addStretch()

        # track table
        track_columns = ["Name", "Visible", "Color", "Alpha", "Bar Height (px)", "Speed (px/sec)"]
        self.table = QTableWidget(0, len(track_columns))
        self.table.setHorizontalHeaderLabels(track_columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        config_tab_layout.addWidget(self.table)

        self.tabs.addTab(config_tab, "Config")

        # --- Preview Tab ---

        preview_tab = QWidget()
        preview_tab_layout = QVBoxLayout(preview_tab)

        # preview controls
        preview_controls_layout = QHBoxLayout()
        preview_tab_layout.addLayout(preview_controls_layout)

        self.play_stop_preview = QPushButton("Play")
        self.mute_checkbox = QCheckBox("Mute")

        preview_controls_layout.addWidget(self.play_stop_preview)
        preview_controls_layout.addWidget(self.mute_checkbox)
        preview_controls_layout.addStretch()

        # preview area
        self.preview_widget = PreviewWidget(self.vis_config)
        preview_tab_layout.addWidget(self.preview_widget)

        self.tabs.addTab(preview_tab, "Preview")

        # button callbacks
        #self.load_btn.clicked.connect(self.load_xml)
        self.save_btn.clicked.connect(self.save_config)
        self.play_stop_preview.clicked.connect(self.toggle_play_preview)

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

        self.play_stop_preview.setText("Play" if self.preview_widget.is_playing() == False else "Stop")

    def update_model(self):
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

    def save_config(self):
        self.update_model()
        
        try:
            self.vis_config.save(INPUT_CONFIG_FILE)
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))

    def toggle_play_preview(self):
        if not self.preview_widget.is_playing():
            self.update_model()
            self.preview_widget.start()
        else:
            self.preview_widget.stop()
        
        self.refresh_ui()