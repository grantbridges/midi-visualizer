from typing import Tuple
from editor.qt_util import QtUtil
from PySide6.QtWidgets import (
    QPushButton,
    QColorDialog,
)

class ColorButton(QPushButton):
    def __init__(self, color: Tuple[int, int, int], parent=None):
        super().__init__(parent)
        self.rgb = color
        self.clicked.connect(self.pick_color)
        self.refresh()

    def refresh(self):
        r, g, b = self.rgb
        self.setText(f"{r}, {g}, {b}")
        self.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b});"
            f"color: {'black' if (r*0.299 + g*0.587 + b*0.114) > 160 else 'white'};"
        )

    def pick_color(self):
        color = QColorDialog.getColor(QtUtil.rgb_to_qcolor(self.rgb), self, "Choose color")
        if color.isValid():
            self.rgb = QtUtil.qcolor_to_rgb(color)
            self.refresh()
            