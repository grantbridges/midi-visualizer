from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
)

from models import VisConfig
from ui.common import PreviewWidget

class PreviewTab(QWidget):
    def __init__(self, vis_config: VisConfig):
        super().__init__()

        self.vis_config = vis_config

        # create controls
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self._toggle_play)
        self.pause_btn = QPushButton("Pause")
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
        self.play_btn.setText("Play" if self.preview_widget.is_playing() == False else "Stop")
    
    def update_model(self):
        pass

    def _toggle_play(self):
        if not self.preview_widget.is_playing():
            self.preview_widget.start()
        else:
            self.preview_widget.stop()
        
        self.refresh_ui()