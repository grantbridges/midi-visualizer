from common import RGB
from PySide6.QtGui import QColor
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
        self.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b});"
            f"color: {'black' if (r*0.299 + g*0.587 + b*0.114) > 160 else 'white'};"
        )

    def pick_color(self):
        color = QColorDialog.getColor(ColorButton._rgb_to_qcolor(self.rgb), self, "Choose color")
        if color.isValid():
            self.rgb = ColorButton._qcolor_to_rgb(color)
            self.refresh()

    @staticmethod
    def _rgb_to_qcolor(rgb: RGB) -> QColor:
        return QColor(*rgb)

    @staticmethod
    def _qcolor_to_rgb(color: QColor) -> RGB:
        return (color.red(), color.green(), color.blue())
            