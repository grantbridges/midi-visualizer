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
    QDialog
)
from PySide6.QtGui import QAction
from common import Const
from models import VisConfig, Resolution
from render import RenderWorker
from ui.tabs import ConfigTab, TracksTab, PreviewWidget
from ui.dialogs import (
    ExportProgressDialog, 
    ExportOptionsDialog, 
    ExportOptions
)

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
        self.setFixedSize(Const.SCREEN_WIDTH, Const.SCREEN_HEIGHT)

        self.render_thread = None
        self.render_worker = None

        self.progress_dialog: ExportProgressDialog = None

        # File menu
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        # Actions
        self.new_project_action = QAction("New Project...", self)
        self.new_project_action.triggered.connect(self.on_new_project_action)
        self.open_action = QAction("Open...", parent=self, shortcut="Ctrl+O")
        self.open_action.triggered.connect(self.on_open_action)
        self.save_action = QAction("Save", parent=self, shortcut="Ctrl+S")
        self.save_action.triggered.connect(self.on_save_action)
        self.save_as_action = QAction("Save As...", parent=self, shortcut="Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self.on_save_as_action)
        self.export_action = QAction("Export...", parent=self, shortcut="Ctrl+Shift+X")
        self.export_action.triggered.connect(self.on_export_action)

        # Add actions to menu
        file_menu.addAction(self.new_project_action)
        file_menu.addSeparator()
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_action)

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
        # tabs
        self.tabs = QTabWidget()
        self.config_tab = ConfigTab(self.on_config_changed, self.vis_config)
        self.tracks_tab = TracksTab(self.on_tracks_changed, self.vis_config)
        self.tabs.addTab(self.config_tab, "Config")
        self.tabs.addTab(self.tracks_tab, "Tracks")
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # preview area
        self.preview_widget = PreviewWidget(self.vis_config)

        self.layout_controls()

        self.refresh_ui()

    def layout_controls(self):
        # create controls
        central = QWidget()
        self.setCentralWidget(central)

        # Layout
        root = QVBoxLayout(central)
        root.addWidget(self.tabs, 1)
        root.addWidget(self.preview_widget, 1)

        self.preview_widget.layout_controls()

    def refresh_ui(self):
        self.config_tab.refresh_ui()
        self.tracks_tab.refresh_ui()
        self.preview_widget.refresh_ui()

    def update_model(self):
        self.config_tab.update_model()
        self.tracks_tab.update_model()

    def on_config_changed(self):
        self.update_model()

        # notify preview tab to redraw
        self.preview_widget.model_changed()

    def on_tracks_changed(self):
        self.update_model()

    def on_tab_changed(self, index: int):
        if self.tabs.widget(index) is self.preview_widget:
            self.preview_widget.on_show()
        else:
            self.preview_widget.on_hide()

    # Action callbacks

    def on_new_project_action(self):
        print("Create clicked")
        pass # TODO

    def on_open_action(self):
        print("Open clicked")
        pass # TODO

    def on_save_action(self):
        self.update_model()
        
        try:
            self.vis_config.save(INPUT_CONFIG_FILE)
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))

    def on_save_as_action(self):
        print("Save As clicked")
        pass # TODO

    def on_export_action(self):
        export_dialog = ExportOptionsDialog(vis_config=self.vis_config, parent=self)

        if export_dialog.exec() == QDialog.Accepted:
            options = export_dialog.get_options()
            self.vis_config.export_dir = options.output_dir
            self.vis_config.export_filename = options.filename
            self.vis_config.export_format = options.render_format
            self.vis_config.export_resolution = options.resolution
            self.save_config()

            self.progress_dialog = ExportProgressDialog(track_title=self.vis_config.track_name, parent=self)
            self.progress_dialog.show()

            self.render_thread = QThread()
            self.render_worker = RenderWorker(self.vis_config)

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

    # Render events

    def on_render_cancelled(self):
        self.render_worker.cancel()
        self.progress_dialog.hide()
        self.progress_dialog = None

    def on_render_failed(self, error: str):
        self.progress_dialog.hide()
        self.progress_dialog = None

        QMessageBox.critical(None, 'Render Failed', error)

    def on_render_finished(self):
        show_output = self.progress_dialog.get_show_output_folder()

        self.progress_dialog.hide()
        self.progress_dialog = None

        if show_output:
            folder = os.path.dirname(self.vis_config.export_dir)

            if sys.platform == "darwin":
                subprocess.run(["open", folder])
            elif sys.platform == "win32":
                os.startfile(folder)
            else:  # linux
                subprocess.run(["xdg-open", folder])
        else:
            QMessageBox.information(None, "Success", f"Exported video to {self.vis_config.export_dir}")
        

