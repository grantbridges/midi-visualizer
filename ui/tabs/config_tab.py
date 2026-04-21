from PySide6.QtWidgets import (
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

        # layout controls
        v_layout = QVBoxLayout(self)

        background_color_layout = QHBoxLayout()
        background_color_layout.addWidget(QLabel("Background Color:"))
        background_color_layout.addWidget(self.bg_button)
        v_layout.addLayout(background_color_layout)

        v_layout.addStretch()

    def refresh_ui(self):
        self.bg_button.rgb = self.vis_config.bg_color
        self.bg_button.refresh()

    def update_model(self):
        self.vis_config.bg_color = self.bg_button.rgb