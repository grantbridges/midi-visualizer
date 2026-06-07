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
    QComboBox,
    QFileDialog
)

from models import VisConfig, BackgroundMode
from ui.common import ColorButton, SectionDivider

class ConfigTab(QWidget):
    def __init__(self, vis_config: VisConfig, on_changes_callback: object, parent=None):
        super().__init__(parent)

        self.on_changes_callback = on_changes_callback
        self.vis_config = vis_config

        self.block_changes_callback: bool = False

        # create controls
        self.track_name = QLineEdit()
        self.track_name.editingFinished.connect(self._on_changes)

        self.fps_input = QSpinBox(minimum=1, maximum=120)
        self.fps_input.valueChanged.connect(self._on_changes)

        self.bg_mode_combo = QComboBox()
        for mode in BackgroundMode:
            self.bg_mode_combo.addItem(mode.name, mode)
        self.bg_mode_combo.currentIndexChanged.connect(self._on_changes)

        self.bg_button = ColorButton()
        self.bg_button.valueChanged.connect(self._on_changes)

        self.bg_image_file_input = QLineEdit(readOnly=True)
        self.bg_image_file_browse_btn = QPushButton("...")
        self.bg_image_file_browse_btn.clicked.connect(self._browse_bg_image_file)

        self.bg_video_file_input = QLineEdit(readOnly=True)
        self.bg_video_file_browse_btn = QPushButton("...")
        self.bg_video_file_browse_btn.clicked.connect(self._browse_bg_video_file)

        self.use_audio_checkbox = QCheckBox()
        self.use_audio_checkbox.toggled.connect(self._on_changes)

        self.audio_file_input = QLineEdit(readOnly=True)
        self.audio_file_browse_btn = QPushButton("...")
        self.audio_file_browse_btn.clicked.connect(self._browse_audio_file)

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

        self.apply_time_offsets_checkbox = QCheckBox()
        self.apply_time_offsets_checkbox.toggled.connect(self._on_changes)

        self.start_time_input = QDoubleSpinBox(decimals=2, minimum=-10.0, maximum=10.0, singleStep=0.01, suffix=" sec")
        self.start_time_input.valueChanged.connect(self._on_changes)

        self.end_time_input = QDoubleSpinBox(decimals=2, minimum=-10.0, maximum=10.0, singleStep=0.01, suffix=" sec")
        self.end_time_input.valueChanged.connect(self._on_changes)

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
        v_left_layout.addWidget(SectionDivider("Track Props"))

        track_name_layout = QHBoxLayout()
        track_name_layout.addWidget(QLabel("Track Name"))
        track_name_layout.addStretch()
        track_name_layout.addWidget(self.track_name)
        v_left_layout.addLayout(track_name_layout)

        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS"))
        fps_layout.addWidget(self.fps_input)
        v_left_layout.addLayout(fps_layout)

        use_audio_layout = QHBoxLayout()
        use_audio_layout.addWidget(QLabel("Use Audio"))
        use_audio_layout.addStretch()
        use_audio_layout.addWidget(self.use_audio_checkbox)
        v_left_layout.addLayout(use_audio_layout)

        self.audio_file_row = QWidget()
        audio_file_layout = QHBoxLayout(self.audio_file_row)
        audio_file_layout.setContentsMargins(0, 0, 0, 0)
        audio_file_layout.addWidget(QLabel("Audio File"))
        audio_file_layout.addStretch()
        audio_file_layout.addWidget(self.audio_file_input)
        audio_file_layout.addWidget(self.audio_file_browse_btn)
        v_left_layout.addWidget(self.audio_file_row)

        v_left_layout.addWidget(SectionDivider("Background"))

        background_mode_layout = QHBoxLayout()
        background_mode_layout.addWidget(QLabel("Background Mode"))
        background_mode_layout.addWidget(self.bg_mode_combo)
        v_left_layout.addLayout(background_mode_layout)

        self.background_color_row = QWidget()
        background_color_layout = QHBoxLayout(self.background_color_row)
        background_color_layout.setContentsMargins(0, 0, 0, 0)
        background_color_layout.addWidget(QLabel("Background Color"))
        background_color_layout.addWidget(self.bg_button)
        v_left_layout.addWidget(self.background_color_row)

        self.background_image_row = QWidget()
        background_image_layout = QHBoxLayout(self.background_image_row)
        background_image_layout.setContentsMargins(0, 0, 0, 0)
        background_image_layout.addWidget(QLabel("Background Image File"))
        background_image_layout.addStretch()
        background_image_layout.addWidget(self.bg_image_file_input)
        background_image_layout.addWidget(self.bg_image_file_browse_btn)
        v_left_layout.addWidget(self.background_image_row)

        self.background_video_row = QWidget()
        background_video_layout = QHBoxLayout(self.background_video_row)
        background_video_layout.setContentsMargins(0, 0, 0, 0)
        background_video_layout.addWidget(QLabel("Background Video File"))
        background_video_layout.addStretch()
        background_video_layout.addWidget(self.bg_video_file_input)
        background_video_layout.addWidget(self.bg_video_file_browse_btn)
        v_left_layout.addWidget(self.background_video_row)

        v_left_layout.addWidget(SectionDivider("Playhead"))

        show_playhead_layout = QHBoxLayout()
        show_playhead_layout.addWidget(QLabel("Show Playhead"))
        show_playhead_layout.addStretch()
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

        v_left_layout.addWidget(SectionDivider("Position"))

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

        v_right_layout.addWidget(SectionDivider("Note Style"))

        note_fadeout_layout = QHBoxLayout()
        note_fadeout_layout.addWidget(QLabel("Note Fadeout"))
        note_fadeout_layout.addWidget(self.note_fadeout_input)
        v_right_layout.addLayout(note_fadeout_layout)

        note_play_color_layout = QHBoxLayout()
        note_play_color_layout.addWidget(QLabel("Note Play Color"))
        note_play_color_layout.addWidget(self.note_play_color_button)
        v_right_layout.addLayout(note_play_color_layout)

        v_right_layout.addWidget(SectionDivider("Pitch Settings"))

        auto_calc_pitch_bounds_layout = QHBoxLayout()
        auto_calc_pitch_bounds_layout.addWidget(QLabel("Auto-Calc Pitch Min/Max"))
        auto_calc_pitch_bounds_layout.addStretch()
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

        v_right_layout.addWidget(SectionDivider("Time Offsets"))

        apply_time_offsets_layout = QHBoxLayout()
        apply_time_offsets_layout.addWidget(QLabel("Apply Time Offsets"))
        apply_time_offsets_layout.addStretch()
        apply_time_offsets_layout.addWidget(self.apply_time_offsets_checkbox)
        v_right_layout.addLayout(apply_time_offsets_layout)

        start_time_layout = QHBoxLayout()
        start_time_layout.addWidget(QLabel("Start Time Offset"))
        start_time_layout.addWidget(self.start_time_input)
        v_right_layout.addLayout(start_time_layout)

        end_time_layout = QHBoxLayout()
        end_time_layout.addWidget(QLabel("End Time Offset"))
        end_time_layout.addWidget(self.end_time_input)
        v_right_layout.addLayout(end_time_layout)

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

        index = self.bg_mode_combo.findData(self.vis_config.bg_mode)
        self.bg_mode_combo.setCurrentIndex(index)

        self.background_color_row.setVisible(self.vis_config.bg_mode == BackgroundMode.Color)
        self.background_image_row.setVisible(self.vis_config.bg_mode == BackgroundMode.Image)
        self.background_video_row.setVisible(self.vis_config.bg_mode == BackgroundMode.Video)

        self.bg_button.setColor(self.vis_config.bg_color)
        self.bg_image_file_input.setText(self.vis_config.bg_image_filepath)
        self.bg_video_file_input.setText(self.vis_config.bg_video_filepath)

        self.use_audio_checkbox.setChecked(self.vis_config.play_audio)
        self.audio_file_input.setText(self.vis_config.audio_filepath)
        self.audio_file_row.setVisible(self.vis_config.play_audio)

        self.show_playhead_checkbox.setChecked(self.vis_config.show_playhead)
        self.playhead_color_button.setColor(self.vis_config.playhead_color)
        self.playhead_pos_input.setValue(self.vis_config.playhead_pos_ratio)

        self.vertical_padding_input.setValue(self.vis_config.vertical_padding_ratio)
        self.vertical_offset_input.setValue(self.vis_config.vertical_offset_ratio)

        self.note_fadeout_input.setValue(self.vis_config.note_fadeout_ratio)
        self.note_play_color_button.setColor(self.vis_config.note_play_color)

        self.auto_calc_pitch_bounds_checkbox.setChecked(self.vis_config.auto_calc_pitch_bounds)

        self.pitch_min_input.setDisabled(self.vis_config.auto_calc_pitch_bounds)
        self.pitch_min_input.setRange(0, self.vis_config.manual_pitch_max)
        self.pitch_min_input.setValue(self.vis_config.get_min_pitch() if self.vis_config.auto_calc_pitch_bounds else self.vis_config.manual_pitch_min)

        self.pitch_max_input.setDisabled(self.vis_config.auto_calc_pitch_bounds)
        self.pitch_max_input.setRange(self.vis_config.manual_pitch_min, 127)
        self.pitch_max_input.setValue(self.vis_config.get_max_pitch() if self.vis_config.auto_calc_pitch_bounds else self.vis_config.manual_pitch_max)  

        self.apply_time_offsets_checkbox.setChecked(self.vis_config.apply_time_offsets)

        self.start_time_input.setDisabled(not self.vis_config.apply_time_offsets)
        self.start_time_input.setValue(self.vis_config.start_time_offset)

        self.end_time_input.setDisabled(not self.vis_config.apply_time_offsets)
        self.end_time_input.setValue(self.vis_config.end_time_offset)  

        self.block_changes_callback = False

    def update_model(self):
        # pull UI values out of controls and set on model
        self.vis_config.track_name = self.track_name.text()
        self.vis_config.fps = self.fps_input.value()

        self.vis_config.bg_mode = self.bg_mode_combo.currentData()
        self.vis_config.bg_color = self.bg_button.getColor()
        self.vis_config.bg_image_filepath = self.bg_image_file_input.text()
        self.vis_config.bg_video_filepath = self.bg_video_file_input.text()

        self.vis_config.play_audio = self.use_audio_checkbox.isChecked()
        self.vis_config.audio_filepath = self.audio_file_input.text()

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

        self.vis_config.apply_time_offsets = self.apply_time_offsets_checkbox.isChecked()
        self.vis_config.start_time_offset = self.start_time_input.value()
        self.vis_config.end_time_offset = self.end_time_input.value()
        

    # callbacks

    def _browse_bg_image_file(self):
        default_filepath = self.vis_config.bg_image_filepath or ""

        image_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Background Image File",
            default_filepath,
            "Image Files (*.png *.jpg *.jpeg *.bmp *.webp)"
        )

        if image_file:
            self._on_changes()


    def _browse_bg_video_file(self):
        default_filepath = self.vis_config.bg_video_filepath or ""

        video_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Background Video File",
            default_filepath,
            "Video Files (*.mp4 *.mov *.webm *.avi)"
        )

        if video_file:
            self._on_changes()

    def _browse_audio_file(self):
        default_filepath = self.vis_config.audio_filepath or ""

        audio_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            default_filepath,
            "Audio Files (*.wav *.mp3 *.aiff *.aif *.flac *.m4a *.ogg)"
        )

        if audio_file:
            self._on_changes()

    def _on_changes(self):
        if not self.block_changes_callback:
            self.on_changes_callback()
