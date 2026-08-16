from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QLabel

class WidgetUtil:
    '''
    Utility for creating some common types of special case widgets
    '''
    def __new__(cls):
        raise TypeError("WidgetUtil is static")
        
    @staticmethod
    def hint_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setForegroundRole(QPalette.PlaceholderText)

        font = label.font()
        font.setPointSizeF(font.pointSizeF() * 0.9)
        label.setFont(font)

        return label