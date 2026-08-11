from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen
from common import Color
from utility import QUtil


class DropOverlay(QWidget):
    """Semi-transparent overlay shown while a valid file is being dragged over the window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Let mouse/drag events pass through to the parent underneath
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        # Needed so paintEvent's alpha actually renders as translucent
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label = QLabel("Drop file to load", self)
        self.label.setAlignment(Qt.AlignCenter)
        r, g, b = Color.ILLUSTRI_TEXT
        self.label.setStyleSheet(f"color: rgb({r}, {g}, {b}); font-size: 18px; font-weight: bold;")

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        # hide until parent decides to show
        self.hide()

    def set_text(self, text: str):
        self.label.setText(text)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        padding = 15 # px
        rect = self.rect().adjusted(padding, padding, -padding, -padding)

        painter.fillRect(rect, QUtil.rgb_to_qcolor(Color.BLACK, 100))

        pen = QPen(QColor(255, 255, 255, 200))
        pen.setWidth(3)
        pen.setStyle(Qt.DotLine)
        pen.setColor(QUtil.rgb_to_qcolor(Color.ILLUSTRI_TEXT))
        painter.setPen(pen)
        painter.drawRect(rect)

        super().paintEvent(event)