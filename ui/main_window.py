import os
from pathlib import Path
import subprocess
import sys
from typing import List
import pretty_midi
from uuid import UUID
from PySide6.QtCore import QEvent, QThread, Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QSplitter,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QDialog,
    QFileDialog
)
from PySide6.QtGui import QAction, QKeySequence, QResizeEvent, QShortcut
from common import Const
from models import VisConfig, Track, Resolution, user_settings, BackgroundMode
from render import RenderWorker
from media import video_provider, audio_provider, image_provider
from ui.tabs import ConfigTab, BackgroundTab, AudioTab, TrackGroupsTab, TracksTab, NotesTab
from ui.common import Icons
from ui.widgets import PreviewWidget
from ui.dialogs import (
    ExportProgressDialog, 
    ExportOptionsDialog, 
    ProgressDialog
)
from utility import LogUtil

import logging
logger = logging.getLogger("MainWindow")

# ----

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        logger.info(f"Starting {Const.APP_NAME} main window")

        self.setMinimumSize(Const.SCREEN_MIN_WIDTH, Const.SCREEN_MIN_HEIGHT)

        # child widgets
        self.config_tab: ConfigTab = None
        self.background_tab: BackgroundTab = None
        self.audio_tab: AudioTab = None
        self.track_groups_tab: TrackGroupsTab = None
        self.tracks_tab: TracksTab = None
        self.notes_tab: NotesTab = None
        self.preview_widget: PreviewWidget = None

        # dialogs
        self.export_progress_dialog: ExportProgressDialog = None
        self.load_video_progress_dialog: ProgressDialog = None

        # used to notify user before exit that they have unsaved changes
        self.has_unsaved_changes = False
        self.initialized_editor_view = False

        # render components
        self.render_thread: QThread | None = None
        self.render_worker: RenderWorker | None = None

        self.init_menu_bar()

        # Key shortcuts
        self.space_shortcut = QShortcut(QKeySequence(Qt.Key_Space), self)
        self.space_shortcut.setContext(Qt.WindowShortcut)
        self.space_shortcut.activated.connect(self._on_space_pressed)

        # Load video preview events callbacks
        video_provider.load_finished.connect(self.on_load_video_finished)
        video_provider.load_failed.connect(self.on_load_video_failed)
        video_provider.load_progress.connect(self.on_load_video_progress)

        # initial config load
        self.vis_config: VisConfig = None
        load_path = user_settings.active_project_path
        if load_path:
            if Path.exists(load_path):
                logger.info(f"Previous active project detected at \"{load_path}\"")
            else:
                logger.warning(f"Previous active project filepath is invalid (\"{load_path}\") - starting default view")
                load_path = None
        else:
            logger.info(f" No previous active project detected - starting default view")
        
        if load_path:
            loaded_vis_config = VisConfig.load(load_path)

            if loaded_vis_config is not None:
                self.vis_config = loaded_vis_config
                self.vis_config.init()
                self._load_config_resources()
            else:
                QMessageBox.critical(self, "Load Failed", f"Unable to load previous project at {load_path}. See logs for details.")

        self.refresh_file_menu()
        self.refresh_window_title()

        # initialize views
        if self.vis_config is not None:
            self.init_vis_config_editor_view()
        else:
            self.init_default_view()

        if user_settings.fullscreen:
            self.showFullScreen()
        else:
            self.resize(Const.SCREEN_INITIAL_WIDTH, Const.SCREEN_INITIAL_HEIGHT)

    def init_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        self.new_project_action = QAction("New Project...", self, shortcut="Ctrl+N")
        self.new_project_action.triggered.connect(self.on_new_project_action)
        self.update_project_action = QAction("Update Project MIDI...", self, shortcut="Ctrl+U")
        self.update_project_action.triggered.connect(self.on_update_project_action)
        self.open_action = QAction("Open...", parent=self, shortcut="Ctrl+O")
        self.open_action.triggered.connect(self.on_open_action)
        self.save_action = QAction("Save", parent=self, shortcut="Ctrl+S")
        self.save_action.triggered.connect(self.on_save_action)
        self.save_as_action = QAction("Save As...", parent=self, shortcut="Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self.on_save_as_action)
        self.export_action = QAction("Export...", parent=self, shortcut="Ctrl+Shift+X")
        self.export_action.triggered.connect(self.on_export_action)

        file_menu.addAction(self.new_project_action)
        file_menu.addAction(self.update_project_action)
        file_menu.addSeparator()
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_action)

        # Help menu
        help_menu = menu_bar.addMenu("Help")

        self.export_logs_action = QAction("Export Logs...", self)
        self.export_logs_action.triggered.connect(self.on_export_logs_action)

        help_menu.addAction(self.export_logs_action)

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
            self.background_tab.shutdown()
            self.background_tab.deleteLater()
            self.audio_tab.shutdown()
            self.audio_tab.deleteLater()
            self.track_groups_tab.shutdown()
            self.track_groups_tab.deleteLater()
            self.tracks_tab.shutdown()
            self.tracks_tab.deleteLater()
            self.notes_tab.shutdown()
            self.notes_tab.deleteLater()
            self.preview_widget.shutdown()
            self.preview_widget.deleteLater()

            self.tabs.deleteLater()

        # tabs
        self.tabs = QTabWidget()
        self.config_tab = ConfigTab(
            self.vis_config, 
            self.on_config_changed
        )
        self.background_tab = BackgroundTab(
            self.vis_config, 
            self.on_config_changed, 
            self.on_bg_video_changed, 
            self.on_bg_image_changed
        )
        self.audio_tab = AudioTab(
            self.vis_config, 
            self.on_config_changed, 
            self.on_audio_changed
        )
        self.tracks_tab = TracksTab(
            self.vis_config, 
            self.on_config_changed
        )
        self.track_groups_tab = TrackGroupsTab(
            self.vis_config, 
            self.on_config_changed, 
            self.on_track_group_selected
        )
        self.notes_tab = NotesTab(
            self.vis_config, 
            self.on_config_changed
        )

        self.tabs.addTab(self.config_tab, "General")
        self.tabs.addTab(self.background_tab, Icons.image_outline(), "Background")
        self.tabs.addTab(self.audio_tab, Icons.audio(), "Audio")
        self.tabs.addTab(self.tracks_tab, Icons.music(), "Tracks")
        self.tabs.addTab(self.track_groups_tab, Icons.group(), "Track Groups")
        self.tabs.addTab(self.notes_tab, Icons.magic(), "Note Effects")
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # preview area
        self.preview_widget = PreviewWidget(self.vis_config)

        # layout controls
        self.layout_editor_controls()

        # initial model changed call to initialize stuff
        self.preview_widget.model_changed()
        self.refresh_ui(True)

        self.initialized_editor_view = True

    def layout_editor_controls(self):
        # create controls
        central = QWidget()
        self.setCentralWidget(central)

        # Layout
        root = QVBoxLayout(central)

        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(2)

        splitter.setStyleSheet("""
            QSplitter::handle:vertical {
                margin-bottom: 5px;
                background-color: #3a3a3a;
            }
        """)

        splitter.addWidget(self.preview_widget)
        splitter.addWidget(self.tabs)

        splitter.setSizes([700, 300])

        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, True)
        
        root.addWidget(splitter)

        self.config_tab.layout_controls()
        self.background_tab.layout_controls()
        self.audio_tab.layout_controls()
        self.track_groups_tab.layout_controls()
        self.tracks_tab.layout_controls()
        self.notes_tab.layout_controls()
        self.preview_widget.layout_controls()

    def refresh_ui(self, refresh_all: bool = False):
        if refresh_all:
            self.config_tab.refresh_ui()
            self.background_tab.refresh_ui()
            self.audio_tab.refresh_ui()
            self.track_groups_tab.refresh_ui()
            self.tracks_tab.refresh_ui()
            self.notes_tab.refresh_ui()
        else:
            # just refresh currently visibile tab
            match self.tabs.currentIndex():
                case 0:
                    self.config_tab.refresh_ui()
                case 1:
                    self.background_tab.refresh_ui()
                case 2:
                    self.audio_tab.refresh_ui()
                case 3:
                    self.track_groups_tab.refresh_ui()
                case 4:
                    self.tracks_tab.refresh_ui()
                case 5:
                    self.notes_tab.refresh_ui()

        self.preview_widget.refresh_ui()

    def refresh_window_title(self):
        title = f"{Const.APP_NAME}"

        if self.vis_config:
            title += f" - {self.vis_config.track_name}"

        if self.has_unsaved_changes:
            title += "*"

        self.setWindowTitle(title)

    def refresh_file_menu(self):
        has_project = self.vis_config is not None

        self.update_project_action.setVisible(has_project)
        self.save_action.setVisible(has_project)
        self.save_as_action.setVisible(has_project)
        self.export_action.setVisible(has_project)

    def update_model(self):
        # ask individual tabs to copy their local UI models into the data model
        self.config_tab.update_model()
        self.background_tab.update_model()
        self.audio_tab.update_model()
        self.track_groups_tab.update_model()
        self.tracks_tab.update_model()
        self.notes_tab.update_model()

    # returns True on successful save
    def save_config(self, force_select_save_location: bool = False) -> bool:
        self.update_model()

        # if we don't have a path, prompt user for where to save it
        if force_select_save_location or not user_settings.active_project_path:
            default_filepath = ""
            if user_settings.active_project_path:
                default_filepath = user_settings.active_project_path
            else:
                default_filepath = f"{self.vis_config.track_name}.{Const.PROJECT_EXT}"

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
            QMessageBox.critical(self, "Save failed", f"Failed to save config: {str(e)}")
            return False
        
    def _load_config_resources(self):
        # will only load each of these if present
        self._load_video()
        self._load_image()
        self._load_audio()

    def _load_video(self):
        video_provider.clear()
        has_video = (
            bool(self.vis_config.bg_video_filepath)
            and Path(self.vis_config.bg_video_filepath).is_file()
        )

        if has_video:
            self.setDisabled(True)
            self.load_video_progress_dialog = ProgressDialog("Load", "Loading video preview...", False)
            self.load_video_progress_dialog.show()

            video_provider.load_video(self.vis_config.bg_video_filepath)
    
    def _load_image(self):
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            image_provider.clear()
            has_image = (
                bool(self.vis_config.bg_image_filepath)
                and Path(self.vis_config.bg_image_filepath).is_file()
            )

            if has_image:
                image_provider.load_image(self.vis_config.bg_image_filepath)
        except Exception as e:
            QMessageBox.critical(self, "Load Failed", f"Failed to load image: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()
    
    def _load_audio(self):
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            audio_provider.clear()
            self.vis_config.waveform.clear()

            audio_path = self.vis_config.audio_filepath

            # ensure this is a valid path before loading
            if bool(audio_path) and Path(audio_path).is_file():
                audio_provider.load_audio(audio_path)

                try:
                    self.vis_config.waveform.load_from_audio(audio_path)
                except:
                    logger.exception("Load Audio | Failed to load audio waveform data from audio file")
            
        except Exception as e:
            logger.exception("Load Audio | Failed to load audio")
            QMessageBox.critical(self, "Load Failed", f"Failed to load audio: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()

    # child tab API

    def on_config_changed(self):
        self.update_model()

        self.has_unsaved_changes = True
        self.refresh_window_title()

        # notify preview tab to redraw
        self.preview_widget.model_changed()

    def on_audio_changed(self):
        self._load_audio()

    def on_bg_image_changed(self):
        self._load_image()

    def on_bg_video_changed(self):
        self._load_video()

    def on_tracks_changed(self):
        self.update_model()

        # notify preview tab to redraw
        self.preview_widget.model_changed()

    def on_tab_changed(self, index: int):
        self.refresh_ui()

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

    def changeEvent(self, event):
        super().changeEvent(event)

        if event.type() == QEvent.Type.WindowStateChange:
            user_settings.fullscreen = self.isFullScreen()
            user_settings.save()

    # action callbacks

    def on_new_project_action(self):
        midi_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Open MIDI File",
            "",
            f"MIDI Files (*.mid *.midi)"
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
        except Exception as e:
            QMessageBox.critical(self, "Project Creation Failed", f'Unable to create new {Const.APP_NAME} project from provided midi file.\n\n{e}')
            return
            
        # import into local working model
        self.vis_config = VisConfig.create_from_midi_data(Path(midi_path).stem, midi_data)
        self.vis_config.init()
        self._load_config_resources()

        # update active project entry
        user_settings.active_project_path = None
        user_settings.save()

        # clear working state
        self.has_unsaved_changes = True # to prompt user to save this project
        self.refresh_window_title()
        self.refresh_file_menu()

        # re-init UI
        self.init_vis_config_editor_view()

    def on_update_project_action(self):
        midi_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select MIDI File",
            "",
            f"MIDI Files (*.mid *.midi)"
        )
        
        if not midi_path:
            return
        
        try:
            midi_data = pretty_midi.PrettyMIDI(midi_path)
        except Exception as e:
            QMessageBox.critical(self, "MIDI Update Failed", f'Unable to parse data from selected midi file.\n\n{e}')
            return
        
        midi_tracks: List[pretty_midi.Instrument] = midi_data.instruments
        midi_tracks_by_name = {t.name: t for t in midi_tracks}
        tracks = self.vis_config.tracks

        midi_names = {t.name for t in midi_tracks}
        track_names = {t.name for t in tracks}

        # 1. MIDI tracks not in vis_config tracks
        missing_from_config = [t for t in midi_tracks if t.name not in track_names]

        # 2. vis_config tracks not in MIDI tracks
        missing_from_midi = [t for t in tracks if t.name not in midi_names]

        # 3. tracks that show up in both
        matching_tracks = [t for t in tracks if t.name in midi_names]

        tracks_to_create: List[Track] = []
        for midi_track in missing_from_config:
            if len(midi_track.notes) == 0:
                continue # ignore track, no notes data

            msg = QMessageBox(self)
            msg.setWindowTitle("New MIDI Track")
            msg.setText(f'New track found in updated MIDI data:\n"{midi_track.name}"')
            add_btn = msg.addButton("Add", QMessageBox.AcceptRole)
            ignore_btn = msg.addButton("Ignore", QMessageBox.RejectRole)

            msg.setDefaultButton(add_btn)
            msg.exec()

            if msg.clickedButton() == add_btn:
                new_track = Track.create_from_midi_data(midi_track)
                new_track.init()
                tracks_to_create.append(new_track)

        tracks_to_delete: List[Track] = []
        for track in missing_from_midi:
            msg = QMessageBox(self)
            msg.setWindowTitle("Missing MIDI Track")
            msg.setText(f'Track missing from updated MIDI data:\n"{track.name}"')
            keep_btn = msg.addButton("Keep", QMessageBox.AcceptRole)
            delete_btn = msg.addButton("Delete", QMessageBox.RejectRole)

            msg.setDefaultButton(keep_btn)
            msg.exec()

            if msg.clickedButton() == delete_btn:
                tracks_to_delete.append(track)

        for track in matching_tracks:
            midi_track = midi_tracks_by_name[track.name]
            track.update_notes_from_midi_data(midi_track)

        # remove and add tracks
        for track in tracks_to_delete:
            self.vis_config.tracks.remove(track)

        self.vis_config.tracks.extend(tracks_to_create)

        # re-init UI with updated data
        self.on_config_changed()
        self.init_vis_config_editor_view()

        QMessageBox.information(
            self,
            "Update Project MIDI",
            f"Updated project tracks from MIDI data:\n"
            f"{len(matching_tracks)} updated\n"
            f"{len(tracks_to_create)} added\n"
            f"{len(tracks_to_delete)} removed"
        )

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
        self._load_config_resources()

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
            if self.preview_widget is not None:
                # notify preview widget to stop playback
                self.preview_widget.handle_export_starting()

            options = export_dialog.get_options()
            self.vis_config.export_dir = options.output_dir
            self.vis_config.export_filename = options.filename
            self.vis_config.export_format = options.render_format
            self.vis_config.export_resolution = options.resolution
            self.vis_config.export_fps = options.fps
            self.has_unsaved_changes = True
            self.refresh_window_title()

            self.export_progress_dialog = ExportProgressDialog(self.vis_config.track_name)
            self.export_progress_dialog.cancel_clicked.connect(self.on_render_cancel_requested)
            self.export_progress_dialog.show()
            self.setDisabled(True)

            self.render_thread = QThread()
            self.render_worker = RenderWorker(self.vis_config)

            self.render_worker.moveToThread(self.render_thread)

            self.render_thread.started.connect(self.render_worker.run)

            # connect ui to thread events
            self.render_worker.progress.connect(self.export_progress_dialog.update_progress)
            self.render_worker.finished.connect(self.on_render_finished)
            self.render_worker.cancelled.connect(self.on_render_cancelled)
            self.render_worker.failed.connect(self.on_render_failed)

            # cleanup thread on any result
            self.render_worker.finished.connect(self.render_thread.quit)
            self.render_worker.failed.connect(self.render_thread.quit)
            self.render_worker.cancelled.connect(self.render_thread.quit)

            self.render_thread.start()

    def on_export_logs_action(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Output Folder", str(Path.home() / "Desktop"))
        if folder:
            try:
                QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                LogUtil.zip_logs_to_dir(folder)
            except Exception as e:
                logger.exception("Failed to export logs to \"%s\"", folder)
                QMessageBox.critical(self, "Logs Export Failed", f"Failed to export logs image: {str(e)}")
            finally:
                QApplication.restoreOverrideCursor()
            
    
    # Render events

    def on_render_cancel_requested(self):
        self.render_worker.cancel()

    def on_render_cancelled(self):
        self.setDisabled(False)
        self.export_progress_dialog.hide()
        self.export_progress_dialog = None

    def on_render_failed(self, error: str):
        self.setDisabled(False)
        self.export_progress_dialog.hide()
        self.export_progress_dialog = None

        QMessageBox.critical(self, 'Export Failed', f"Failed to export video: {error}")

    def on_render_finished(self):
        open_file = self.export_progress_dialog.get_open_output_file()

        self.setDisabled(False)
        self.export_progress_dialog.hide()
        self.export_progress_dialog = None

        output_filepath = str(self.vis_config.get_exported_filepath())

        if open_file:
            if sys.platform == "darwin":
                subprocess.run(["open", output_filepath])
            elif sys.platform == "win32":
                os.startfile(output_filepath)
            else:  # linux
                subprocess.run(["xdg-open", output_filepath])
        else:
            QMessageBox.information(self, "Success", f"Exported video to {output_filepath}")
                
    # Key press callbacks
    def _on_space_pressed(self):
        if self.preview_widget is not None:
            self.preview_widget.handle_space_pressed()

    # Load Video Preview events
    def on_load_video_failed(self, error: str):
        self.setDisabled(False)
        self.load_video_progress_dialog.hide()
        self.load_video_progress_dialog = None
        QMessageBox.critical(self, 'Load Failed', f"Failed to load video preview: {error}")

    def on_load_video_finished(self):
        self.setDisabled(False)
        self.load_video_progress_dialog.hide()
        self.load_video_progress_dialog = None

    def on_load_video_progress(self, percent: int):
        self.load_video_progress_dialog.update_progress(percent)
