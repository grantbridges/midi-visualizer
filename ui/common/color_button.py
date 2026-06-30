from common import RGB
from common import Color
from utility import QUtil, Util

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QPushButton,
    QColorDialog,
    QApplication,
    QMenu,
)


class ColorButton(QPushButton):
    valueChanged = Signal(tuple)

    def __init__(self, color: RGB = None, parent=None):
        super().__init__(parent)

        self._rgb = color if color is not None else Color.WHITE

        # allows for selecting in style formatting
        self.setObjectName("ColorButton")

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
        text_r, text_g, text_b = Util.contrast_color((r, g, b))
       
        self.setText(f"{r}, {g}, {b}")
        if not self.isEnabled():
            r, g, b = Color.DARK_GRAY
            text_r, text_g, text_b = Color.LIGHTISH_GRAY

        # color bg + text by color
        self.setStyleSheet(
            f"""
            QPushButton#ColorButton {{
                background-color: rgb({r}, {g}, {b});
                color: rgb({text_r}, {text_g}, {text_b});
            }}
            """
        )

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self._copy_color)
        menu.addAction(copy_action)

        clipboard_text = QApplication.clipboard().text()
        pasted_color = self._parse_clipboard_color(clipboard_text)

        # only enable paste button if current clipboard contents are a valid color
        paste_action = QAction("Paste", self)
        paste_action.setEnabled(pasted_color is not None)
        paste_action.triggered.connect(self._paste_color)
        menu.addAction(paste_action)

        menu.exec(event.globalPos())

    def _copy_color(self):
        r, g, b = self._rgb
        QApplication.clipboard().setText(f"{r}, {g}, {b}")

    def _paste_color(self):
        clipboard_text = QApplication.clipboard().text()
        color = self._parse_clipboard_color(clipboard_text)

        if color is None:
            return

        self._set_color_and_emit(color)

    def _parse_clipboard_color(self, text: str) -> RGB | None:
        text = text.strip()

        # expected format: "r, g, b"

        if len(text) > 20:
            # too big, probably not what we're expecting
            return None

        parts = [part.strip() for part in text.split(",")]

        if len(parts) != 3:
            return None

        try:
            r, g, b = (int(part) for part in parts)
        except ValueError:
            return None

        if not all(0 <= value <= 255 for value in (r, g, b)):
            return None

        return (r, g, b)

    def _set_color_and_emit(self, color: RGB):
        self._rgb = color
        self.refresh()
        self.valueChanged.emit(self._rgb)

    def _pick_color(self):
        color = QColorDialog.getColor(
            QUtil.rgb_to_qcolor(self._rgb),
            self,
            "Choose color",
        )

        if color.isValid():
            self._set_color_and_emit(QUtil.qcolor_to_rgb(color))