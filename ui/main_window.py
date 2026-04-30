import os
import subprocess
import sys
import pretty_midi
from PySide6.QtCore import QThread
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
from render import Resolution, RenderWorker
from ui.tabs import ConfigTab, TracksTab, PreviewTab
from ui.dialogs import ExportProgressDialog

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

        self.render_thread = None
        self.render_worker = None

        self.progress_dialog: ExportProgressDialog = None

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
        self.export_btn = QPushButton("Export MP4")
        self.export_btn.clicked.connect(self.export_mp4)

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
        top_row.addWidget(self.export_btn)
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

    def on_config_changed(self):
        self.update_model()

        # notify preview tab to redraw
        self.preview_tab.model_changed()

    def on_tracks_changed(self):
        self.update_model()

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

    def export_mp4(self):
        self.progress_dialog = ExportProgressDialog(track_title=self.vis_config.track_name, parent=self)
        self.progress_dialog.show()

        self.render_thread = QThread()
        self.render_worker = RenderWorker(self.vis_config, Resolution.HD, "output")

        self.render_worker.moveToThread(self.render_thread)

        self.render_thread.started.connect(self.render_worker.run)

        # connect ui to thread events
        self.render_worker.progress.connect(self.progress_dialog.update_progress)
        self.render_worker.finished.connect(self.on_render_finished)
        self.render_worker.failed.connect(lambda msg: self.on_render_failed(msg))

        self.progress_dialog.cancel_clicked.connect(self.on_render_cancelled)

        # cleanup thread on any result
        self.render_worker.finished.connect(self.render_thread.quit)
        self.render_worker.failed.connect(self.render_thread.quit)
        self.render_worker.cancelled.connect(self.render_thread.quit)

        self.render_thread.start()

    def on_render_cancelled(self):
        self.render_worker.cancel()
        self.progress_dialog.hide()
        self.progress_dialog = None

    def on_render_failed(self, error: str):
        self.progress_dialog.hide()
        self.progress_dialog = None

        QMessageBox.critical(None, 'Render Failed', error)

    def on_render_finished(self, output_file: str):
        show_output = self.progress_dialog.get_show_output_folder()

        self.progress_dialog.hide()
        self.progress_dialog = None

        if show_output:
            if not output_file:
                return

            folder = os.path.dirname(output_file)

            if sys.platform == "darwin":
                subprocess.run(["open", folder])
            elif sys.platform == "win32":
                os.startfile(folder)
            else:  # linux
                subprocess.run(["xdg-open", folder])
        else:
            QMessageBox.information(None, "Success", f"Exported video to '{output_file}'")
        

