from typing import override

from PySide6.QtWidgets import QWidget, QHBoxLayout, QCheckBox
from PySide6.QtCore import Qt, Signal

class TableCheckBox(QWidget):
    '''
    Wrapper around QCheckBox for use in tables so it centers nicely
    '''
    valueChanged = Signal(bool)

    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(checked)

        self.checkbox.clicked.connect(self._on_clicked)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.checkbox)

    def _on_clicked(self):
        self.valueChanged.emit(self.isChecked())

    @override
    def isChecked(self) -> bool:
        return self.checkbox.isChecked()

    @override
    def setChecked(self, value: bool):
        self.checkbox.setChecked(value)