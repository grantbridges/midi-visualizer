from enum import Enum
import time
from uuid import UUID
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QAction, QFont, QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QMenu,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QSlider,
)
from common import Const, Color
from models import VisConfig, user_settings
from render import MidiRenderUtil
from utility import QUtil, Util
from ui.widgets.preview_canvas import PreviewCanvas

class PreviewWidget(QWidget):
    def __init__(self, vis_config: VisConfig, parent=None):
        super().__init__(parent)

        self.vis_config = vis_config
        self.current_fps = 60
        if self.vis_config is not None:
            self.current_fps = self.vis_config.fps

        self.playing = False
        self.start_time = 0.0
        self.end_time = 1.0
        self.current_time = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(int(1000 / self.current_fps))

        # computed and cached for quick lookup
        self.pitch_min: int = 0
        self.pitch_max: int = 0

        # create controls
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self._toggle_play)
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self._reset)
        self.mute_checkbox = QCheckBox("Mute")
        self.mute_checkbox.setChecked(user_settings.mute_audio)
        self.mute_checkbox.toggled.connect(self._on_mute_toggled)
        self.loop_checkbox = QCheckBox("Loop")
        self.loop_checkbox.setChecked(user_settings.loop_preview)
        self.loop_checkbox.toggled.connect(self._on_loop_toggled)

        # create button
        self.settings_btn = QPushButton("⚙")
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

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self._on_slider_changed)

        self.preview_canvas = PreviewCanvas(parent=self)

    def shutdown(self):
        self.timer.stop()

    def layout_controls(self):
        # layout controls
        v_layout = QVBoxLayout(self)

        top_row_layout = QHBoxLayout()
        top_row_layout.addWidget(self.play_btn)
        top_row_layout.addWidget(self.reset_btn)
        # top_row_layout.addWidget(self.mute_checkbox) # TODO when audio preview is supported
        top_row_layout.addWidget(self.loop_checkbox)
        top_row_layout.addStretch()
        top_row_layout.addWidget(self.settings_btn)
        v_layout.addLayout(top_row_layout)

        slider_bar_layout = QHBoxLayout()
        slider_bar_layout.addWidget(self.slider)
        v_layout.addLayout(slider_bar_layout)

        v_layout.addWidget(self.preview_canvas)

    def handle_resize(self, screen_width: int, screen_height: int):
        self.preview_canvas.setFixedWidth(screen_width)
        self.preview_canvas.setFixedHeight(screen_height / 2 - 100)

    def model_changed(self):
        if self.vis_config is not None:
            if self.current_fps != self.vis_config.fps:
                # reset timer with new fps
                self.current_fps = self.vis_config.fps
                self.timer.stop()
                self.timer.start(int(1000 / self.current_fps))

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
                self.playing = False
                self.start_time = new_start_time
                self.end_time = new_end_time
                if self.start_time == self.end_time:
                    self.end_time += 1 # prevent divide by 0

                if was_time_at_start:
                    self.current_time = self.start_time
                elif was_time_at_end:
                    self.current_time = self.end_time
                else:
                    # apply clamping to ensure current time stays in bounds
                    self.current_time = Util.clamp(self.current_time, self.start_time, self.end_time)

                self._update_slider_position()

        self._refresh_canvas()
        self.refresh_ui()

    def refresh_ui(self):
        self.play_btn.setText("▶ Play" if not self.playing else "⏹ Stop")

    def set_selected_group_id(self, group_id: UUID | None):
        self.preview_canvas.set_selected_group_id(group_id)

    # private methods

    def _on_tick(self):
        # only update widget if playing and user isn't dragging slider
        if self.playing and not self.slider.isSliderDown():
            if self.playing == True:
                self.current_time += 1 / float(self.vis_config.fps) # iterate one frame

                if self.current_time > self.end_time:
                    if user_settings.loop_preview:
                        self.current_time = self.start_time
                    else:
                        self._stop()

            self._update_slider_position()
            self._refresh_canvas()

    def _refresh_canvas(self):
        self.preview_canvas.refresh(
            self.current_time, 
            self.vis_config, 
            self.pitch_min, 
            self.pitch_max
        )

    def _toggle_play(self):
        if self.playing == False:
            self._play()
        else:
            self._stop()

    def _reset(self):
        self.playing = False
        self.current_time = self.start_time
        self._update_slider_position()
        self._refresh_canvas()

        self.refresh_ui()

    def _update_slider_position(self):
        # set slider position from current time
        t_norm = (self.current_time - self.start_time) / (self.end_time - self.start_time)
        slider_value = int(t_norm * 1000)
        slider_value = max(0, min(1000, slider_value)) # clamp
        self.slider.setValue(slider_value)

    def _on_mute_toggled(self, checked: bool):
        user_settings.mute_audio = checked
        user_settings.save()

    def _on_loop_toggled(self, checked: bool):
        user_settings.loop_preview = checked
        user_settings.save()

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

    def _on_slider_changed(self, value):
        # only apply if this is a user-driven movement
        if self.slider.isSliderDown():
            t_norm = value / 1000
            self.current_time = self.start_time + t_norm * (self.end_time - self.start_time)
            self._refresh_canvas()

    def _play(self):
        self.playing = True      
        self.refresh_ui()

    def _stop(self):
        self.playing = False
        self.refresh_ui()