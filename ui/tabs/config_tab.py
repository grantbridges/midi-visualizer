from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMessageBox,
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

from models import VisConfig, Orientation
from ui.common import ColorButton, LayoutUtil, Icons, ScaledSpinbox, SliderDoubleSpinbox

class ConfigTab(QWidget):
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
        self.track_name = QLineEdit()
        self.track_name.editingFinished.connect(self._on_changes)

        self.orientation_combo = QComboBox()
        for mode in Orientation:
            self.orientation_combo.addItem(str(mode), mode)
        self.orientation_combo.currentIndexChanged.connect(self._on_changes)

        self.show_playhead_checkbox = QCheckBox()
        self.show_playhead_checkbox.toggled.connect(self._on_changes)
        self.playhead_color_button = ColorButton()
        self.playhead_color_button.valueChanged.connect(self._on_changes)
        self.playhead_opacity_input = ScaledSpinbox(display_min=0, display_max=100, internal_min=0, internal_max=255)
        self.playhead_opacity_input.valueChanged.connect(self._on_changes)
        self.playhead_thickness_input = QDoubleSpinBox(decimals=4, minimum=0.0001, maximum=0.1, singleStep=0.001)
        self.playhead_thickness_input.valueChanged.connect(self._on_changes)
        self.playhead_pos_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1.00, singleStep=0.01)
        self.playhead_pos_input.valueChanged.connect(self._on_changes)

        self.vertical_padding_input = SliderDoubleSpinbox(decimals=2, minimum=0.00, maximum=1.00, singleStep=0.01)
        self.vertical_padding_input.valueChanged.connect(self._on_changes)
        self.vertical_offset_input = SliderDoubleSpinbox(decimals=2, minimum=-1.00, maximum=1.00, singleStep=0.01)
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
        LayoutUtil.combobox(column, "Orientation", self.orientation_combo)

        LayoutUtil.section(column, "Scaling/Position")
        LayoutUtil.spinbox(column, "Vertical Padding", self.vertical_padding_input)
        LayoutUtil.spinbox(column, "Vertical Offset", self.vertical_offset_input)

        LayoutUtil.section(column, "Playhead")
        LayoutUtil.checkbox(column, "Show Playhead", self.show_playhead_checkbox)
        LayoutUtil.button(column, "Playhead Color", self.playhead_color_button)
        LayoutUtil.spinbox(column, "Playhead Opacity", self.playhead_opacity_input)
        LayoutUtil.spinbox(column, "Playhead Thickness", self.playhead_thickness_input)
        LayoutUtil.spinbox(column, "Playhead Position", self.playhead_pos_input)

        column.addStretch()

        # --- Right Column ---
        column = v_right_layout

        LayoutUtil.section(column, "Pitch Settings")
        LayoutUtil.checkbox(column, "Auto-Calc Pitch Min/Max", self.auto_calc_pitch_bounds_checkbox)
        LayoutUtil.spinbox(column, "Pitch Min", self.pitch_min_input)
        LayoutUtil.spinbox(column, "Pitch Max", self.pitch_max_input)

        LayoutUtil.section(column, "Time Offsets")
        LayoutUtil.checkbox(column, "Apply Time Offsets", self.apply_time_offsets_checkbox)
        LayoutUtil.spinbox(column, "Start Time Offset", self.start_time_input)
        LayoutUtil.spinbox(column, "End Time Offset", self.end_time_input)

        column.addStretch()

        root_h_layout.addLayout(v_left_layout, 1)
        root_h_layout.addSpacing(10)
        root_h_layout.addLayout(v_right_layout, 1)

        content_layout.addLayout(root_h_layout)
        
        scroll_area.setWidget(content)

        root.addWidget(scroll_area)

    def refresh_ui(self):
        self.block_changes_callback = True # prevent "change" callbacks from triggering while we set values

        self.track_name.setText(self.vis_config.track_name)

        index = self.orientation_combo.findData(self.vis_config.orientation)
        self.orientation_combo.setCurrentIndex(index)

        self.show_playhead_checkbox.setChecked(self.vis_config.show_playhead)
        self.playhead_color_button.setColor(self.vis_config.playhead_color)
        self.playhead_color_button.setEnabled(self.vis_config.show_playhead)
        self.playhead_opacity_input.setInternalValue(self.vis_config.playhead_alpha)
        self.playhead_opacity_input.setEnabled(self.vis_config.show_playhead)
        self.playhead_thickness_input.setValue(self.vis_config.playhead_thickness_ratio)
        self.playhead_thickness_input.setEnabled(self.vis_config.show_playhead)
        self.playhead_pos_input.setValue(self.vis_config.playhead_pos_ratio)
        self.playhead_pos_input.setEnabled(self.vis_config.show_playhead)

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
        self.start_time_input.setEnabled(self.vis_config.apply_time_offsets)
        self.start_time_input.setValue(self.vis_config.start_time_offset)
        self.end_time_input.setEnabled(self.vis_config.apply_time_offsets)
        self.end_time_input.setValue(self.vis_config.end_time_offset)  

        self.block_changes_callback = False

    def update_model(self):
        # pull UI values out of controls and set on model
        self.vis_config.track_name = self.track_name.text()
        self.vis_config.orientation = self.orientation_combo.currentData()

        self.vis_config.show_playhead = self.show_playhead_checkbox.isChecked()
        self.vis_config.playhead_color = self.playhead_color_button.getColor()
        self.vis_config.playhead_alpha = self.playhead_opacity_input.getInternalValue()
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

    # callbacks

    def _on_changes(self):
        if not self.block_changes_callback:
            self.on_changes_callback()
            self.refresh_ui()
