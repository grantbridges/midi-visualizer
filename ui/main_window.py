import os
from pathlib import Path
import subprocess
import sys
import pretty_midi
from uuid import UUID
from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QDialog,
    QFileDialog
)
from PySide6.QtGui import QAction, QKeySequence, QResizeEvent
from common import Const
from models import VisConfig, Resolution, user_settings
from render import RenderWorker
from ui.tabs import ConfigTab, TrackGroupsTab, TracksTab
from ui.widgets import PreviewWidget
from ui.dialogs import (
    ExportProgressDialog, 
    ExportOptionsDialog, 
    ExportOptions
)

# ----

FORCE_INITIAL_VIEW: bool = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        print(f"MainWindow | Starting MIDI Visualizer app")

        self.resize(Const.SCREEN_MIN_WIDTH, Const.SCREEN_MIN_HEIGHT)
        self.setMinimumSize(Const.SCREEN_MIN_WIDTH, Const.SCREEN_MIN_HEIGHT)

        # child widgets
        self.config_tab: ConfigTab = None
        self.track_groups_tab: TrackGroupsTab = None
        self.tracks_tab: TracksTab = None
        self.preview_widget: PreviewWidget = None

        # used to notify user before exit that they have unsaved changes
        self.has_unsaved_changes = False
        self.initialized_editor_view = False

        # render components
        self.render_thread = None
        self.render_worker = None
        self.progress_dialog: ExportProgressDialog = None

        # initial config load
        self.vis_config: VisConfig = None
        if not FORCE_INITIAL_VIEW:
            load_path = user_settings.active_project_path
            if load_path and not Path.exists(load_path):
                # if last active project doesn't exist, load nothing
                load_path = None
            
            if load_path:
                loaded_vis_config = VisConfig.load(load_path)

                if loaded_vis_config is not None:
                    self.vis_config = loaded_vis_config
                    self.vis_config.init()
                else:
                    QMessageBox.critical(self, "Load Failed", f"Unable to load previous project at {load_path}. See logs for details.")

        # File menu
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        # Actions
        self.new_project_action = QAction("New Project...", self, shortcut="Ctrl+N")
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

        self.refresh_file_menu()
        self.refresh_window_title()

        # initialize views
        if self.vis_config is not None:
            self.init_vis_config_editor_view()
        else:
            self.init_default_view()

    def init_default_view(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignCenter)

        new_shortcut = self.new_project_action.shortcut().toString(QKeySequence.NativeText)
        open_shortcut = self.open_action.shortcut().toString(QKeySequence.NativeText)

        help_tips = [
            f"{new_shortcut} to create a new project from a .midi file",
            f"{open_shortcut} to open an existing project"
        ]

        for text in help_tips:
            label = QLabel()
            label.setText(text)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #888888;")
            font = label.font()
            font.setFamily(Const.PRIMARY_FONT)
            font.setPointSize(14)
            label.setFont(font)
            layout.addWidget(label)
        

    def init_vis_config_editor_view(self):
        # clean up children if already initialized 
        if self.initialized_editor_view:
            self.config_tab.shutdown()
            self.config_tab.deleteLater()
            self.track_groups_tab.shutdown()
            self.track_groups_tab.deleteLater()
            self.tracks_tab.shutdown()
            self.tracks_tab.deleteLater()
            self.preview_widget.shutdown()
            self.preview_widget.deleteLater()

            self.tabs.deleteLater()

        # tabs
        self.tabs = QTabWidget()
        self.config_tab = ConfigTab(self.vis_config, self.on_config_changed)
        self.track_groups_tab = TrackGroupsTab(self.vis_config, self.on_config_changed, self.on_track_group_selected)
        self.tracks_tab = TracksTab(self.vis_config, self.on_config_changed)
        self.tabs.addTab(self.config_tab, "Config")
        self.tabs.addTab(self.track_groups_tab, "Track Groups")
        self.tabs.addTab(self.tracks_tab, "Tracks")
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # preview area
        self.preview_widget = PreviewWidget(self.vis_config)

        # layout controls
        self.layout_editor_controls()

        # initial model changed call to initialize stuff
        self.preview_widget.model_changed()
        self.refresh_ui()

        self.initialized_editor_view = True

    def layout_editor_controls(self):
        # create controls
        central = QWidget()
        self.setCentralWidget(central)

        # Layout
        root = QVBoxLayout(central)
        root.addWidget(self.tabs, 1)
        root.addWidget(self.preview_widget, 1)

        self.config_tab.layout_controls()
        self.track_groups_tab.layout_controls()
        self.tracks_tab.layout_controls()
        self.preview_widget.layout_controls()

    def refresh_ui(self):
        self.config_tab.refresh_ui()
        self.track_groups_tab.refresh_ui()
        self.tracks_tab.refresh_ui()
        self.preview_widget.refresh_ui()

    def refresh_window_title(self):
        title = Const.APP_NAME

        if self.vis_config:
            title += f" - {self.vis_config.track_name}"

        if self.has_unsaved_changes:
            title += "*"

        self.setWindowTitle(title)

    def refresh_file_menu(self):
        has_project = self.vis_config is not None

        self.save_action.setVisible(has_project)
        self.save_as_action.setVisible(has_project)
        self.export_action.setVisible(has_project)

    def update_model(self):
        # ask individual tabs to copy their local UI models into the data model
        self.config_tab.update_model()
        self.track_groups_tab.update_model()
        self.tracks_tab.update_model()

    # returns True on successful save
    def save_config(self, force_select_save_location: bool = False) -> bool:
        self.update_model()

        # if we don't have a path, prompt user for where to save it
        if force_select_save_location or not user_settings.active_project_path:
            default_filepath = ""
            if user_settings.active_project_path:
                default_filepath = user_settings.active_project_path

            save_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Save {Const.APP_NAME} Project",
                default_filepath,
                f"{Const.APP_NAME} Project Files (*.{Const.PROJECT_EXT})"
            )

            if not save_path:
                return False # cancelled
            
            path = Path(save_path)
            expected_suffix = f".{Const.PROJECT_EXT}"
            if path.suffix != expected_suffix:
                path = path.with_suffix(expected_suffix)
            
            # update active project path
            user_settings.active_project_path = str(path)
            user_settings.save()
        
        try:
            self.vis_config.save(user_settings.active_project_path)
            self.has_unsaved_changes = False
            self.refresh_window_title()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))
            return False

    # child tab API

    def on_config_changed(self):
        self.update_model()

        self.has_unsaved_changes = True
        self.refresh_window_title()

        # notify preview tab to redraw
        self.preview_widget.model_changed()

    def on_tracks_changed(self):
        self.update_model()

        # notify preview tab to redraw
        self.preview_widget.model_changed()

    def on_tab_changed(self, index: int):
        if index == 0:
            self.config_tab.refresh_ui()
        elif index == 1:
            self.track_groups_tab.refresh_ui()
        elif index == 2:
            self.tracks_tab.refresh_ui()

    def on_track_group_selected(self, group_id: UUID | None):
        self.preview_widget.set_selected_group_id(group_id)

    # event overrides
    def closeEvent(self, event):
        if not self.has_unsaved_changes:
            event.accept()
            return

        result = QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Save before closing?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )

        if result == QMessageBox.Save:
            saved = self.save_config()
            if saved:
                event.accept()
            else:
                event.ignore()

        elif result == QMessageBox.Discard:
            event.accept()

        else:  # Cancel
            event.ignore()

    def resizeEvent(self, event: QResizeEvent):
        new_size = event.size()

        width = new_size.width()
        height = new_size.height()

        if self.preview_widget is not None:
            self.preview_widget.handle_resize(width, height)

        super().resizeEvent(event)

    # action callbacks

    def on_new_project_action(self):
        midi_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Open MIDI File",
            "",
            f"MIDI Files (*.mid, *.midi)"
        )
        
        if not midi_path:
            return
       
        # first prompt for saving unsaved changes
        if self.has_unsaved_changes:
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )

            if result == QMessageBox.Save:
                save_result = self.save_config()
                if not save_result:
                    return # something went wrong while saving
            elif result == QMessageBox.Discard:
                pass # ignore, continue loading
            elif result == QMessageBox.Cancel:
                return # user cancelled load
            
        try:
            midi_data = pretty_midi.PrettyMIDI(midi_path)
        except ValueError:
            QMessageBox.critical(self, "Project Creation Failed", f'Unable to create new {Const.APP_NAME} project from provided midi file')
            return
            
        # update local working model
        self.vis_config = VisConfig.create_from_midi_data(Path(midi_path).stem, midi_data)
        self.vis_config.init()

        # update active project entry
        user_settings.active_project_path = None
        user_settings.save()

        # clear working state
        self.has_unsaved_changes = True # to prompt user to save this project
        self.refresh_window_title()
        self.refresh_file_menu()

        # re-init UI
        self.init_vis_config_editor_view()

    def on_open_action(self):
        default_filepath = ""
        if user_settings.active_project_path:
            default_filepath = user_settings.active_project_path

        load_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Open {Const.APP_NAME} Project",
            default_filepath,
            f"{Const.APP_NAME} Project Files (*.{Const.PROJECT_EXT})"
        )

        if not load_path:
            return
        
        # first prompt for saving unsaved changes
        if self.has_unsaved_changes:
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )

            if result == QMessageBox.Save:
                save_result = self.save_config()
                if not save_result:
                    return # something went wrong while saving
            elif result == QMessageBox.Discard:
                pass # ignore, continue loading
            elif result == QMessageBox.Cancel:
                return # user cancelled load
        
        # load new file in
        vis_config = VisConfig.load(load_path)
        if vis_config is None:
            QMessageBox.critical(self, "Load Failed", f'Unable to load {Const.APP_NAME} project file')
            return
        
        # update local working model
        self.vis_config = vis_config
        self.vis_config.init()

        # update active project entry
        user_settings.active_project_path = load_path
        user_settings.save()

        # clear working state
        self.has_unsaved_changes = False
        self.refresh_window_title()
        self.refresh_file_menu()

        # re-init UI
        self.init_vis_config_editor_view()

    def on_save_action(self):
        self.save_config()

    def on_save_as_action(self):
        self.save_config(True)

    def on_export_action(self):
        export_dialog = ExportOptionsDialog(vis_config=self.vis_config, parent=self)

        if export_dialog.exec() == QDialog.Accepted:
            options = export_dialog.get_options()
            self.vis_config.export_dir = options.output_dir
            self.vis_config.export_filename = options.filename
            self.vis_config.export_format = options.render_format
            self.vis_config.export_resolution = options.resolution
            self.has_unsaved_changes = True
            self.refresh_window_title()

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

        QMessageBox.critical(self, 'Render Failed', error)

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
            QMessageBox.information(self, "Success", f"Exported video to {self.vis_config.export_dir}")
        

