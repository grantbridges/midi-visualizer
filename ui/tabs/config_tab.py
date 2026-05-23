from PySide6.QtWidgets import (
    QSpinBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog
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
        self.bg_button.valueChanged.connect(self.on_changes_callback)

        self.playhead_pos_input = QSpinBox()
        self.playhead_pos_input.setRange(0, 100)
        self.playhead_pos_input.setSuffix('%')
        self.playhead_pos_input.setValue(self.vis_config.playhead_pos * 100)
        self.playhead_pos_input.valueChanged.connect(self.on_changes_callback)

        self.audio_file_input = QLineEdit(self.vis_config.audio_filepath)
        self.audio_file_input.setReadOnly(True)
        self.audio_file_browse_btn = QPushButton("Browse...")
        self.audio_file_browse_btn.clicked.connect(self.browse_audio_file)

        # layout controls
        v_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()
        v_left_layout = QVBoxLayout()

        background_color_layout = QHBoxLayout()
        background_color_layout.addWidget(QLabel("Background Color"))
        background_color_layout.addWidget(self.bg_button)
        v_left_layout.addLayout(background_color_layout)

        playhead_pos_layout = QHBoxLayout()
        playhead_pos_layout.addWidget(QLabel("Playhead Position"))
        playhead_pos_layout.addWidget(self.playhead_pos_input)
        v_left_layout.addLayout(playhead_pos_layout)

        audio_file_layout = QHBoxLayout()
        audio_file_layout.addWidget(QLabel("Audio File"))
        audio_file_layout.addWidget(self.audio_file_input)
        audio_file_layout.addWidget(self.audio_file_browse_btn)
        v_left_layout.addLayout(audio_file_layout)

        v_left_layout.addStretch()

        h_layout.addLayout(v_left_layout)
        h_layout.addStretch()

        v_layout.addLayout(h_layout)

    def refresh_ui(self):
        self.bg_button.rgb = self.vis_config.bg_color
        self.bg_button.refresh()

    def browse_audio_file(self):
        default_filepath = ""
        if self.vis_config.audio_filepath:
            default_filepath = self.vis_config.audio_filepath

        audio_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            default_filepath,
            "Audio Files (*.wav *.mp3 *.aiff *.aif *.flac *.m4a *.ogg)"
        )

        if audio_file:
            self.audio_file_input.setText(audio_file)
            self.on_changes_callback()

    def update_model(self):
        self.vis_config.bg_color = self.bg_button.rgb
        self.vis_config.playhead_pos = self.playhead_pos_input.value() / 100
        self.vis_config.audio_filepath = self.audio_file_input.text()