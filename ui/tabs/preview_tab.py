from enum import Enum
import time
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
)
from common import Const
from models import VisConfig
from ui.common import PreviewWidget

class PreviewState(str, Enum):
    Stopped = "Stopped"
    Playing = "Playing"
    Paused = "Paused"

class PreviewTab(QWidget):
    def __init__(self, vis_config: VisConfig):
        super().__init__()

        self.vis_config = vis_config

        self.state = PreviewState.Stopped

        # computed at preview start
        self.start_time = 0.0
        self.preview_time = 0.0 # sec since start of preview loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)

        # create controls
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self._toggle_play)
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self._toggle_pause)
        self.mute_checkbox = QCheckBox("Mute")

        self.preview_widget = PreviewWidget(self.vis_config)

        # layout controls
        v_layout = QVBoxLayout(self)

        top_row_layout = QHBoxLayout()
        top_row_layout.addWidget(self.play_btn)
        top_row_layout.addWidget(self.pause_btn)
        top_row_layout.addWidget(self.mute_checkbox)
        top_row_layout.addStretch()
        v_layout.addLayout(top_row_layout)

        v_layout.addWidget(self.preview_widget)

    def refresh_ui(self):
        self.play_btn.setText("Play" if self.state == PreviewState.Stopped else "Stop")

        # hide pause btn when stopped
        self.pause_btn.setVisible(self.state is not PreviewState.Stopped)
        self.pause_btn.setText("Resume" if self.state == PreviewState.Paused else "Pause")
    
    def update_model(self):
        pass

    def _on_tick(self):
        if self.state == PreviewState.Playing: 
            self.preview_time += 1 / float(Const.FPS) # iterate one frame-second

        current_time = self.start_time + self.preview_time
        self.preview_widget.tick(current_time)

    def _toggle_play(self):
        if self.state == PreviewState.Stopped:
            self.state = PreviewState.Playing
            
            self.preview_time = 0.0
            time_min = self.vis_config.get_min_time()

            # TODO I think this would be a lot easier if we just consider the right edge of the screen
            # as time = 0 instead of the playhead
            self.start_time = time_min - self.preview_widget.calculate_start_time_offset()

            self.preview_widget.reset()
            self.preview_widget.tick(self.start_time)
            self.preview_widget.set_active(True)
            
            self.timer.start(int(1000 / Const.FPS))
        else: # playing or paused
            self.state = PreviewState.Stopped
            self.preview_widget.set_active(False)

            self.timer.stop()
        
        self.refresh_ui()

    def _toggle_pause(self):
        if self.state == PreviewState.Playing:
            self.state = PreviewState.Paused
        else:
            self.state = PreviewState.Playing

        self.refresh_ui()