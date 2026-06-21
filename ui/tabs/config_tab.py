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
from ui.common import ColorButton, LayoutUtil

class ConfigTab(QWidget):
    def __init__(self, 
        vis_config: VisConfig, 
        on_changes_callback: object,
        on_bg_video_selected_callback: object,
        on_bg_image_selected_callback: object,
        on_audio_selected_callback: object,
        parent=None
    ):
        super().__init__(parent)

        self.on_changes_callback = on_changes_callback
        self.on_bg_video_selected_callback = on_bg_video_selected_callback
        self.on_bg_image_selected_callback = on_bg_image_selected_callback
        self.on_audio_selected_callback = on_audio_selected_callback
        self.vis_config = vis_config

        self.block_changes_callback: bool = False

        # create controls
        self.track_name = QLineEdit()
        self.track_name.editingFinished.connect(self._on_changes)

        self.fps_input = QSpinBox(minimum=1, maximum=120)
        self.fps_input.valueChanged.connect(self._on_changes)

        self.bg_mode_combo = QComboBox()
        for mode in BackgroundMode:
            self.bg_mode_combo.addItem(mode.value, mode)
        self.bg_mode_combo.currentIndexChanged.connect(self._on_changes)

        self.bg_color_button = ColorButton()
        self.bg_color_button.valueChanged.connect(self._on_changes)

        self.bg_image_file_input = QLineEdit(readOnly=True)
        self.bg_image_file_browse_btn = QPushButton("...")
        self.bg_image_file_browse_btn.clicked.connect(self._browse_bg_image_file)

        self.bg_video_file_input = QLineEdit(readOnly=True)
        self.bg_video_file_browse_btn = QPushButton("...")
        self.bg_video_file_browse_btn.clicked.connect(self._browse_bg_video_file)
        self.bg_video_time_offset_input = QDoubleSpinBox(decimals=2, minimum=-10.0, maximum=10.0, singleStep=0.01, suffix=" sec")
        self.bg_video_time_offset_input.valueChanged.connect(self._on_changes)
        self.bg_video_loop_checkbox = QCheckBox()
        self.bg_video_loop_checkbox.toggled.connect(self._on_changes)

        self.bg_tint_checkbox = QCheckBox()
        self.bg_tint_checkbox.toggled.connect(self._on_changes)
        self.bg_tint_color_button = ColorButton()
        self.bg_tint_color_button.valueChanged.connect(self._on_changes)
        self.bg_tint_alpha_input = QSpinBox(minimum=0, maximum=255)
        self.bg_tint_alpha_input.valueChanged.connect(self._on_changes)

        self.use_audio_checkbox = QCheckBox()
        self.use_audio_checkbox.toggled.connect(self._on_changes)
        self.audio_file_input = QLineEdit(readOnly=True)
        self.audio_file_browse_btn = QPushButton("...")
        self.audio_file_browse_btn.clicked.connect(self._browse_audio_file)

        self.show_playhead_checkbox = QCheckBox()
        self.show_playhead_checkbox.toggled.connect(self._on_changes)
        self.playhead_color_button = ColorButton()
        self.playhead_color_button.valueChanged.connect(self._on_changes)
        self.playhead_alpha_input = QSpinBox(minimum=0, maximum=255)
        self.playhead_alpha_input.valueChanged.connect(self._on_changes)
        self.playhead_thickness_input = QDoubleSpinBox(decimals=4, minimum=0.0001, maximum=0.1, singleStep=0.001)
        self.playhead_thickness_input.valueChanged.connect(self._on_changes)
        self.playhead_pos_input = QDoubleSpinBox(decimals=2, minimum=0.00, maximum=1.00, singleStep=0.01)
        self.playhead_pos_input.valueChanged.connect(self._on_changes)

        self.vertical_padding_input = QDoubleSpinBox(decimals=2, minimum=0.00, maximum=1.00, singleStep=0.01)
        self.vertical_padding_input.valueChanged.connect(self._on_changes)
        self.vertical_offset_input = QDoubleSpinBox(decimals=2, minimum=-1.00, maximum=1.00, singleStep=0.01)
        self.vertical_offset_input.valueChanged.connect(self._on_changes)

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

        self.fade_in_checkbox = QCheckBox()
        self.fade_in_checkbox.toggled.connect(self._on_changes)
        self.fade_in_color = ColorButton()
        self.fade_in_color.valueChanged.connect(self._on_changes)
        self.fade_in_time = QDoubleSpinBox(decimals=2, minimum=0.1, maximum=10.00, singleStep=0.1, suffix=" sec")
        self.fade_in_time.valueChanged.connect(self._on_changes)
        self.fade_out_checkbox = QCheckBox()
        self.fade_out_checkbox.toggled.connect(self._on_changes)
        self.fade_out_color = ColorButton()
        self.fade_out_color.valueChanged.connect(self._on_changes)
        self.fade_out_time = QDoubleSpinBox(decimals=2, minimum=0.1, maximum=10.00, singleStep=0.1, suffix=" sec")
        self.fade_out_time.valueChanged.connect(self._on_changes)

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

        root_h_layout = QHBoxLayout()
        v_left_layout = QVBoxLayout()
        v_right_layout = QVBoxLayout()
        v_left_layout.setSpacing(2)
        v_right_layout.setSpacing(2)

        # --- Left Column ---
        column = v_left_layout

        LayoutUtil.section(column, "Track Props")
        LayoutUtil.line_edit(column, "Track Name", self.track_name)
        LayoutUtil.spinbox(column, "FPS", self.fps_input)
        LayoutUtil.checkbox(column, "Use Audio", self.use_audio_checkbox)
        self.audio_file_row = LayoutUtil.file_picker(column, "Audio File", self.audio_file_input, self.audio_file_browse_btn)

        LayoutUtil.section(column, "Background")
        LayoutUtil.combobox(column, "Background Mode", self.bg_mode_combo)
        self.bg_color_row = LayoutUtil.button(column, "Background Color", self.bg_color_button)
        self.bg_image_row = LayoutUtil.file_picker(column, "Background Image File", self.bg_image_file_input, self.bg_image_file_browse_btn)
        self.bg_video_row = LayoutUtil.file_picker(column, "Background Video File", self.bg_video_file_input, self.bg_video_file_browse_btn)

        self.bg_video_time_offset_row = LayoutUtil.spinbox(column, "Background Video Time Offset", self.bg_video_time_offset_input)
        self.bg_video_loop_row = LayoutUtil.checkbox(column, "Background Video Loop", self.bg_video_loop_checkbox)

        LayoutUtil.section(column, "Background Tint")
        LayoutUtil.checkbox(column, "Background Tint", self.bg_tint_checkbox)
        LayoutUtil.button(column, "Background Tint Color", self.bg_tint_color_button)
        LayoutUtil.spinbox(column, "Background Tint Alpha", self.bg_tint_alpha_input)

        LayoutUtil.section(column, "Fade In/Out")
        LayoutUtil.checkbox(column, "Fade In", self.fade_in_checkbox)
        LayoutUtil.button(column, "Fade In Color", self.fade_in_color)
        LayoutUtil.spinbox(column, "Fade In Time", self.fade_in_time)
        LayoutUtil.checkbox(column, "Fade Out", self.fade_out_checkbox)
        LayoutUtil.button(column, "Fade Out Color", self.fade_out_color)
        LayoutUtil.spinbox(column, "Fade Out Time", self.fade_out_time)

        column.addStretch()

        # --- Right Column ---
        column = v_right_layout

        LayoutUtil.section(column, "Scaling/Position")
        LayoutUtil.spinbox(column, "Vertical Padding", self.vertical_padding_input)
        LayoutUtil.spinbox(column, "Vertical Offset", self.vertical_offset_input)

        LayoutUtil.section(column, "Pitch Settings")
        LayoutUtil.checkbox(column, "Auto-Calc Pitch Min/Max", self.auto_calc_pitch_bounds_checkbox)
        LayoutUtil.spinbox(column, "Pitch Min", self.pitch_min_input)
        LayoutUtil.spinbox(column, "Pitch Max", self.pitch_max_input)

        LayoutUtil.section(column, "Time Offsets")
        LayoutUtil.checkbox(column, "Apply Time Offsets", self.apply_time_offsets_checkbox)
        LayoutUtil.spinbox(column, "Start Time Offset", self.start_time_input)
        LayoutUtil.spinbox(column, "End Time Offset", self.end_time_input)

        LayoutUtil.section(column, "Playhead")
        LayoutUtil.checkbox(column, "Show Playhead", self.show_playhead_checkbox)
        LayoutUtil.button(column, "Playhead Color", self.playhead_color_button)
        LayoutUtil.spinbox(column, "Playhead Alpha", self.playhead_alpha_input)
        LayoutUtil.spinbox(column, "Playhead Thickness", self.playhead_thickness_input)
        LayoutUtil.spinbox(column, "Playhead Position", self.playhead_pos_input)

        column.addStretch()

        root_h_layout.addLayout(v_left_layout, 1)
        root_h_layout.addLayout(v_right_layout, 1)

        content_layout.addLayout(root_h_layout)
        
        scroll_area.setWidget(content)

        root.addWidget(scroll_area)

    def refresh_ui(self):
        self.block_changes_callback = True # prevent "change" callbacks from triggering while we set values

        self.track_name.setText(self.vis_config.track_name)
        self.fps_input.setValue(self.vis_config.fps)

        index = self.bg_mode_combo.findData(self.vis_config.bg_mode)
        self.bg_mode_combo.setCurrentIndex(index)

        self.bg_color_row.setVisible(self.vis_config.bg_mode == BackgroundMode.Color)
        self.bg_image_row.setVisible(self.vis_config.bg_mode == BackgroundMode.Image)
        self.bg_video_row.setVisible(self.vis_config.bg_mode == BackgroundMode.Video)
        self.bg_video_time_offset_row.setVisible(self.vis_config.bg_mode == BackgroundMode.Video)
        self.bg_video_loop_row.setVisible(self.vis_config.bg_mode == BackgroundMode.Video)

        self.bg_color_button.setColor(self.vis_config.bg_color)
        self.bg_image_file_input.setText(self.vis_config.bg_image_filepath)
        self.bg_video_file_input.setText(self.vis_config.bg_video_filepath)
        self.bg_video_time_offset_input.setValue(self.vis_config.bg_video_time_offset)
        self.bg_video_loop_checkbox.setChecked(self.vis_config.bg_video_loop)

        self.bg_tint_checkbox.setChecked(self.vis_config.bg_tint_enabled)
        self.bg_tint_color_button.setColor(self.vis_config.bg_tint_color)
        self.bg_tint_color_button.setDisabled(not self.vis_config.bg_tint_enabled)
        self.bg_tint_alpha_input.setValue(self.vis_config.bg_tint_alpha)
        self.bg_tint_alpha_input.setDisabled(not self.vis_config.bg_tint_enabled)

        self.use_audio_checkbox.setChecked(self.vis_config.play_audio)
        self.audio_file_input.setText(self.vis_config.audio_filepath)
        self.audio_file_row.setVisible(self.vis_config.play_audio)

        self.show_playhead_checkbox.setChecked(self.vis_config.show_playhead)
        self.playhead_color_button.setColor(self.vis_config.playhead_color)
        self.playhead_color_button.setDisabled(not self.vis_config.show_playhead)
        self.playhead_alpha_input.setValue(self.vis_config.playhead_alpha)
        self.playhead_alpha_input.setDisabled(not self.vis_config.show_playhead)
        self.playhead_thickness_input.setValue(self.vis_config.playhead_thickness_ratio)
        self.playhead_thickness_input.setDisabled(not self.vis_config.show_playhead)
        self.playhead_pos_input.setValue(self.vis_config.playhead_pos_ratio)
        self.playhead_pos_input.setDisabled(not self.vis_config.show_playhead)

        self.vertical_padding_input.setValue(self.vis_config.vertical_padding_ratio)
        self.vertical_offset_input.setValue(self.vis_config.vertical_offset_ratio)

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

        self.fade_in_checkbox.setChecked(self.vis_config.fade_in_enabled)
        self.fade_in_color.setColor(self.vis_config.fade_in_color)
        self.fade_in_color.setDisabled(not self.vis_config.fade_in_enabled)
        self.fade_in_time.setValue(self.vis_config.fade_in_time)
        self.fade_in_time.setDisabled(not self.vis_config.fade_in_enabled)

        self.fade_out_checkbox.setChecked(self.vis_config.fade_out_enabled)
        self.fade_out_color.setColor(self.vis_config.fade_out_color)
        self.fade_out_color.setDisabled(not self.vis_config.fade_out_enabled)
        self.fade_out_time.setValue(self.vis_config.fade_out_time)
        self.fade_out_time.setDisabled(not self.vis_config.fade_out_enabled)

        self.block_changes_callback = False

    def update_model(self):
        # pull UI values out of controls and set on model
        self.vis_config.track_name = self.track_name.text()
        self.vis_config.fps = self.fps_input.value()

        self.vis_config.bg_mode = self.bg_mode_combo.currentData()
        self.vis_config.bg_color = self.bg_color_button.getColor()
        self.vis_config.bg_image_filepath = self.bg_image_file_input.text()
        self.vis_config.bg_video_filepath = self.bg_video_file_input.text()

        self.vis_config.bg_video_time_offset = self.bg_video_time_offset_input.value()
        self.vis_config.bg_video_loop = self.bg_video_loop_checkbox.isChecked()

        self.vis_config.bg_tint_enabled = self.bg_tint_checkbox.isChecked()
        self.vis_config.bg_tint_color = self.bg_tint_color_button.getColor()
        self.vis_config.bg_tint_alpha = self.bg_tint_alpha_input.value()

        self.vis_config.play_audio = self.use_audio_checkbox.isChecked()
        self.vis_config.audio_filepath = self.audio_file_input.text()

        self.vis_config.show_playhead = self.show_playhead_checkbox.isChecked()
        self.vis_config.playhead_color = self.playhead_color_button.getColor()
        self.vis_config.playhead_alpha = self.playhead_alpha_input.value()
        self.vis_config.playhead_thickness_ratio = self.playhead_thickness_input.value()
        self.vis_config.playhead_pos_ratio = self.playhead_pos_input.value()

        self.vis_config.vertical_padding_ratio = self.vertical_padding_input.value()
        self.vis_config.vertical_offset_ratio = self.vertical_offset_input.value()

        if not self.vis_config.auto_calc_pitch_bounds:
            self.vis_config.manual_pitch_min = self.pitch_min_input.value()
            self.vis_config.manual_pitch_max = self.pitch_max_input.value()
        
        self.vis_config.auto_calc_pitch_bounds = self.auto_calc_pitch_bounds_checkbox.isChecked()

        self.vis_config.apply_time_offsets = self.apply_time_offsets_checkbox.isChecked()
        self.vis_config.start_time_offset = self.start_time_input.value()
        self.vis_config.end_time_offset = self.end_time_input.value()

        self.vis_config.fade_in_enabled = self.fade_in_checkbox.isChecked()
        self.vis_config.fade_in_color = self.fade_in_color.getColor()
        self.vis_config.fade_in_time = self.fade_in_time.value()
        self.vis_config.fade_out_enabled = self.fade_out_checkbox.isChecked()
        self.vis_config.fade_out_color = self.fade_out_color.getColor()
        self.vis_config.fade_out_time = self.fade_out_time.value()

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
            self.bg_image_file_input.setText(image_file)
            self._on_bg_image_selected()


    def _browse_bg_video_file(self):
        default_filepath = self.vis_config.bg_video_filepath or ""

        video_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Background Video File",
            default_filepath,
            "Video Files (*.mp4 *.mov *.webm *.avi)"
        )

        if video_file:
            self.bg_video_file_input.setText(video_file)
            self._on_bg_video_selected()

    def _browse_audio_file(self):
        default_filepath = self.vis_config.audio_filepath or ""

        audio_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            default_filepath,
            "Audio Files (*.wav *.mp3 *.aiff *.aif *.flac *.m4a *.ogg)"
        )

        if audio_file:
            self.audio_file_input.setText(audio_file)
            self._on_audio_selected()

    def _on_changes(self):
        if not self.block_changes_callback:
            self.on_changes_callback()
            self.refresh_ui()

    def _on_bg_video_selected(self):
        if not self.block_changes_callback:
            self.on_bg_video_selected_callback()
            self.on_changes_callback()
            self.refresh_ui()

    def _on_bg_image_selected(self):
        if not self.block_changes_callback:
            self.on_bg_image_selected_callback()
            self.on_changes_callback()
            self.refresh_ui()

    def _on_audio_selected(self):
        if not self.block_changes_callback:
            self.on_audio_selected_callback()
            self.on_changes_callback()
            self.refresh_ui()
