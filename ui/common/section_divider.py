from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QSizePolicy
from PySide6.QtCore import Qt

class SectionDivider(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)

        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                font-weight: 600;
            }
        """)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet("color: #555555;")
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 4)
        layout.setSpacing(8)
        layout.addWidget(label, 0, Qt.AlignVCenter)
        layout.addWidget(line, 1, Qt.AlignVCenter)