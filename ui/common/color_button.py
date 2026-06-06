from common import RGB
from common import Color
from utility import QUtil
from PySide6.QtCore import Signal

from PySide6.QtWidgets import (
    QPushButton,
    QColorDialog
)

class ColorButton(QPushButton):
    valueChanged = Signal(tuple)

    def __init__(self, color: RGB = None, parent=None):
        super().__init__(parent)

        self._rgb = color if color is not None else Color.WHITE

        self.clicked.connect(self._pick_color)
        self.refresh()

    def setDisabled(self, disabled: bool):
        super().setDisabled(disabled)
        self.refresh()

    def getColor(self) -> RGB:
        return self._rgb

    def setColor(self, color: RGB):
        self._rgb = color
        self.refresh()

    def refresh(self):
        r, g, b = self._rgb
        self.setText(f"{r}, {g}, {b}")

        if not self.isEnabled():
            r, g, b = Color.DARK_GRAY

        # color bg + text by color
        self.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b});"
            f"color: {'black' if (r*0.299 + g*0.587 + b*0.114) > 160 else 'white'};"
        )

    # click handling
    def _pick_color(self):
        color = QColorDialog.getColor(QUtil.rgb_to_qcolor(self._rgb), self, "Choose color")
        if color.isValid():
            self._rgb = QUtil.qcolor_to_rgb(color)
            self.refresh()

            self.valueChanged.emit(self._rgb)
            