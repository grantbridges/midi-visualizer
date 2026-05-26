from PySide6.QtWidgets import (
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
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

        self.show_playhead_checkbox = QCheckBox()
        self.show_playhead_checkbox.setChecked(self.vis_config.show_playhead)
        self.show_playhead_checkbox.toggled.connect(self.on_changes_callback)

        self.playhead_color_button = ColorButton(self.vis_config.playhead_color)
        self.playhead_color_button.valueChanged.connect(self.on_changes_callback)

        self.playhead_pos_input = QDoubleSpinBox()
        self.playhead_pos_input.setDecimals(2)
        self.playhead_pos_input.setRange(0.00, 1.00)
        self.playhead_pos_input.setSingleStep(0.01)
        self.playhead_pos_input.setValue(self.vis_config.playhead_pos_ratio)
        self.playhead_pos_input.valueChanged.connect(self.on_changes_callback)

        self.vertical_padding_input = QDoubleSpinBox()
        self.vertical_padding_input.setDecimals(2)
        self.vertical_padding_input.setRange(0.00, 1.00)
        self.vertical_padding_input.setSingleStep(.01)
        self.vertical_padding_input.setValue(self.vis_config.vertical_padding_ratio)
        self.vertical_padding_input.valueChanged.connect(self.on_changes_callback)

        self.vertical_offset_input = QDoubleSpinBox()
        self.vertical_offset_input.setDecimals(2)
        self.vertical_offset_input.setRange(-1.00, 1.00)
        self.vertical_offset_input.setSingleStep(.01)
        self.vertical_offset_input.setValue(self.vis_config.vertical_offset_ratio)
        self.vertical_offset_input.valueChanged.connect(self.on_changes_callback)

        self.fps_input = QSpinBox()
        self.fps_input.setRange(1, 120)
        self.fps_input.setValue(self.vis_config.fps)
        self.fps_input.valueChanged.connect(self.on_changes_callback)

        self.audio_file_input = QLineEdit(self.vis_config.audio_filepath)
        self.audio_file_input.setReadOnly(True)
        self.audio_file_browse_btn = QPushButton("Browse...")
        self.audio_file_browse_btn.clicked.connect(self.browse_audio_file)

        self.note_fadeout_input = QDoubleSpinBox()
        self.note_fadeout_input.setDecimals(2)
        self.note_fadeout_input.setRange(0.01, 1.00)
        self.note_fadeout_input.setSingleStep(.01)
        self.note_fadeout_input.setValue(self.vis_config.note_fadeout_ratio)
        self.note_fadeout_input.valueChanged.connect(self.on_changes_callback)

        self.note_play_color_button = ColorButton(self.vis_config.note_play_color)
        self.note_play_color_button.valueChanged.connect(self.on_changes_callback)

        # layout controls
        v_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()
        v_left_layout = QVBoxLayout()
        v_right_layout = QVBoxLayout()

        # Left Column
        audio_file_layout = QHBoxLayout()
        audio_file_layout.addWidget(QLabel("Audio File"))
        audio_file_layout.addWidget(self.audio_file_input)
        audio_file_layout.addWidget(self.audio_file_browse_btn)
        v_left_layout.addLayout(audio_file_layout)

        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS"))
        fps_layout.addWidget(self.fps_input)
        v_left_layout.addLayout(fps_layout)

        background_color_layout = QHBoxLayout()
        background_color_layout.addWidget(QLabel("Background Color"))
        background_color_layout.addWidget(self.bg_button)
        v_left_layout.addLayout(background_color_layout)

        show_playhead_layout = QHBoxLayout()
        show_playhead_layout.addWidget(QLabel("Show Playhead"))
        show_playhead_layout.addWidget(self.show_playhead_checkbox)
        v_left_layout.addLayout(show_playhead_layout)

        playhead_color_layout = QHBoxLayout()
        playhead_color_layout.addWidget(QLabel("Playhead Color"))
        playhead_color_layout.addWidget(self.playhead_color_button)
        v_left_layout.addLayout(playhead_color_layout)

        playhead_pos_layout = QHBoxLayout()
        playhead_pos_layout.addWidget(QLabel("Playhead Position"))
        playhead_pos_layout.addWidget(self.playhead_pos_input)
        v_left_layout.addLayout(playhead_pos_layout)

        vertical_padding_layout = QHBoxLayout()
        vertical_padding_layout.addWidget(QLabel("Vertical Padding"))
        vertical_padding_layout.addWidget(self.vertical_padding_input)
        v_left_layout.addLayout(vertical_padding_layout)

        vertifcal_offset_layout = QHBoxLayout()
        vertifcal_offset_layout.addWidget(QLabel("Vertical Offset"))
        vertifcal_offset_layout.addWidget(self.vertical_offset_input)
        v_left_layout.addLayout(vertifcal_offset_layout)

        v_left_layout.addStretch()

        # Right Column
        note_fadeout_layout = QHBoxLayout()
        note_fadeout_layout.addWidget(QLabel("Note Fadeout"))
        note_fadeout_layout.addWidget(self.note_fadeout_input)
        v_right_layout.addLayout(note_fadeout_layout)

        note_play_color_layout = QHBoxLayout()
        note_play_color_layout.addWidget(QLabel("Note Play Color"))
        note_play_color_layout.addWidget(self.note_play_color_button)
        v_right_layout.addLayout(note_play_color_layout)

        v_right_layout.addStretch()

        h_layout.addLayout(v_left_layout, 1)
        h_layout.addLayout(v_right_layout, 1)

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
        # pull UI values out of controls and set on model
        self.vis_config.audio_filepath = self.audio_file_input.text()
        self.vis_config.fps = self.fps_input.value()
        self.vis_config.bg_color = self.bg_button.rgb

        self.vis_config.show_playhead = self.show_playhead_checkbox.isChecked()
        self.vis_config.playhead_color = self.playhead_color_button.rgb
        self.vis_config.playhead_pos_ratio = self.playhead_pos_input.value()

        self.vis_config.vertical_padding_ratio = self.vertical_padding_input.value()
        self.vis_config.vertical_offset_ratio = self.vertical_offset_input.value()

        self.vis_config.note_fadeout_ratio = self.note_fadeout_input.value()
        self.vis_config.note_play_color = self.note_play_color_button.rgb