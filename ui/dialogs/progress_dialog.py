from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal

from ui.common.layout_util import LayoutUtil

class ProgressDialog(QDialog):
    '''
    A generic progress dialog with configurable display text and finished, 
    failed, and progress callback handling, and an optional cancel button 
    '''
    cancel_clicked = Signal()

    def __init__(self, title: str, message: str, allow_cancel: bool=False, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(340, 120)

        self.setWindowFlags(
            Qt.WindowType.Dialog
            # prevent resizing or exiting from window bar
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )

        # --- Widgets ---
        self.status_label = QLabel(message)
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setWordWrap(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        button_box = QDialogButtonBox()
        cancel_btn = button_box.addButton("Cancel", QDialogButtonBox.RejectRole)
        cancel_btn.setEnabled(allow_cancel)
        cancel_btn.setDefault(True)
        cancel_btn.setAutoDefault(True)
        button_box.rejected.connect(self.cancel_clicked)

        # --- Layout ---
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(10)

        root_layout.addWidget(self.status_label)
        root_layout.addWidget(self.progress_bar)

        root_layout.addStretch()
        LayoutUtil.dialog_button_box(root_layout, button_box)

    def update_progress(self, percent: int):
        if percent and percent >= 0 and percent <= 100:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(percent)
        else:
            # show indeterminate
            self.progress_bar.setRange(0, 0)

    def _on_cancel_clicked(self):
        self.cancel_clicked.emit()