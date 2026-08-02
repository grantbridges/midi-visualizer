import logging
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
from ui.common import WidgetUtil
from utility import Util, ProgressCalc

logger = logging.getLogger("ExportProgressDialog")

class ExportProgressDialog(QDialog):
    cancel_clicked = Signal()

    def __init__(self, track_title: str, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"{track_title} Export")
        self.setModal(True)
        self.setFixedSize(400, 140)

        self.setWindowFlags(
            Qt.WindowType.Dialog
            # prevent resizing or exiting from window bar
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )

        self.cancelling: bool = False
        self.progress_calc: ProgressCalc = ProgressCalc()

        # --- Widgets ---
        self.status_label = QLabel("Preparing...")
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setWordWrap(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        self.time_remaining_label = WidgetUtil.hint_label("Est. time remaining: Calculating...")

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
        root_layout.addWidget(self.time_remaining_label)
        root_layout.addStretch()

        button_row = QHBoxLayout()
        button_row.addWidget(self.open_file_checkbox)
        button_row.addStretch()
        button_row.addWidget(self.cancel_button)

        root_layout.addLayout(button_row)

        self.cancel_button.clicked.connect(self._on_cancel_clicked)

    def update_progress(self, percent: float, message: str):
        if self.cancelling:
            return # ignore
        
        if percent and percent >= 0 and percent <= 100:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(int(percent))

            remaining_ms = self.progress_calc.update(percent)
            if remaining_ms is not None:
                self.time_remaining_label.setText(f"Est. time remaining: {Util.format_ms(remaining_ms)}")

        else:
            # show indeterminate
            self.progress_bar.setRange(0, 0)
            self.time_remaining_label.setText("Est. time remaining: Calculating...")

        self.status_label.setText(message)

    def get_open_output_file(self) -> bool:
        return self.open_file_checkbox.isChecked()

    def _on_cancel_clicked(self):
        self.cancelling = True

        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Cancelling export...")
        self.time_remaining_label.setText("")

        self.cancel_button.setDisabled(True)
        self.open_file_checkbox.setDisabled(True)

        self.cancel_clicked.emit()