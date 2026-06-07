from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QProgressBar,
    QPushButton,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

class ExportProgressDialog(QDialog):
    cancel_clicked = Signal()

    def __init__(self, track_title: str, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"{track_title} Export")
        self.setModal(True)
        self.setFixedSize(400, 140)

        # --- Widgets ---
        self.status_label = QLabel("Preparing...")
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setWordWrap(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        self.open_file_checkbox = QCheckBox("Open file when complete")
        self.open_file_checkbox.setChecked(True)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # --- Layout ---
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(10)

        root_layout.addWidget(self.status_label)
        root_layout.addWidget(self.progress_bar)
        root_layout.addStretch()

        button_row = QHBoxLayout()
        button_row.addWidget(self.open_file_checkbox)
        button_row.addStretch()
        button_row.addWidget(self.cancel_button)

        root_layout.addLayout(button_row)

        self.cancel_button.clicked.connect(self._on_cancel_clicked)

    def update_progress(self, percent: int, message: str):
        if percent and percent >= 0 and percent <= 100:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(percent)
        else:
            # show indeterminate
            self.progress_bar.setRange(0, 0)

        self.status_label.setText(message)

    def get_open_output_file(self) -> bool:
        return self.open_file_checkbox.isChecked()

    def _on_cancel_clicked(self):
        self.cancel_clicked.emit()