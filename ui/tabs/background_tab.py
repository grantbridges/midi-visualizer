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
    QComboBox,
    QFileDialog
)

from models import VisConfig, BackgroundMode
from ui.common import (
    ColorButton, 
    LayoutUtil, 
    Icons,
    ScaledSliderSpinbox,
    SliderDoubleSpinbox
)

class BackgroundTab(QWidget):
    def __init__(self, 
        vis_config: VisConfig, 
        on_changes_callback: object,
        on_bg_video_selected_callback: object,
        on_bg_image_selected_callback: object,
        parent=None
    ):
        super().__init__(parent)

        self.on_changes_callback = on_changes_callback
        self.on_bg_video_selected_callback = on_bg_video_selected_callback
        self.on_bg_image_selected_callback = on_bg_image_selected_callback
        self.vis_config = vis_config

        self.block_changes_callback: bool = False

        # create controls
        
        self.bg_mode_combo = QComboBox()
        for mode in BackgroundMode:
            self.bg_mode_combo.addItem(mode.value, mode)
        self.bg_mode_combo.currentIndexChanged.connect(self._on_changes)

        self.bg_color_button = ColorButton()
        self.bg_color_button.valueChanged.connect(self._on_changes)

        self.bg_image_file_input = QLineEdit(readOnly=True)
        self.bg_image_file_browse_btn = QPushButton()
        self.bg_image_file_browse_btn.setIcon(Icons.ellipsis())
        self.bg_image_file_browse_btn.clicked.connect(self._browse_bg_image_file)
        self.bg_image_file_clear_btn = QPushButton()
        self.bg_image_file_clear_btn.setIcon(Icons.trash_can())
        self.bg_image_file_clear_btn.clicked.connect(self._clear_bg_image_file)

        self.bg_video_file_input = QLineEdit(readOnly=True)
        self.bg_video_file_browse_btn = QPushButton()
        self.bg_video_file_browse_btn.setIcon(Icons.ellipsis())
        self.bg_video_file_browse_btn.clicked.connect(self._browse_bg_video_file)
        self.bg_video_file_clear_btn = QPushButton()
        self.bg_video_file_clear_btn.setIcon(Icons.trash_can())
        self.bg_video_file_clear_btn.clicked.connect(self._clear_bg_video_file)
        self.bg_video_time_offset_input = SliderDoubleSpinbox(decimals=2, minimum=-10.0, maximum=10.0, singleStep=0.01, suffix=" sec")
        self.bg_video_time_offset_input.valueChanged.connect(self._on_changes)
        self.bg_video_loop_checkbox = QCheckBox()
        self.bg_video_loop_checkbox.toggled.connect(self._on_changes)

        self.bg_tint_checkbox = QCheckBox()
        self.bg_tint_checkbox.toggled.connect(self._on_changes)
        self.bg_tint_color_button = ColorButton()
        self.bg_tint_color_button.valueChanged.connect(self._on_changes)
        self.bg_tint_opacity_input = ScaledSliderSpinbox(display_min=0, display_max=100, internal_min=0, internal_max=255)
        self.bg_tint_opacity_input.valueChanged.connect(self._on_changes)

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

        LayoutUtil.section(column, "Background")
        LayoutUtil.combobox(column, "Background Mode", self.bg_mode_combo)
        self.bg_color_row = LayoutUtil.button(column, "Background Color", self.bg_color_button)
        self.bg_image_row = LayoutUtil.file_picker(column, "Background Image File", self.bg_image_file_input, self.bg_image_file_browse_btn, self.bg_image_file_clear_btn)
        self.bg_video_row = LayoutUtil.file_picker(column, "Background Video File", self.bg_video_file_input, self.bg_video_file_browse_btn, self.bg_video_file_clear_btn)

        self.bg_video_time_offset_row = LayoutUtil.spinbox(column, "Background Video Time Delay", self.bg_video_time_offset_input)
        self.bg_video_loop_row = LayoutUtil.checkbox(column, "Background Video Loop", self.bg_video_loop_checkbox)

        LayoutUtil.section(column, "Background Tint")
        LayoutUtil.checkbox(column, "Background Tint", self.bg_tint_checkbox)
        LayoutUtil.button(column, "Background Tint Color", self.bg_tint_color_button)
        LayoutUtil.spinbox(column, "Background Tint Opacity", self.bg_tint_opacity_input)

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

        index = self.bg_mode_combo.findData(self.vis_config.bg_mode)
        self.bg_mode_combo.setCurrentIndex(index)

        self.bg_color_row.setVisible(self.vis_config.bg_mode == BackgroundMode.Color)
        self.bg_image_row.setVisible(self.vis_config.bg_mode == BackgroundMode.Image)
        self.bg_video_row.setVisible(self.vis_config.bg_mode == BackgroundMode.Video)
        self.bg_video_time_offset_row.setVisible(self.vis_config.bg_mode == BackgroundMode.Video)
        self.bg_video_loop_row.setVisible(self.vis_config.bg_mode == BackgroundMode.Video)

        self.bg_color_button.setColor(self.vis_config.bg_color)
        self.bg_image_file_input.setText(self.vis_config.bg_image_filepath)
        self.bg_image_file_clear_btn.setEnabled(bool(self.vis_config.bg_image_filepath))
        self.bg_video_file_input.setText(self.vis_config.bg_video_filepath)
        self.bg_video_file_clear_btn.setEnabled(bool(self.vis_config.bg_video_filepath))
        self.bg_video_time_offset_input.setValue(self.vis_config.bg_video_time_offset)
        self.bg_video_loop_checkbox.setChecked(self.vis_config.bg_video_loop)

        self.bg_tint_checkbox.setChecked(self.vis_config.bg_tint_enabled)
        self.bg_tint_color_button.setColor(self.vis_config.bg_tint_color)
        self.bg_tint_color_button.setEnabled(self.vis_config.bg_tint_enabled)
        self.bg_tint_opacity_input.setInternalValue(self.vis_config.bg_tint_alpha)
        self.bg_tint_opacity_input.setEnabled(self.vis_config.bg_tint_enabled)

        self.block_changes_callback = False

    def update_model(self):
        # pull UI values out of controls and set on model

        self.vis_config.bg_mode = self.bg_mode_combo.currentData()
        self.vis_config.bg_color = self.bg_color_button.getColor()
        self.vis_config.bg_image_filepath = self.bg_image_file_input.text()
        self.vis_config.bg_video_filepath = self.bg_video_file_input.text()

        self.vis_config.bg_video_time_offset = self.bg_video_time_offset_input.value()
        self.vis_config.bg_video_loop = self.bg_video_loop_checkbox.isChecked()

        self.vis_config.bg_tint_enabled = self.bg_tint_checkbox.isChecked()
        self.vis_config.bg_tint_color = self.bg_tint_color_button.getColor()
        self.vis_config.bg_tint_alpha = self.bg_tint_opacity_input.getInternalValue()

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

    def _clear_bg_image_file(self):
        result = QMessageBox.question(
            self,
            "Confirm Image File Remove",
            f"Are you sure you want to remove the selected background image file?",
            QMessageBox.Cancel | QMessageBox.Yes,
            QMessageBox.Cancel,
        )

        if result != QMessageBox.Yes:
            return

        self.bg_image_file_input.setText("")
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

    def _clear_bg_video_file(self):
        result = QMessageBox.question(
            self,
            "Confirm Video File Remove",
            f"Are you sure you want to remove the selected background video file?",
            QMessageBox.Cancel | QMessageBox.Yes,
            QMessageBox.Cancel,
        )

        if result != QMessageBox.Yes:
            return

        self.bg_video_file_input.setText("")
        self._on_bg_video_selected()

    def _on_changes(self):
        if not self.block_changes_callback:
            self.on_changes_callback()
            self.refresh_ui()

    def _on_bg_video_selected(self):
        if not self.block_changes_callback:
            self.on_changes_callback()
            self.on_bg_video_selected_callback()
            self.refresh_ui()

    def _on_bg_image_selected(self):
        if not self.block_changes_callback:
            self.on_changes_callback()
            self.on_bg_image_selected_callback()
            self.refresh_ui()
