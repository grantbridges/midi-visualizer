from common import RGB
from common import Color
from utility import QUtil

from PySide6.QtWidgets import (
    QPushButton,
    QColorDialog
)

class ColorButton(QPushButton):
    def __init__(self, color: RGB, parent=None):
        super().__init__(parent)
        self.rgb = color

        self.clicked.connect(self.pick_color)
        self.refresh()

    def refresh(self):
        r, g, b = self.rgb
        self.setText(f"{r}, {g}, {b}")

        # color bg + text by color
        self.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b});"
            f"color: {'black' if (r*0.299 + g*0.587 + b*0.114) > 160 else 'white'};"
        )

    def pick_color(self):
        color = QColorDialog.getColor(QUtil.rgb_to_qcolor(self.rgb), self, "Choose color")
        if color.isValid():
            self.rgb = QUtil.qcolor_to_rgb(color)
            self.refresh()
            