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

from models import VisConfig
from ui.common import ColorButton, LayoutUtil, Icons

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

        column.addStretch()

        # --- Right Column ---
        column = v_right_layout

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

        self.block_changes_callback = False

    def update_model(self):
        # pull UI values out of controls and set on model
        self.vis_config.play_audio = self.use_audio_checkbox.isChecked()
        self.vis_config.audio_filepath = self.audio_file_input.text()

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
