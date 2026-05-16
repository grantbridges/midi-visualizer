from dataclasses import dataclass
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QHBoxLayout,
    QLineEdit, 
    QFileDialog,
    QComboBox
)
from pathlib import Path
from models import VisConfig, RenderFormat, Resolution

@dataclass
class ExportOptions:
    filename: str
    output_dir: str
    render_format: RenderFormat
    resolution: Resolution

class ExportOptionsDialog(QDialog):
    def __init__(self, vis_config: VisConfig, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Export")
        self.setModal(True)

        self._options: ExportOptions | None = None

        layout = QVBoxLayout(self)

        # Output directory selection
        output_dir = vis_config.export_dir if vis_config.export_dir else str(Path.home() / "Desktop")
        self.output_dir_input = QLineEdit(output_dir)
        self.output_dir_input.setReadOnly(True)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output_dir)
        output_dir_row = QHBoxLayout()
        output_dir_row.addWidget(QLabel("Output folder"))
        output_dir_row.addWidget(self.output_dir_input)
        output_dir_row.addWidget(browse_btn)
        layout.addLayout(output_dir_row)

        # Filename input
        filename = vis_config.export_filename if vis_config.export_filename else vis_config.track_name
        self.filename_input = QLineEdit(filename)
        filename_row = QHBoxLayout()
        filename_row.addWidget(QLabel("Filename"))
        filename_row.addWidget(self.filename_input)
        self.filename_ext = QLabel(f".{vis_config.export_format}")
        filename_row.addWidget(self.filename_ext)
        layout.addLayout(filename_row)

        # render format dropdown
        self.format_combo = QComboBox()
        self.format_combo.addItem("mp4", RenderFormat.MP4)
        self.format_combo.addItem("mov", RenderFormat.MOV)
        self.format_combo.addItem("webm", RenderFormat.WEBM)
        self.format_combo.currentIndexChanged.connect(self.on_format_combo_changed)

        if vis_config.export_format:
            # initialize if previously set
            index = self.format_combo.findData(vis_config.export_format)
            self.format_combo.setCurrentIndex(index)

        format_row = QHBoxLayout()
        format_row.addWidget(QLabel("Format"))
        format_row.addWidget(self.format_combo)
        layout.addLayout(format_row)

        # resolution combo
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItem("HD (720p)", Resolution.HD)
        self.resolution_combo.addItem("Full HD (1080p)", Resolution.FullHD)
        self.resolution_combo.addItem("Quad HD (1440p)", Resolution.QuadHD)
        self.resolution_combo.addItem("4K (2160p)", Resolution.UltraHD)

        if vis_config.export_resolution:
            # initialize if previously set
            index = self.resolution_combo.findData(vis_config.export_resolution)
            self.resolution_combo.setCurrentIndex(index)

        resolution_row = QHBoxLayout()
        resolution_row.addWidget(QLabel("Resolution"))
        resolution_row.addWidget(self.resolution_combo)
        layout.addLayout(resolution_row)

        # button row
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        export_btn = QPushButton("Export")
        export_btn.setDefault(True) # highlight
        export_btn.clicked.connect(self.on_export_clicked)

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(cancel_btn)
        button_row.addWidget(export_btn)
        layout.addLayout(button_row)

        # resize and fix
        self.adjustSize()
        self.setFixedSize(self.size())

    def browse_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Output Folder", self.output_dir_input.text())
        if folder:
            self.output_dir_input.setText(folder)

    def on_format_combo_changed(self):
        rf: RenderFormat = self.format_combo.currentData()
        self.filename_ext.setText(f".{rf.value}")
    
    def on_export_clicked(self):
        # pull values out of ui
        options = ExportOptions(
            output_dir=self.output_dir_input.text(),
            filename=self.filename_input.text(),
            render_format=self.format_combo.currentData(),
            resolution=self.resolution_combo.currentData()
        )

        # validation
        if not options.output_dir:
            QMessageBox.critical(None, 'Error', 'Output directory required')
            return
        
        if not options.filename:
            QMessageBox.critical(None, 'Error', 'Filename required')
            return
        
        # validation passed
        self._options = options
        self.accept()

    def get_options(self) -> ExportOptions | None:
        return self._options