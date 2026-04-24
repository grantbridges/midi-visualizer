import pretty_midi
from models import VisConfig
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
)
from models import VisConfig
from ui.tabs import ConfigTab, TracksTab, PreviewTab

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

        self.setWindowTitle("MIDI Visualizer Config Editor")
        self.setFixedSize(1200, 900)

        # 1) Check if we already have a .mvc (midi visual config) file for this track
        self.vis_config = VisConfig.load(INPUT_CONFIG_FILE)

        if self.vis_config is None:
            # 2) Generate new vis_config from midi file
            print(f"Generating new config for \"{TRACK_NAME}\"")
            midi_data = pretty_midi.PrettyMIDI(INPUT_MIDI_FILE)
            self.vis_config = VisConfig.create_from_midi_data(TRACK_NAME, midi_data)

            # 2.1) Save out as initial generated file
            self.vis_config.save(INPUT_CONFIG_FILE)

        if self.vis_config is not None:
            self.init_vis_config_editor_view()
        else:
            self.init_default_view()

    def init_default_view(self):
        pass # TODO

    def init_vis_config_editor_view(self):
        # create controls
        central = QWidget()
        self.setCentralWidget(central)

        # top row controls
        self.create_btn = QPushButton("Create from MIDI")
        self.load_btn = QPushButton("Load Config")
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_config)

        # tabs
        self.tabs = QTabWidget()
        self.config_tab = ConfigTab(self.on_config_changed, self.vis_config)
        self.tracks_tab = TracksTab(self.on_tracks_changed, self.vis_config)
        self.preview_tab = PreviewTab(self.vis_config)
        self.tabs.addTab(self.config_tab, "Config")
        self.tabs.addTab(self.tracks_tab, "Tracks")
        self.tabs.addTab(self.preview_tab, "Preview")

        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Layout
        root = QVBoxLayout(central)

        top_row = QHBoxLayout()
        top_row.addWidget(self.create_btn)
        top_row.addWidget(self.load_btn)
        top_row.addStretch()
        top_row.addWidget(self.save_btn)
        root.addLayout(top_row)

        root.addWidget(self.tabs)

        self.refresh_ui()

    def refresh_ui(self):
        self.config_tab.refresh_ui()
        self.tracks_tab.refresh_ui()
        self.preview_tab.refresh_ui()

    def update_model(self):
        self.config_tab.update_model()
        self.tracks_tab.update_model()
        self.preview_tab.update_model()

    def on_config_changed(self):
        pass

    def on_tracks_changed(self):
        pass

    def on_tab_changed(self, index: int):
        if self.tabs.widget(index) is self.preview_tab:
            self.preview_tab.on_show()
        else:
            self.preview_tab.on_hide()

    def save_config(self):
        self.update_model()
        
        try:
            self.vis_config.save(INPUT_CONFIG_FILE)
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))

