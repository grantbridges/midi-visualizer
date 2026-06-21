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
        self.note_highlight_intensity_input = QDoubleSpinBox(decimals=2, minimum=0.00, maximum=1.00, singleStep=0.01)
        self.note_highlight_intensity_input.valueChanged.connect(self._on_changes)

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

        # Left Column

        v_left_layout.addWidget(SectionDivider("Note Style"))

        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Note Fade Distance"))
        h_layout.addWidget(self.note_fadeout_input)
        v_left_layout.addLayout(h_layout)

        v_left_layout.addWidget(SectionDivider("Note Highlight & Glow"))

        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Note Highlight Enabled"))
        h_layout.addStretch()
        h_layout.addWidget(self.note_highlight_checkbox)
        v_left_layout.addLayout(h_layout)

        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Note Highlight Intensity"))
        h_layout.addWidget(self.note_highlight_intensity_input)
        v_left_layout.addLayout(h_layout)

        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Note Glow Enabled"))
        h_layout.addStretch()
        h_layout.addWidget(self.note_glow_checkbox)
        v_left_layout.addLayout(h_layout)

        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Note Glow Size"))
        h_layout.addWidget(self.note_glow_size_input)
        v_left_layout.addLayout(h_layout)

        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Note Glow Intensity"))
        h_layout.addWidget(self.note_glow_intensity_input)
        v_left_layout.addLayout(h_layout)

        v_left_layout.addStretch()

        # Right Column

        v_right_layout.addStretch()

        root_h_layout.addLayout(v_left_layout, 1)
        root_h_layout.addLayout(v_right_layout, 1)

        content_layout.addLayout(root_h_layout)
        
        scroll_area.setWidget(content)

        root.addWidget(scroll_area)

    def refresh_ui(self):
        self.block_changes_callback = True # prevent "change" callbacks from triggering while we set values

        self.note_fadeout_input.setValue(self.vis_config.note_fadeout_ratio)

        self.note_glow_checkbox.setChecked(self.vis_config.note_glow_enabled)
        self.note_glow_size_input.setValue(self.vis_config.note_glow_size)
        self.note_glow_size_input.setDisabled(not self.vis_config.note_glow_enabled)
        self.note_glow_intensity_input.setValue(self.vis_config.note_glow_intensity)
        self.note_glow_intensity_input.setDisabled(not self.vis_config.note_glow_enabled)

        self.note_highlight_checkbox.setChecked(self.vis_config.note_highlight_enabled)
        self.note_highlight_intensity_input.setValue(self.vis_config.note_highlight_intensity)
        self.note_highlight_intensity_input.setDisabled(not self.vis_config.note_highlight_enabled)

        self.block_changes_callback = False

    def update_model(self):
        # pull UI values out of controls and set on model
        
        self.vis_config.note_fadeout_ratio = self.note_fadeout_input.value()

        self.vis_config.note_glow_enabled = self.note_glow_checkbox.isChecked()
        self.vis_config.note_glow_size = self.note_glow_size_input.value()
        self.vis_config.note_glow_intensity = self.note_glow_intensity_input.value()

        self.vis_config.note_highlight_enabled = self.note_highlight_checkbox.isChecked()
        self.vis_config.note_highlight_intensity = self.note_highlight_intensity_input.value()

    # callbacks

    def _on_changes(self):
        if not self.block_changes_callback:
            self.on_changes_callback()
            self.refresh_ui()