from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMessageBox,
    QScrollArea,
    QCheckBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog
)

from models import VisConfig
from ui.common import (
    ColorButton, 
    LayoutUtil, 
    Icons, 
    SliderDoubleSpinbox,
    ScaledSliderSpinbox, 
    ScaledSliderDoubleSpinbox
)

class AudioTab(QWidget):
    def __init__(self, 
        vis_config: VisConfig, 
        on_changes_callback: object,
        on_audio_selected_callback: object,
        parent=None
    ):
        super().__init__(parent)

        self.on_changes_callback = on_changes_callback
        self.on_audio_selected_callback = on_audio_selected_callback
        self.vis_config = vis_config

        self.block_changes_callback: bool = False

        # create controls
        self.use_audio_checkbox = QCheckBox()
        self.use_audio_checkbox.toggled.connect(self._on_changes)
        self.audio_file_input = QLineEdit(readOnly=True)
        self.audio_file_browse_btn = QPushButton()
        self.audio_file_browse_btn.setIcon(Icons.ellipsis())
        self.audio_file_browse_btn.clicked.connect(self._browse_audio_file)
        self.audio_file_clear_btn = QPushButton()
        self.audio_file_clear_btn.setIcon(Icons.trash_can())
        self.audio_file_clear_btn.clicked.connect(self._clear_audio_file)
        self.audio_offset_input = SliderDoubleSpinbox(decimals=2, minimum=-5.0, maximum=5.0, singleStep=0.01, suffix=" sec")
        self.audio_offset_input.valueChanged.connect(self._on_changes)

        self.show_waveform_checkbox = QCheckBox()
        self.show_waveform_checkbox.toggled.connect(self._on_changes)
        self.waveform_color_button = ColorButton()
        self.waveform_color_button.valueChanged.connect(self._on_changes)
        self.waveform_opacity_input = ScaledSliderSpinbox(display_min=0, display_max=100, internal_min=0, internal_max=255)
        self.waveform_opacity_input.valueChanged.connect(self._on_changes)
        self.waveform_speed_input = ScaledSliderDoubleSpinbox(decimals=2, singleStep=0.01, display_min=0.1, display_max=10.0, internal_min=20.0, internal_max=0.1)
        self.waveform_speed_input.valueChanged.connect(self._on_changes)
        self.waveform_height_input = SliderDoubleSpinbox(decimals=2, minimum=0.01, maximum=1.0, singleStep=0.01)
        self.waveform_height_input.valueChanged.connect(self._on_changes)
        self.waveform_pos_input = SliderDoubleSpinbox(decimals=2, minimum=0.00, maximum=1.0, singleStep=0.01)
        self.waveform_pos_input.valueChanged.connect(self._on_changes)

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

        LayoutUtil.section(column, "Audio")
        LayoutUtil.checkbox(column, "Use Audio", self.use_audio_checkbox)
        LayoutUtil.file_picker(column, "Audio File", self.audio_file_input, self.audio_file_browse_btn, self.audio_file_clear_btn)
        LayoutUtil.spinbox(column, "Audio Time Delay", self.audio_offset_input)

        LayoutUtil.section(column, "Waveform")
        LayoutUtil.checkbox(column, "Show Waveform", self.show_waveform_checkbox)
        LayoutUtil.button(column, "Waveform Color", self.waveform_color_button)
        LayoutUtil.spinbox(column, "Waveform Opacity", self.waveform_opacity_input)
        LayoutUtil.spinbox(column, "Waveform Speed", self.waveform_speed_input)
        LayoutUtil.spinbox(column, "Waveform Size", self.waveform_height_input)
        LayoutUtil.spinbox(column, "Waveform Position", self.waveform_pos_input)

        column.addStretch()

        # --- Right Column ---
        column = v_right_layout

        # contents here...

        column.addStretch()

        root_h_layout.addLayout(v_left_layout, 1)
        root_h_layout.addSpacing(10)
        root_h_layout.addLayout(v_right_layout, 1)

        content_layout.addLayout(root_h_layout)
        
        scroll_area.setWidget(content)

        root.addWidget(scroll_area)

    def refresh_ui(self):
        self.block_changes_callback = True # prevent "change" callbacks from triggering while we set values

        self.use_audio_checkbox.setChecked(self.vis_config.play_audio)
        self.audio_file_input.setText(self.vis_config.audio_filepath)
        self.audio_file_input.setEnabled(self.vis_config.play_audio)
        self.audio_file_browse_btn.setEnabled(self.vis_config.play_audio)
        self.audio_file_clear_btn.setEnabled(self.vis_config.play_audio and bool(self.vis_config.audio_filepath))
        self.audio_offset_input.setValue(self.vis_config.audio_time_offset)
        self.audio_offset_input.setEnabled(self.vis_config.play_audio)

        self.show_waveform_checkbox.setChecked(self.vis_config.show_waveform)
        self.show_waveform_checkbox.setEnabled(self.vis_config.has_audio())
        self.waveform_color_button.setColor(self.vis_config.waveform_color)
        self.waveform_color_button.setEnabled(self.vis_config.show_waveform and self.vis_config.has_audio())
        self.waveform_opacity_input.setInternalValue(self.vis_config.waveform_alpha)
        self.waveform_opacity_input.setEnabled(self.vis_config.show_waveform and self.vis_config.has_audio())
        self.waveform_speed_input.setInternalValue(self.vis_config.waveform_sec_across_screen)
        self.waveform_speed_input.setEnabled(self.vis_config.show_waveform and self.vis_config.has_audio())
        self.waveform_height_input.setValue(self.vis_config.waveform_height_ratio)
        self.waveform_height_input.setEnabled(self.vis_config.show_waveform and self.vis_config.has_audio())
        self.waveform_pos_input.setValue(self.vis_config.waveform_pos_ratio)
        self.waveform_pos_input.setEnabled(self.vis_config.show_waveform and self.vis_config.has_audio())

        self.block_changes_callback = False

    def update_model(self):
        # pull UI values out of controls and set on model
        self.vis_config.play_audio = self.use_audio_checkbox.isChecked()
        self.vis_config.audio_filepath = self.audio_file_input.text()
        self.vis_config.audio_time_offset = self.audio_offset_input.value()

        self.vis_config.show_waveform = self.show_waveform_checkbox.isChecked()
        self.vis_config.waveform_color = self.waveform_color_button.getColor()
        self.vis_config.waveform_alpha = self.waveform_opacity_input.getInternalValue()
        self.vis_config.waveform_sec_across_screen = self.waveform_speed_input.getInternalValue()
        self.vis_config.waveform_height_ratio = self.waveform_height_input.value()
        self.vis_config.waveform_pos_ratio = self.waveform_pos_input.value()

    # callbacks

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

    def _clear_audio_file(self):
        result = QMessageBox.question(
            self,
            "Confirm Audio File Remove",
            f"Are you sure you want to remove the selected audio file?",
            QMessageBox.Cancel | QMessageBox.Yes,
            QMessageBox.Cancel,
        )

        if result != QMessageBox.Yes:
            return
        
        self.audio_file_input.setText("")
        self._on_audio_selected()

    def _on_changes(self):
        if not self.block_changes_callback:
            self.on_changes_callback()
            self.refresh_ui()

    def _on_audio_selected(self):
        if not self.block_changes_callback:
            self.on_changes_callback()
            self.on_audio_selected_callback()
            self.refresh_ui()
