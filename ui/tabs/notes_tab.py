from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QScrollArea,
    QCheckBox,
    QDoubleSpinBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)
from models import VisConfig
from ui.common import (
    LayoutUtil, 
    ColorButton,
    SliderSpinbox,
    SliderDoubleSpinbox
)

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
        self.enhance_color_checkbox = QCheckBox()
        self.enhance_color_checkbox.toggled.connect(self._on_changes)
        self.round_edges_checkbox = QCheckBox()
        self.round_edges_checkbox.toggled.connect(self._on_changes)
        self.round_edges_input = SliderDoubleSpinbox(decimals=2, minimum=0.00, maximum=1.0, singleStep=0.01)
        self.round_edges_input.valueChanged.connect(self._on_changes)

        self.fadein_checkbox = QCheckBox()
        self.fadein_checkbox.toggled.connect(self._on_changes)
        self.fadein_start_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.00, singleStep=.01)
        self.fadein_start_input.valueChanged.connect(self._on_changes)
        self.fadein_end_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.00, singleStep=.01)
        self.fadein_end_input.valueChanged.connect(self._on_changes)
        self.fadeout_checkbox = QCheckBox()
        self.fadeout_checkbox.toggled.connect(self._on_changes)
        self.fadeout_start_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.00, singleStep=.01)
        self.fadeout_start_input.valueChanged.connect(self._on_changes)
        self.fadeout_end_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.00, singleStep=.01)
        self.fadeout_end_input.valueChanged.connect(self._on_changes)

        self.glow_checkbox = QCheckBox()
        self.glow_checkbox.toggled.connect(self._on_changes)
        self.glow_played_region_checkbox = QCheckBox()
        self.glow_played_region_checkbox.toggled.connect(self._on_changes)
        self.glow_color = ColorButton()
        self.glow_color.valueChanged.connect(self._on_changes)
        self.glow_size_input = SliderDoubleSpinbox(decimals=2, minimum=0.00, maximum=2.0, singleStep=0.01)
        self.glow_size_input.valueChanged.connect(self._on_changes)
        self.glow_intensity_input = SliderDoubleSpinbox(decimals=2, minimum=0.00, maximum=1.00, singleStep=0.01)
        self.glow_intensity_input.valueChanged.connect(self._on_changes)

        self.highlight_checkbox = QCheckBox()
        self.highlight_checkbox.toggled.connect(self._on_changes)
        self.highlight_played_region_checkbox = QCheckBox()
        self.highlight_played_region_checkbox.toggled.connect(self._on_changes)
        self.highlight_use_vel_checkbox = QCheckBox()
        self.highlight_use_vel_checkbox.toggled.connect(self._on_changes)
        self.highlight_color = ColorButton()
        self.highlight_color.valueChanged.connect(self._on_changes)
        self.highlight_intensity_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.00, singleStep=0.01)
        self.highlight_intensity_input.valueChanged.connect(self._on_changes)
        self.highlight_min_intensity_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.00, singleStep=0.01)
        self.highlight_min_intensity_input.valueChanged.connect(self._on_changes)
        self.highlight_max_intensity_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.00, singleStep=0.01)
        self.highlight_max_intensity_input.valueChanged.connect(self._on_changes)

        self.sparks_checkbox = QCheckBox()
        self.sparks_checkbox.toggled.connect(self._on_changes)
        self.sparks_start_dist_input = SliderDoubleSpinbox(decimals=1, minimum=0.0, maximum=10.0, singleStep=0.1)
        self.sparks_start_dist_input.valueChanged.connect(self._on_changes)
        self.sparks_start_length_input = SliderDoubleSpinbox(decimals=2, minimum=0.25, maximum=10.0, singleStep=0.01)
        self.sparks_start_length_input.valueChanged.connect(self._on_changes)
        self.sparks_speed_input = SliderDoubleSpinbox(decimals=2, minimum=0.01, maximum=5.0, singleStep=0.01)
        self.sparks_speed_input.valueChanged.connect(self._on_changes)
        self.sparks_speed_var_input = SliderDoubleSpinbox(decimals=2, minimum=0.01, maximum=5.0, singleStep=0.01)
        self.sparks_speed_var_input.valueChanged.connect(self._on_changes)
        self.sparks_opacity_ratio_input = SliderDoubleSpinbox(decimals=2, minimum=0.01, maximum=1.0, singleStep=0.01)
        self.sparks_opacity_ratio_input.valueChanged.connect(self._on_changes)
        self.sparks_count_input = SliderSpinbox(minimum=1, maximum=50)
        self.sparks_count_input.valueChanged.connect(self._on_changes)
        self.sparks_angle_input = SliderSpinbox(minimum=0, maximum=180, suffix="°")
        self.sparks_angle_input.valueChanged.connect(self._on_changes)
        self.sparks_fade_time_input = SliderDoubleSpinbox(decimals=2, minimum=0.01, maximum=5.0, singleStep=0.01, suffix=" sec")
        self.sparks_fade_time_input.valueChanged.connect(self._on_changes)

        self.bounce_checkbox = QCheckBox()
        self.bounce_checkbox.toggled.connect(self._on_changes)
        self.bounce_height_input = SliderDoubleSpinbox(decimals=2, minimum=0.01, maximum=5.0, singleStep=0.01)
        self.bounce_height_input.valueChanged.connect(self._on_changes)

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
        LayoutUtil.checkbox(column, "Fade In Enabled", self.fadein_checkbox)
        LayoutUtil.spinbox(column, "Fade In Start", self.fadein_start_input)
        LayoutUtil.spinbox(column, "Fade In End", self.fadein_end_input)
        LayoutUtil.checkbox(column, "Fade Out Enabled", self.fadeout_checkbox)
        LayoutUtil.spinbox(column, "Fade Out Start", self.fadeout_start_input)
        LayoutUtil.spinbox(column, "Fade Out End", self.fadeout_end_input)

        LayoutUtil.section(column, "Highlight")
        LayoutUtil.checkbox(column, "Highlight Enabled", self.highlight_checkbox)
        LayoutUtil.checkbox(column, "Highlight Only Played Region", self.highlight_played_region_checkbox)
        LayoutUtil.button(column, "Highlight Color", self.highlight_color)
        LayoutUtil.checkbox(column, "Highlight Intensity by Velocity", self.highlight_use_vel_checkbox)
        self.highlight_intensity_row = LayoutUtil.spinbox(column, "Highlight Intensity", self.highlight_intensity_input)
        self.highlight_min_intensity_row = LayoutUtil.spinbox(column, "Highlight Min Intensity", self.highlight_min_intensity_input)
        self.highlight_max_intensity_row = LayoutUtil.spinbox(column, "Highlight Max Intensity", self.highlight_max_intensity_input)
        LayoutUtil.section(column, "Glow")
        LayoutUtil.checkbox(column, "Glow Enabled", self.glow_checkbox)
        LayoutUtil.checkbox(column, "Glow Only Played Region", self.glow_played_region_checkbox)
        LayoutUtil.button(column, "Glow Color", self.glow_color)
        LayoutUtil.spinbox(column, "Glow Size", self.glow_size_input)
        LayoutUtil.spinbox(column, "Glow Intensity", self.glow_intensity_input)

        column.addStretch()

        # --- Right Column ---
        column = v_right_layout

        LayoutUtil.section(column, "Style")
        LayoutUtil.checkbox(column, "Enhance Color", self.enhance_color_checkbox)
        LayoutUtil.checkbox(column, "Round Edges", self.round_edges_checkbox)
        LayoutUtil.spinbox(column, "Round Edges Amount", self.round_edges_input)

        LayoutUtil.section(column, "Sparks")
        LayoutUtil.checkbox(column, "Sparks Enabled", self.sparks_checkbox)
        LayoutUtil.spinbox(column, "Start Distance", self.sparks_start_dist_input)
        LayoutUtil.spinbox(column, "Size", self.sparks_start_length_input)
        LayoutUtil.spinbox(column, "Speed Min", self.sparks_speed_input)
        LayoutUtil.spinbox(column, "Speed Max", self.sparks_speed_var_input)
        LayoutUtil.spinbox(column, "Opacity Ratio", self.sparks_opacity_ratio_input)
        LayoutUtil.spinbox(column, "Particle Count", self.sparks_count_input)
        LayoutUtil.spinbox(column, "Angle", self.sparks_angle_input)
        LayoutUtil.spinbox(column, "Fade Time", self.sparks_fade_time_input)

        LayoutUtil.section(column, "Bounce")
        LayoutUtil.checkbox(column, "Bounce Enabled", self.bounce_checkbox)
        LayoutUtil.spinbox(column, "Bounce Grow Size", self.bounce_height_input)

        column.addStretch()

        root_h_layout.addLayout(v_left_layout, 1)
        root_h_layout.addSpacing(10)
        root_h_layout.addLayout(v_right_layout, 1)

        content_layout.addLayout(root_h_layout)
        
        scroll_area.setWidget(content)

        root.addWidget(scroll_area)

    def refresh_ui(self):
        self.block_changes_callback = True # prevent "change" callbacks from triggering while we set values

        self.enhance_color_checkbox.setChecked(self.vis_config.note_enhance_color)
        self.round_edges_checkbox.setChecked(self.vis_config.note_round_edges)
        self.round_edges_input.setValue(self.vis_config.note_round_ratio)
        self.round_edges_input.setEnabled(self.vis_config.note_round_edges)

        self.fadein_checkbox.setChecked(self.vis_config.note_fadein_enabled)
        self.fadein_start_input.setValue(self.vis_config.note_fadein_start_ratio)
        self.fadein_start_input.setMinimum(self.vis_config.note_fadein_end_ratio + .01)
        self.fadein_start_input.setEnabled(self.vis_config.note_fadein_enabled)
        self.fadein_end_input.setValue(self.vis_config.note_fadein_end_ratio)
        self.fadein_end_input.setMaximum(self.vis_config.note_fadein_start_ratio - .01)
        self.fadein_end_input.setEnabled(self.vis_config.note_fadein_enabled)

        self.fadeout_checkbox.setChecked(self.vis_config.note_fadeout_enabled)
        self.fadeout_start_input.setValue(self.vis_config.note_fadeout_start_ratio)
        self.fadeout_start_input.setMinimum(self.vis_config.note_fadeout_end_ratio + .01)
        self.fadeout_start_input.setEnabled(self.vis_config.note_fadeout_enabled)
        self.fadeout_end_input.setValue(self.vis_config.note_fadeout_end_ratio)
        self.fadeout_end_input.setMaximum(self.vis_config.note_fadeout_start_ratio - .01)
        self.fadeout_end_input.setEnabled(self.vis_config.note_fadeout_enabled)

        self.glow_checkbox.setChecked(self.vis_config.note_glow_enabled)
        self.glow_played_region_checkbox.setChecked(self.vis_config.note_glow_played_region)
        self.glow_played_region_checkbox.setEnabled(self.vis_config.note_glow_enabled)
        self.glow_color.setColor(self.vis_config.note_glow_color)
        self.glow_color.setEnabled(self.vis_config.note_glow_enabled)
        self.glow_size_input.setValue(self.vis_config.note_glow_size)
        self.glow_size_input.setEnabled(self.vis_config.note_glow_enabled)
        self.glow_intensity_input.setValue(self.vis_config.note_glow_intensity)
        self.glow_intensity_input.setEnabled(self.vis_config.note_glow_enabled)

        self.highlight_checkbox.setChecked(self.vis_config.note_highlight_enabled)
        self.highlight_played_region_checkbox.setChecked(self.vis_config.note_highlight_played_region)
        self.highlight_played_region_checkbox.setEnabled(self.vis_config.note_highlight_enabled)
        self.highlight_use_vel_checkbox.setChecked(self.vis_config.note_highlight_use_velocity)
        self.highlight_use_vel_checkbox.setEnabled(self.vis_config.note_highlight_enabled)
        self.highlight_color.setColor(self.vis_config.note_highlight_color)
        self.highlight_color.setEnabled(self.vis_config.note_highlight_enabled)
        self.highlight_intensity_input.setValue(self.vis_config.note_highlight_intensity)
        self.highlight_intensity_input.setEnabled(self.vis_config.note_highlight_enabled)
        self.highlight_intensity_row.setVisible(not self.vis_config.note_highlight_use_velocity)
        self.highlight_min_intensity_input.setValue(self.vis_config.note_highlight_min_intensity)
        self.highlight_min_intensity_input.setEnabled(self.vis_config.note_highlight_enabled)
        self.highlight_min_intensity_input.setMaximum(self.vis_config.note_highlight_max_intensity - .01)
        self.highlight_min_intensity_row.setVisible(self.vis_config.note_highlight_use_velocity)
        self.highlight_max_intensity_input.setValue(self.vis_config.note_highlight_max_intensity)
        self.highlight_max_intensity_input.setEnabled(self.vis_config.note_highlight_enabled)
        self.highlight_max_intensity_input.setMinimum(self.vis_config.note_highlight_min_intensity + .01)
        self.highlight_max_intensity_row.setVisible(self.vis_config.note_highlight_use_velocity)

        self.sparks_checkbox.setChecked(self.vis_config.note_sparks_enabled)
        self.sparks_start_dist_input.setValue(self.vis_config.note_sparks_start_dist_ratio)
        self.sparks_start_dist_input.setEnabled(self.vis_config.note_sparks_enabled)
        self.sparks_start_length_input.setValue(self.vis_config.note_sparks_start_length_ratio)
        self.sparks_start_length_input.setEnabled(self.vis_config.note_sparks_enabled)
        self.sparks_speed_input.setValue(self.vis_config.note_sparks_speed_ratio)
        self.sparks_speed_input.setEnabled(self.vis_config.note_sparks_enabled)
        self.sparks_speed_var_input.setValue(self.vis_config.note_sparks_speed_var_ratio)
        self.sparks_speed_var_input.setEnabled(self.vis_config.note_sparks_enabled)
        self.sparks_opacity_ratio_input.setValue(self.vis_config.note_sparks_alpha_ratio)
        self.sparks_opacity_ratio_input.setEnabled(self.vis_config.note_sparks_enabled)
        self.sparks_count_input.setValue(self.vis_config.note_sparks_count)
        self.sparks_count_input.setEnabled(self.vis_config.note_sparks_enabled)
        self.sparks_angle_input.setValue(self.vis_config.note_sparks_max_angle_deg)
        self.sparks_angle_input.setEnabled(self.vis_config.note_sparks_enabled)
        self.sparks_fade_time_input.setValue(self.vis_config.note_sparks_time_to_fade_sec)
        self.sparks_fade_time_input.setEnabled(self.vis_config.note_sparks_enabled)
        
        self.bounce_checkbox.setChecked(self.vis_config.note_bounce_enabled)
        self.bounce_height_input.setValue(self.vis_config.note_bounce_height_ratio)
        self.bounce_height_input.setEnabled(self.vis_config.note_bounce_enabled)

        self.block_changes_callback = False

    def update_model(self):
        # pull UI values out of controls and set on model

        self.vis_config.note_enhance_color = self.enhance_color_checkbox.isChecked()
        self.vis_config.note_round_edges = self.round_edges_checkbox.isChecked()
        self.vis_config.note_round_ratio = self.round_edges_input.value()
        
        self.vis_config.note_fadein_enabled = self.fadein_checkbox.isChecked()
        self.vis_config.note_fadein_start_ratio = self.fadein_start_input.value()
        self.vis_config.note_fadein_end_ratio = self.fadein_end_input.value()
        self.vis_config.note_fadeout_enabled = self.fadeout_checkbox.isChecked()
        self.vis_config.note_fadeout_start_ratio = self.fadeout_start_input.value()
        self.vis_config.note_fadeout_end_ratio = self.fadeout_end_input.value()

        self.vis_config.note_glow_enabled = self.glow_checkbox.isChecked()
        self.vis_config.note_glow_played_region = self.glow_played_region_checkbox.isChecked()
        self.vis_config.note_glow_color = self.glow_color.getColor()
        self.vis_config.note_glow_size = self.glow_size_input.value()
        self.vis_config.note_glow_intensity = self.glow_intensity_input.value()

        self.vis_config.note_highlight_enabled = self.highlight_checkbox.isChecked()
        self.vis_config.note_highlight_played_region = self.highlight_played_region_checkbox.isChecked()
        self.vis_config.note_highlight_use_velocity = self.highlight_use_vel_checkbox.isChecked()
        self.vis_config.note_highlight_color = self.highlight_color.getColor()
        self.vis_config.note_highlight_intensity = self.highlight_intensity_input.value()
        self.vis_config.note_highlight_min_intensity = self.highlight_min_intensity_input.value()
        self.vis_config.note_highlight_max_intensity = self.highlight_max_intensity_input.value()

        self.vis_config.note_sparks_enabled = self.sparks_checkbox.isChecked()
        self.vis_config.note_sparks_start_dist_ratio = self.sparks_start_dist_input.value()
        self.vis_config.note_sparks_start_length_ratio = self.sparks_start_length_input.value()
        self.vis_config.note_sparks_speed_ratio = self.sparks_speed_input.value()
        self.vis_config.note_sparks_speed_var_ratio = self.sparks_speed_var_input.value()
        self.vis_config.note_sparks_alpha_ratio = self.sparks_opacity_ratio_input.value()
        self.vis_config.note_sparks_count = self.sparks_count_input.value()
        self.vis_config.note_sparks_max_angle_deg = self.sparks_angle_input.value()
        self.vis_config.note_sparks_time_to_fade_sec = self.sparks_fade_time_input.value()

        self.vis_config.note_bounce_enabled = self.bounce_checkbox.isChecked()
        self.vis_config.note_bounce_height_ratio = self.bounce_height_input.value()

    # callbacks

    def _on_changes(self):
        if not self.block_changes_callback:
            self.on_changes_callback()
            self.refresh_ui()