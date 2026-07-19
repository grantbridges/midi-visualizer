from uuid import UUID
from PySide6.QtCore import Qt, QTimer, QElapsedTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMenu,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QSlider,
    QDoubleSpinBox
)
from models import VisConfig, user_settings
from utility import Util
from ui.widgets.preview_canvas import PreviewCanvas
from ui.widgets.minimap_canvas import MinimapCanvas
from ui.common import Icons
from media import audio_provider
import logging
logger = logging.getLogger("PreviewWidget")

PREVIEW_MIN_HEIGHT = 240

# qta-browser

class PreviewWidget(QWidget):
    def __init__(self, vis_config: VisConfig, parent=None):
        super().__init__(parent)

        self.vis_config = vis_config

        self.playing = False
        self.start_time = 0.0
        self.end_time = 1.0
        self.current_time = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(20)

        self.audio_sync_tolerance_sec: float = 0.25

        self.play_timer = QElapsedTimer()
        self.play_start_visual_time = 0.0

        # computed and cached for quick lookup
        self.pitch_min: int = 0
        self.pitch_max: int = 0

        # create controls
        self.play_btn = QPushButton() # icon set in refresh ui
        self.play_btn.clicked.connect(self._toggle_play)
        self.reset_btn = QPushButton()
        self.reset_btn.setIcon(Icons.rewind())
        self.reset_btn.clicked.connect(self._reset)
        self.mute_btn = QPushButton() # icon set in refresh UI
        self.mute_btn.clicked.connect(self._toggle_mute)
        self.loop_btn = QPushButton() # icon set in refresh ui
        self.loop_btn.clicked.connect(self._on_loop_toggled)
        self.step_input = QDoubleSpinBox(decimals=2, value = 0.05, minimum=0.01, maximum=10.00, singleStep=0.01, suffix=" sec")
        self.step_fwd_btn = QPushButton()
        self.step_fwd_btn.setIcon(Icons.skip_fwd())
        self.step_fwd_btn.clicked.connect(lambda: self._step(self.step_input.value()))
        self.step_back_btn = QPushButton()
        self.step_back_btn.setIcon(Icons.skip_back())
        self.step_back_btn.clicked.connect(lambda: self._step(-1 * self.step_input.value()))

        # create button
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(Icons.gear())
        self.settings_btn.setFixedWidth(32)

        # create settings menu
        # (I did this in extreme shorthand to keep it easy to add configs here)
        settings_menu = QMenu(self)
        for action in [
            self._create_settings_action("Show Time Display", "show_time_display"),
            self._create_settings_action("Show Guides", "show_guides"),
            self._create_settings_action("Show Pitch Lines", "show_pitches"),
            self._create_settings_action("Show Track Groups", "show_track_groups")
        ]:
            settings_menu.addAction(action)

        self.settings_btn.setMenu(settings_menu)

        self.minimap_canvas = MinimapCanvas(parent=self)
        self.minimap_canvas.valueChanged.connect(self._on_slider_changed)
        self.preview_canvas = PreviewCanvas(parent=self)

    def shutdown(self):
        self.timer.stop()

    def layout_controls(self):
        v_layout = QVBoxLayout(self)

        self.top_bar_widget = QWidget()
        top_row_layout = QHBoxLayout(self.top_bar_widget)
        top_row_layout.setContentsMargins(0, 0, 0, 0)

        group_spacing = 25

        top_row_layout.addWidget(self.mute_btn)
        top_row_layout.addStretch()
        top_row_layout.addWidget(self.reset_btn)
        top_row_layout.addSpacing(group_spacing)
        top_row_layout.addWidget(self.step_back_btn)
        top_row_layout.addWidget(self.play_btn)
        #top_row_layout.addWidget(self.step_input)
        top_row_layout.addWidget(self.step_fwd_btn)
        top_row_layout.addSpacing(group_spacing)
        top_row_layout.addWidget(self.loop_btn)
        top_row_layout.addStretch()
        top_row_layout.addWidget(self.settings_btn)

        v_layout.addWidget(self.minimap_canvas)
        v_layout.addWidget(self.preview_canvas, stretch=1)
        v_layout.addWidget(self.top_bar_widget)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.minimap_canvas.set_dirty()

    def handle_export_starting(self):
        self._stop()

    def handle_space_pressed(self):
        self._toggle_play()
        
    def model_changed(self):
        if self.vis_config is not None:
            self.pitch_min = self.vis_config.get_min_pitch()
            self.pitch_max = self.vis_config.get_max_pitch()

            # calculate start/end time for preview area
            new_start_time = self.vis_config.get_min_time()
            new_end_time = self.vis_config.get_max_time()

            if self.start_time != new_start_time or self.end_time != new_end_time:
                # store whether current time was at existing start/end position so
                # we can reset it there after updating time range
                was_time_at_start = Util.is_equal(self.current_time, self.start_time)
                was_time_at_end = Util.is_equal(self.current_time, self.end_time)

                # if time bounds changed, reset position
                self.start_time = new_start_time
                self.end_time = new_end_time
                if self.start_time == self.end_time:
                    self.end_time += 1 # prevent divide by 0

                if was_time_at_start:
                    self._set_current_time(self.start_time)
                elif was_time_at_end:
                    self._set_current_time(self.end_time)
                else:
                    # apply clamping to ensure current time stays in bounds
                    self._set_current_time(Util.clamp(self.current_time, self.start_time, self.end_time))

        self.minimap_canvas.set_dirty()
        self._refresh_canvas()
        self.refresh_ui()

    def refresh_ui(self):
        self.play_btn.setIcon(Icons.play() if not self.playing else Icons.pause())

        self.step_back_btn.setDisabled(self.playing)
        self.step_fwd_btn.setDisabled(self.playing)
        self.step_input.setDisabled(self.playing)

        self.loop_btn.setIcon(Icons.arrow_right_thin() if not user_settings.loop_preview else Icons.loop())

        self.mute_btn.setIcon(Icons.audio() if not user_settings.mute_audio else Icons.muted())
        self.mute_btn.setEnabled(self.vis_config.has_audio())


    def set_selected_group_id(self, group_id: UUID | None):
        self.preview_canvas.set_selected_group_id(group_id)

    # private methods

    def _on_tick(self):
        # only update widget if playing and user isn't dragging slider
        if self.playing and not self.minimap_canvas.is_slider_down():
            if self.playing == True:
                # calculate current time from how long has elapsed since play start
                elapsed_sec = self.play_timer.elapsed() / 1000.0
                self.current_time = self.play_start_visual_time + elapsed_sec
                #logger.debug(f"Current Time (tick): {self.current_time:.2f} s")

                if self.current_time > self.end_time:
                    if user_settings.loop_preview:
                        self._set_current_time(self.start_time)
                    else:
                        self._set_current_time(self.end_time)
                        self._stop()
                
                if self.vis_config.has_audio():
                    if self.current_time >= 0.0:
                        if not audio_provider.is_playing():
                            audio_provider.play_at(self.current_time)
                        else:
                            # check if audio has fallen out of sync with timing and re-sync
                            if self.current_time <= audio_provider.get_duration_seconds():
                                audio_out_of_sync_sec = abs(audio_provider.get_position_seconds() - self.current_time)
                                if audio_out_of_sync_sec >= self.audio_sync_tolerance_sec:
                                    # logger.debug(f"Audio out of sync by {audio_out_of_sync_sec:.2f} sec - resyncing")
                                    audio_provider.seek_seconds(self.current_time)
                    else:
                        if audio_provider.is_playing():
                            audio_provider.stop()
                else:
                    if audio_provider.is_playing():
                        audio_provider.stop()

            self._refresh_canvas()


    def _refresh_canvas(self):
        self.minimap_canvas.refresh(
            self.current_time,
            self.vis_config,
            self.start_time, 
            self.end_time,
            self.pitch_min, 
            self.pitch_max
        )

        self.preview_canvas.refresh(
            self.current_time,
            self.vis_config,
            self.start_time, 
            self.end_time,
            self.pitch_min, 
            self.pitch_max
        )

    def _toggle_play(self):
        if self.playing == False:
            self._play()
        else:
            self._stop()
    
    def _step(self, time_inc: float):
        step_to_time = self.current_time + time_inc
        step_to_time = Util.clamp(step_to_time, self.start_time, self.end_time)

        if step_to_time is not self.current_time: 
            self._set_current_time(step_to_time)
            self._refresh_canvas()
            self.refresh_ui()

    def _toggle_mute(self):
        user_settings.mute_audio = not user_settings.mute_audio
        user_settings.save()

        self.refresh_ui()

        audio_provider.refresh_mute_state()

    def _on_loop_toggled(self):
        user_settings.loop_preview = not user_settings.loop_preview
        user_settings.save()

        self.refresh_ui()

    def _create_settings_action(self, label: str, property_name: str) -> QAction:
        action = QAction(label, self)
        action.setCheckable(True)
        action.setChecked(getattr(user_settings, property_name))

        def on_triggered(checked: bool):
            setattr(user_settings, property_name, checked)
            user_settings.save()
            self._refresh_canvas()

        action.triggered.connect(on_triggered)

        return action

    def _on_user_setting_toggled(self, property_name: str, checked: bool):
        setattr(user_settings, property_name, checked)
        user_settings.save()
        self._refresh_canvas()

    def _on_slider_changed(self, new_time: float):
        if audio_provider.is_playing():
            audio_provider.stop() # will resume during tick

        self._set_current_time(new_time)

        self._refresh_canvas()

    def _play(self):
        self.playing = True

        self.play_start_visual_time = self.current_time
        self.play_timer.restart()

        self.refresh_ui()

    def _stop(self):
        self.playing = False
        audio_provider.stop()
        self.refresh_ui()

    def _reset(self):
        self._set_current_time(self.start_time)

        audio_provider.stop() # will restart on tick
        self._refresh_canvas()

        self.refresh_ui()

    def _set_current_time(self, time: float):
        self.current_time = time
        #logger.debug(f"Current Time: {self.current_time:.2f} s")

        # reset when this "play" context started from
        self.play_start_visual_time = self.current_time
        self.play_timer.restart()