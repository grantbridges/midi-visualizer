from enum import Enum
import time
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QSlider,
)
from common import Const
from models import VisConfig
from ui.common import PreviewWidget

class PreviewTab(QWidget):
    def __init__(self, vis_config: VisConfig):
        super().__init__()

        self.vis_config = vis_config

        self.playing = False
        self.start_time = 0.0
        self.end_time = 1.0
        self.current_time = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.initialized = False

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

        self.preview_widget = PreviewWidget(self.vis_config)

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

        v_layout.addWidget(self.preview_widget)

    def model_changed(self):
        # flip flag and we'll reinitialize on next show
        self.initialized = False

    def on_hide(self):
        self.timer.stop()

    def on_show(self):
        self.timer.start(int(1000 / Const.FPS))

        if not self.initialized:
            # calculate start/end time with visible preview widget size
            self.playing = False
            self.start_time = self.preview_widget.calculate_start_time()
            self.end_time = self.preview_widget.calculate_end_time()
            self.current_time = self.start_time
            self._update_slider_position()
            self.preview_widget.tick(self.current_time)

            self.initialized = True

        self.refresh_ui()

    def refresh_ui(self):
        self.play_btn.setText("▶ Play" if not self.playing else "⏹ Stop")

    def _on_tick(self):
        # only update widget if playing and user isn't dragging slider
        if self.playing and not self.slider.isSliderDown():
            if self.playing == True:
                self.current_time += 1 / float(Const.FPS) # iterate one frame
                # don't exceed max
                self.current_time = min(self.current_time, self.end_time)

            self._update_slider_position()
            self.preview_widget.tick(self.current_time)

    def _toggle_play(self):
        if self.playing == False:
            self._play()
        else:
            self._stop()

    def _reset(self):
        self.current_time = self.start_time
        self._update_slider_position()
        self.preview_widget.tick(self.current_time)

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
            self.preview_widget.tick(self.current_time)

    def _play(self):
        self.playing = True      
        self.refresh_ui()

    def _stop(self):
        self.playing = False
        self.refresh_ui()