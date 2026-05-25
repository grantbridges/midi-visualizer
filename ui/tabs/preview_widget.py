from enum import Enum
import time
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QFont, QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QSlider,
)
from common import Const, Color
from models import VisConfig
from render import MidiRenderUtil
from utility import QUtil
from ui.common import PreviewCanvas

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
        self.initialized = False

        # computed and cached for quick lookup
        self.pitch_min: int = 0
        self.pitch_max: int = 0

        # create controls
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self._toggle_play)
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self._reset)
        self.mute_checkbox = QCheckBox("Mute")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self._on_slider_changed)

        self.preview_canvas = PreviewCanvas(parent=self)

        self.timer.start(int(1000 / Const.FPS))

    def layout_controls(self):
        # layout controls
        v_layout = QVBoxLayout(self)

        top_row_layout = QHBoxLayout()
        top_row_layout.addWidget(self.play_btn)
        top_row_layout.addWidget(self.reset_btn)
        top_row_layout.addWidget(self.mute_checkbox)
        top_row_layout.addStretch()
        v_layout.addLayout(top_row_layout)

        slider_bar_layout = QHBoxLayout()
        slider_bar_layout.addWidget(self.slider)
        v_layout.addLayout(slider_bar_layout)

        self.preview_canvas.setFixedWidth(Const.SCREEN_WIDTH)
        self.preview_canvas.setFixedHeight(Const.SCREEN_HEIGHT / 2)
        v_layout.addWidget(self.preview_canvas)

    def model_changed(self):
        if self.vis_config is not None:
            self.pitch_min = self.vis_config.get_min_pitch()
            self.pitch_max = self.vis_config.get_max_pitch()

            # calculate start/end time for preview area
            new_start_time = MidiRenderUtil.calc_start_time(self.vis_config, self.preview_canvas.width())
            new_end_time = MidiRenderUtil.calc_end_time(self.vis_config, self.preview_canvas.width())

            if self.start_time != new_start_time or self.end_time != new_end_time:
                # if time bounds changed, reset position
                self.playing = False
                self.start_time = new_start_time
                self.end_time = new_end_time
                self.current_time = self.start_time
                self._update_slider_position()

        self._refresh_canvas()
        self.refresh_ui()

    def refresh_ui(self):
        self.play_btn.setText("▶ Play" if not self.playing else "⏹ Stop")

    def _on_tick(self):
        # only update widget if playing and user isn't dragging slider
        if self.playing and not self.slider.isSliderDown():
            if self.playing == True:
                self.current_time += 1 / float(Const.FPS) # iterate one frame

                if self.current_time > self.end_time:
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