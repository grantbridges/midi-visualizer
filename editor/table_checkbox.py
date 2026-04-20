from PySide6.QtWidgets import QWidget, QHBoxLayout, QCheckBox
from PySide6.QtCore import Qt

class TableCheckbox(QWidget):
    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(checked)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.checkbox)

    def isChecked(self) -> bool:
        return self.checkbox.isChecked()

    def setChecked(self, value: bool):
        self.checkbox.setChecked(value)