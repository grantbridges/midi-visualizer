from dataclasses import dataclass
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QHBoxLayout,
    QLineEdit, 
    QFileDialog,
    QComboBox
)
from pathlib import Path
from models import VisConfig, RenderFormat, Resolution
from ui.common import LayoutUtil

@dataclass
class ExportOptions:
    filename: str
    output_dir: str
    render_format: RenderFormat
    resolution: Resolution
    fps: int

class ExportOptionsDialog(QDialog):
    def __init__(self, vis_config: VisConfig, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Export")
        self.setModal(True)

        self._options: ExportOptions | None = None

        # -- Create Controls --

        # Output directory selection
        output_dir = vis_config.export_dir if vis_config.export_dir else str(Path.home() / "Desktop")
        self.output_dir_input = QLineEdit(output_dir)
        self.output_dir_input.setReadOnly(True)
        browse_btn = QPushButton("…")
        browse_btn.clicked.connect(self.browse_output_dir)

        # Filename input
        filename = vis_config.export_filename if vis_config.export_filename else vis_config.track_name
        self.filename_input = QLineEdit(filename)
        self.filename_ext = QLabel(f".{vis_config.export_format.value}")

        # render format dropdown
        self.format_combo = QComboBox()
        self.format_combo.addItem("mp4", RenderFormat.MP4)
        self.format_combo.addItem("mov", RenderFormat.MOV)
        self.format_combo.addItem("webm", RenderFormat.WEBM)
        self.format_combo.currentIndexChanged.connect(self.on_format_combo_changed)

        # initialize export format dropdown
        index = self.format_combo.findData(vis_config.export_format)
        self.format_combo.setCurrentIndex(index)

        # resolution combo
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItem("Low (360p)", Resolution.Low)
        self.resolution_combo.addItem("SD (480p)", Resolution.SD)
        self.resolution_combo.addItem("HD (720p)", Resolution.HD)
        self.resolution_combo.addItem("Full HD (1080p)", Resolution.FullHD)
        self.resolution_combo.addItem("Quad HD (1440p)", Resolution.QuadHD)
        self.resolution_combo.addItem("4K (2160p)", Resolution.UltraHD)
        self.resolution_combo.insertSeparator(self.resolution_combo.count())
        self.resolution_combo.addItem("Vertical", Resolution.VerticalHD)
        self.resolution_combo.addItem("Square", Resolution.SquareHD)
        self.resolution_combo.addItem("Portrait Feed", Resolution.PortraitFeed)

        # initialize resolution dropdown
        index = self.resolution_combo.findData(vis_config.export_resolution)
        self.resolution_combo.setCurrentIndex(index)

        # fps
        self.fps_input = QSpinBox(value=vis_config.export_fps, minimum=1, maximum=120)

        # button row
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.on_export_clicked)

        # -- Layout Controls --

        column = QVBoxLayout(self)

        LayoutUtil.file_picker(column, "Output folder", self.output_dir_input, browse_btn)
        LayoutUtil.line_edit_suffix(column, "Filename", self.filename_input, self.filename_ext)
        LayoutUtil.combobox(column, "Format", self.format_combo)
        LayoutUtil.combobox(column, "Resolution", self.resolution_combo)
        LayoutUtil.spinbox(column, "FPS", self.fps_input)
        LayoutUtil.buttons(column, [cancel_btn, export_btn])

        export_btn.setDefault(True) # highlight

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
            resolution=self.resolution_combo.currentData(),
            fps=self.fps_input.value()
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