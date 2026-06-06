from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QScrollArea,
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
    def __init__(self, vis_config: VisConfig, on_changes_callback: object, parent=None):
        super().__init__(parent)

        self.on_changes_callback = on_changes_callback
        self.vis_config = vis_config

        self.block_changes_callback: bool = False

        # create controls
        self.track_name = QLineEdit()
        self.track_name.editingFinished.connect(self._on_changes)

        self.bg_button = ColorButton()
        self.bg_button.valueChanged.connect(self._on_changes)

        self.show_playhead_checkbox = QCheckBox()
        self.show_playhead_checkbox.toggled.connect(self._on_changes)

        self.playhead_color_button = ColorButton()
        self.playhead_color_button.valueChanged.connect(self._on_changes)

        self.playhead_pos_input = QDoubleSpinBox(decimals=2, minimum=0.00, maximum=1.00, singleStep=0.01)
        self.playhead_pos_input.valueChanged.connect(self._on_changes)

        self.vertical_padding_input = QDoubleSpinBox(decimals=2, minimum=0.00, maximum=1.00, singleStep=0.01)
        self.vertical_padding_input.valueChanged.connect(self._on_changes)

        self.vertical_offset_input = QDoubleSpinBox(decimals=2, minimum=-1.00, maximum=1.00, singleStep=0.01)
        self.vertical_offset_input.valueChanged.connect(self._on_changes)

        self.fps_input = QSpinBox(minimum=1, maximum=120)
        self.fps_input.valueChanged.connect(self._on_changes)

        self.audio_file_input = QLineEdit(readOnly=True)
        self.audio_file_browse_btn = QPushButton("...")
        self.audio_file_browse_btn.clicked.connect(self.browse_audio_file)

        self.note_fadeout_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.00, singleStep=.01)
        self.note_fadeout_input.valueChanged.connect(self._on_changes)

        self.note_play_color_button = ColorButton()
        self.note_play_color_button.valueChanged.connect(self._on_changes)

        self.auto_calc_pitch_bounds_checkbox = QCheckBox()
        self.auto_calc_pitch_bounds_checkbox.toggled.connect(self._on_changes)

        self.pitch_min_input = QSpinBox()
        self.pitch_min_input.valueChanged.connect(self._on_changes)

        self.pitch_max_input = QSpinBox()      
        self.pitch_max_input.valueChanged.connect(self._on_changes)

    def shutdown(self):
        pass

    def layout_controls(self):
        # layout controls
        root = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        h_layout = QHBoxLayout()
        v_left_layout = QVBoxLayout()
        v_right_layout = QVBoxLayout()
        v_left_layout.setSpacing(2)
        v_right_layout.setSpacing(2)

        # Left Column
        track_name_layout = QHBoxLayout()
        track_name_layout.addWidget(QLabel("Track Name"))
        track_name_layout.addStretch()
        track_name_layout.addWidget(self.track_name)
        v_left_layout.addLayout(track_name_layout)

        audio_file_layout = QHBoxLayout()
        audio_file_layout.addWidget(QLabel("Audio File"))
        audio_file_layout.addStretch()
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

        vertical_offset_layout = QHBoxLayout()
        vertical_offset_layout.addWidget(QLabel("Vertical Offset"))
        vertical_offset_layout.addWidget(self.vertical_offset_input)
        v_left_layout.addLayout(vertical_offset_layout)

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

        auto_calc_pitch_bounds_layout = QHBoxLayout()
        auto_calc_pitch_bounds_layout.addWidget(QLabel("Auto-Calc Pitch Min/Max"))
        auto_calc_pitch_bounds_layout.addWidget(self.auto_calc_pitch_bounds_checkbox)
        v_right_layout.addLayout(auto_calc_pitch_bounds_layout)

        pitch_min_layout = QHBoxLayout()
        pitch_min_layout.addWidget(QLabel("Pitch Min"))
        pitch_min_layout.addWidget(self.pitch_min_input)
        v_right_layout.addLayout(pitch_min_layout)

        pitch_max_layout = QHBoxLayout()
        pitch_max_layout.addWidget(QLabel("Pitch Max"))
        pitch_max_layout.addWidget(self.pitch_max_input)
        v_right_layout.addLayout(pitch_max_layout)

        v_right_layout.addStretch()

        h_layout.addLayout(v_left_layout, 1)
        h_layout.addLayout(v_right_layout, 1)

        content_layout.addLayout(h_layout)
        
        scroll_area.setWidget(content)

        root.addWidget(scroll_area)

    def refresh_ui(self):
        self.block_changes_callback = True # prevent "change" callbacks from triggering while we set values

        self.track_name.setText(self.vis_config.track_name)
        self.fps_input.setValue(self.vis_config.fps)

        self.bg_button.setColor(self.vis_config.bg_color)

        self.show_playhead_checkbox.setChecked(self.vis_config.show_playhead)
        self.playhead_color_button.setColor(self.vis_config.playhead_color)
        self.playhead_pos_input.setValue(self.vis_config.playhead_pos_ratio)

        self.vertical_padding_input.setValue(self.vis_config.vertical_padding_ratio)
        self.vertical_offset_input.setValue(self.vis_config.vertical_offset_ratio)

        self.audio_file_input.setText(self.vis_config.audio_filepath)

        self.note_fadeout_input.setValue(self.vis_config.note_fadeout_ratio)
        self.note_play_color_button.setColor(self.vis_config.note_play_color)

        self.auto_calc_pitch_bounds_checkbox.setChecked(self.vis_config.auto_calc_pitch_bounds)

        self.pitch_min_input.setDisabled(self.vis_config.auto_calc_pitch_bounds)
        self.pitch_min_input.setRange(0, self.vis_config.manual_pitch_max)
        self.pitch_min_input.setValue(self.vis_config.get_min_pitch() if self.vis_config.auto_calc_pitch_bounds else self.vis_config.manual_pitch_min)

        self.pitch_max_input.setDisabled(self.vis_config.auto_calc_pitch_bounds)
        self.pitch_max_input.setRange(self.vis_config.manual_pitch_min, 127)
        self.pitch_max_input.setValue(self.vis_config.get_max_pitch() if self.vis_config.auto_calc_pitch_bounds else self.vis_config.manual_pitch_max)  

        self.block_changes_callback = False

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
            self._on_changes()

    def update_model(self):
        # pull UI values out of controls and set on model
        self.vis_config.track_name = self.track_name.text()
        self.vis_config.audio_filepath = self.audio_file_input.text()
        self.vis_config.fps = self.fps_input.value()
        self.vis_config.bg_color = self.bg_button.getColor()

        self.vis_config.show_playhead = self.show_playhead_checkbox.isChecked()
        self.vis_config.playhead_color = self.playhead_color_button.getColor()
        self.vis_config.playhead_pos_ratio = self.playhead_pos_input.value()

        self.vis_config.vertical_padding_ratio = self.vertical_padding_input.value()
        self.vis_config.vertical_offset_ratio = self.vertical_offset_input.value()

        self.vis_config.note_fadeout_ratio = self.note_fadeout_input.value()
        self.vis_config.note_play_color = self.note_play_color_button.getColor()

        if not self.vis_config.auto_calc_pitch_bounds:
            self.vis_config.manual_pitch_min = self.pitch_min_input.value()
            self.vis_config.manual_pitch_max = self.pitch_max_input.value()
        
        self.vis_config.auto_calc_pitch_bounds = self.auto_calc_pitch_bounds_checkbox.isChecked()

    def _on_changes(self):
        if not self.block_changes_callback:
            self.on_changes_callback()
