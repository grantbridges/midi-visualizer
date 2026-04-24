from PySide6.QtWidgets import (
    QSpinBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)

from models import VisConfig
from ui.common import ColorButton

class ConfigTab(QWidget):
    def __init__(self, on_changes_callback: object, vis_config: VisConfig):
        super().__init__()

        self.on_changes_callback = on_changes_callback
        self.vis_config = vis_config

        # create controls
        self.bg_button = ColorButton(self.vis_config.bg_color)
        self.playhead_pos_input = QSpinBox()
        self.playhead_pos_input.setRange(0, 100)
        self.playhead_pos_input.setSuffix('%')
        self.playhead_pos_input.setValue(self.vis_config.playhead_pos * 100)

        # layout controls
        v_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()
        v_left_layout = QVBoxLayout()

        background_color_layout = QHBoxLayout()
        background_color_layout.addWidget(QLabel("Background Color:"))
        background_color_layout.addWidget(self.bg_button)
        v_left_layout.addLayout(background_color_layout)

        playhead_pos_layout = QHBoxLayout()
        playhead_pos_layout.addWidget(QLabel("Playhead Position:"))
        playhead_pos_layout.addWidget(self.playhead_pos_input)
        v_left_layout.addLayout(playhead_pos_layout)

        v_left_layout.addStretch()

        h_layout.addLayout(v_left_layout)
        h_layout.addStretch()

        v_layout.addLayout(h_layout)

    def refresh_ui(self):
        self.bg_button.rgb = self.vis_config.bg_color
        self.bg_button.refresh()

    def update_model(self):
        self.vis_config.bg_color = self.bg_button.rgb
        self.vis_config.playhead_pos = self.playhead_pos_input.value() / 100