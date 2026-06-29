from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QScrollArea,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

from models import VisConfig
from ui.common import LayoutUtil

class NotesTab(QWidget):
    def __init__(self, 
        vis_config: VisConfig, 
        on_changes_callback: object,
        parent=None
    ):
        super().__init__(parent)

        self.on_changes_callback = on_changes_callback
        self.vis_config = vis_config

        self.block_changes_callback: bool = False

        # create controls
        self.note_fadeout_checkbox = QCheckBox()
        self.note_fadeout_checkbox.toggled.connect(self._on_changes)
        self.note_fadeout_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.00, singleStep=.01)
        self.note_fadeout_input.valueChanged.connect(self._on_changes)

        self.note_glow_checkbox = QCheckBox()
        self.note_glow_checkbox.toggled.connect(self._on_changes)
        self.note_glow_size_input = QDoubleSpinBox(decimals=2, minimum=0.00, maximum=2.0, singleStep=0.01)
        self.note_glow_size_input.valueChanged.connect(self._on_changes)
        self.note_glow_intensity_input = QDoubleSpinBox(decimals=2, minimum=0.00, maximum=1.00, singleStep=0.01)
        self.note_glow_intensity_input.valueChanged.connect(self._on_changes)

        self.note_highlight_checkbox = QCheckBox()
        self.note_highlight_checkbox.toggled.connect(self._on_changes)
        self.note_highlight_use_vel_checkbox = QCheckBox()
        self.note_highlight_use_vel_checkbox.toggled.connect(self._on_changes)
        self.note_highlight_intensity_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.00, singleStep=0.01)
        self.note_highlight_intensity_input.valueChanged.connect(self._on_changes)
        self.note_highlight_min_intensity_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.00, singleStep=0.01)
        self.note_highlight_min_intensity_input.valueChanged.connect(self._on_changes)
        self.note_highlight_max_intensity_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.00, singleStep=0.01)
        self.note_highlight_max_intensity_input.valueChanged.connect(self._on_changes)

        self.note_sparks_checkbox = QCheckBox()
        self.note_sparks_checkbox.toggled.connect(self._on_changes)
        self.note_sparks_start_dist_input = QDoubleSpinBox(decimals=1, minimum=0.0, maximum=10.0, singleStep=0.1)
        self.note_sparks_start_dist_input.valueChanged.connect(self._on_changes)
        self.note_sparks_start_length_input = QDoubleSpinBox(decimals=2, minimum=0.25, maximum=10.0, singleStep=0.01)
        self.note_sparks_start_length_input.valueChanged.connect(self._on_changes)
        self.note_sparks_speed_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=5.0, singleStep=0.01)
        self.note_sparks_speed_input.valueChanged.connect(self._on_changes)
        self.note_sparks_speed_var_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=5.0, singleStep=0.01)
        self.note_sparks_speed_var_input.valueChanged.connect(self._on_changes)
        self.note_sparks_alpha_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.0, singleStep=0.01)
        self.note_sparks_alpha_input.valueChanged.connect(self._on_changes)
        self.note_sparks_count_input = QSpinBox(minimum=1, maximum=50)
        self.note_sparks_count_input.valueChanged.connect(self._on_changes)
        self.note_sparks_angle_input = QSpinBox(minimum=0, maximum=180, suffix="°")
        self.note_sparks_angle_input.valueChanged.connect(self._on_changes)
        self.note_sparks_fade_time_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=5.0, singleStep=0.01, suffix=" sec")
        self.note_sparks_fade_time_input.valueChanged.connect(self._on_changes)

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

        LayoutUtil.section(column, "Fade")
        LayoutUtil.checkbox(column, "Fade Enabled", self.note_fadeout_checkbox)
        LayoutUtil.spinbox(column, "Fade Distance", self.note_fadeout_input)

        LayoutUtil.section(column, "Highlight & Glow")
        LayoutUtil.checkbox(column, "Highlight Enabled", self.note_highlight_checkbox)
        LayoutUtil.checkbox(column, "Highlight Use Velocity", self.note_highlight_use_vel_checkbox)
        LayoutUtil.spinbox(column, "Highlight Intensity", self.note_highlight_intensity_input)
        LayoutUtil.spinbox(column, "Highlight Min Intensity", self.note_highlight_min_intensity_input)
        LayoutUtil.spinbox(column, "Highlight Max Intensity", self.note_highlight_max_intensity_input)
        LayoutUtil.checkbox(column, "Glow Enabled", self.note_glow_checkbox)
        LayoutUtil.spinbox(column, "Glow Size", self.note_glow_size_input)
        LayoutUtil.spinbox(column, "Glow Intensity", self.note_glow_intensity_input)

        column.addStretch()

        # --- Right Column ---
        column = v_right_layout

        LayoutUtil.section(column, "Sparks")
        LayoutUtil.checkbox(column, "Sparks Enabled", self.note_sparks_checkbox)
        LayoutUtil.spinbox(column, "Start Distance", self.note_sparks_start_dist_input)
        LayoutUtil.spinbox(column, "Size", self.note_sparks_start_length_input)
        LayoutUtil.spinbox(column, "Speed Min", self.note_sparks_speed_input)
        LayoutUtil.spinbox(column, "Speed Max", self.note_sparks_speed_var_input)
        LayoutUtil.spinbox(column, "Alpha Ratio", self.note_sparks_alpha_input)
        LayoutUtil.spinbox(column, "Particle Count", self.note_sparks_count_input)
        LayoutUtil.spinbox(column, "Angle", self.note_sparks_angle_input)
        LayoutUtil.spinbox(column, "Fade Time", self.note_sparks_fade_time_input)

        column.addStretch()

        root_h_layout.addLayout(v_left_layout, 1)
        root_h_layout.addLayout(v_right_layout, 1)

        content_layout.addLayout(root_h_layout)
        
        scroll_area.setWidget(content)

        root.addWidget(scroll_area)

    def refresh_ui(self):
        self.block_changes_callback = True # prevent "change" callbacks from triggering while we set values

        self.note_fadeout_checkbox.setChecked(self.vis_config.note_fadeout_enabled)
        self.note_fadeout_input.setValue(self.vis_config.note_fadeout_ratio)
        self.note_fadeout_input.setDisabled(not self.vis_config.note_fadeout_enabled)

        self.note_glow_checkbox.setChecked(self.vis_config.note_glow_enabled)
        self.note_glow_size_input.setValue(self.vis_config.note_glow_size)
        self.note_glow_size_input.setDisabled(not self.vis_config.note_glow_enabled)
        self.note_glow_intensity_input.setValue(self.vis_config.note_glow_intensity)
        self.note_glow_intensity_input.setDisabled(not self.vis_config.note_glow_enabled)

        self.note_highlight_checkbox.setChecked(self.vis_config.note_highlight_enabled)
        self.note_highlight_use_vel_checkbox.setChecked(self.vis_config.note_highlight_use_velocity)
        self.note_highlight_use_vel_checkbox.setDisabled(not self.vis_config.note_highlight_enabled)
        self.note_highlight_intensity_input.setValue(self.vis_config.note_highlight_intensity)
        self.note_highlight_intensity_input.setDisabled(not self.vis_config.note_highlight_enabled or self.vis_config.note_highlight_use_velocity)
        self.note_highlight_min_intensity_input.setValue(self.vis_config.note_highlight_min_intensity)
        self.note_highlight_min_intensity_input.setDisabled(not self.vis_config.note_highlight_enabled or not self.vis_config.note_highlight_use_velocity)
        self.note_highlight_min_intensity_input.setMaximum(self.vis_config.note_highlight_max_intensity - .01)
        self.note_highlight_max_intensity_input.setValue(self.vis_config.note_highlight_max_intensity)
        self.note_highlight_max_intensity_input.setDisabled(not self.vis_config.note_highlight_enabled or not self.vis_config.note_highlight_use_velocity)
        self.note_highlight_max_intensity_input.setMinimum(self.vis_config.note_highlight_min_intensity + .01)

        self.note_sparks_checkbox.setChecked(self.vis_config.note_sparks_enabled)
        self.note_sparks_start_dist_input.setValue(self.vis_config.note_sparks_start_dist_ratio)
        self.note_sparks_start_dist_input.setDisabled(not self.vis_config.note_sparks_enabled)
        self.note_sparks_start_length_input.setValue(self.vis_config.note_sparks_start_length_ratio)
        self.note_sparks_start_length_input.setDisabled(not self.vis_config.note_sparks_enabled)
        self.note_sparks_speed_input.setValue(self.vis_config.note_sparks_speed_ratio)
        self.note_sparks_speed_input.setDisabled(not self.vis_config.note_sparks_enabled)
        self.note_sparks_speed_var_input.setValue(self.vis_config.note_sparks_speed_var_ratio)
        self.note_sparks_speed_var_input.setDisabled(not self.vis_config.note_sparks_enabled)
        self.note_sparks_alpha_input.setValue(self.vis_config.note_sparks_alpha_ratio)
        self.note_sparks_alpha_input.setDisabled(not self.vis_config.note_sparks_enabled)
        self.note_sparks_count_input.setValue(self.vis_config.note_sparks_count)
        self.note_sparks_count_input.setDisabled(not self.vis_config.note_sparks_enabled)
        self.note_sparks_angle_input.setValue(self.vis_config.note_sparks_max_angle_deg)
        self.note_sparks_angle_input.setDisabled(not self.vis_config.note_sparks_enabled)
        self.note_sparks_fade_time_input.setValue(self.vis_config.note_sparks_time_to_fade_sec)
        self.note_sparks_fade_time_input.setDisabled(not self.vis_config.note_sparks_enabled)

        self.block_changes_callback = False

    def update_model(self):
        # pull UI values out of controls and set on model
        
        self.vis_config.note_fadeout_enabled = self.note_fadeout_checkbox.isChecked()
        self.vis_config.note_fadeout_ratio = self.note_fadeout_input.value()

        self.vis_config.note_glow_enabled = self.note_glow_checkbox.isChecked()
        self.vis_config.note_glow_size = self.note_glow_size_input.value()
        self.vis_config.note_glow_intensity = self.note_glow_intensity_input.value()

        self.vis_config.note_highlight_enabled = self.note_highlight_checkbox.isChecked()
        self.vis_config.note_highlight_use_velocity = self.note_highlight_use_vel_checkbox.isChecked()
        self.vis_config.note_highlight_intensity = self.note_highlight_intensity_input.value()
        self.vis_config.note_highlight_min_intensity = self.note_highlight_min_intensity_input.value()
        self.vis_config.note_highlight_max_intensity = self.note_highlight_max_intensity_input.value()

        self.vis_config.note_sparks_enabled = self.note_sparks_checkbox.isChecked()
        self.vis_config.note_sparks_start_dist_ratio = self.note_sparks_start_dist_input.value()
        self.vis_config.note_sparks_start_length_ratio = self.note_sparks_start_length_input.value()
        self.vis_config.note_sparks_speed_ratio = self.note_sparks_speed_input.value()
        self.vis_config.note_sparks_speed_var_ratio = self.note_sparks_speed_var_input.value()
        self.vis_config.note_sparks_alpha_ratio = self.note_sparks_alpha_input.value()
        self.vis_config.note_sparks_count = self.note_sparks_count_input.value()
        self.vis_config.note_sparks_max_angle_deg = self.note_sparks_angle_input.value()
        self.vis_config.note_sparks_time_to_fade_sec = self.note_sparks_fade_time_input.value()

    # callbacks

    def _on_changes(self):
        if not self.block_changes_callback:
            self.on_changes_callback()
            self.refresh_ui()