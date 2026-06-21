from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QPushButton
)
from common import RGB

class QUtil:
    def __new__(cls):
        raise TypeError("QUtil is static")
    
    # -- Color helpers --
    @staticmethod
    def rgb_to_qcolor(rgb: RGB, alpha: int = 255) -> QColor:
        return QColor(*rgb, a=alpha)

    @staticmethod
    def qcolor_to_rgb(color: QColor) -> RGB:
        return (color.red(), color.green(), color.blue())
    
    # -- Widget helpers --
    @staticmethod
    def color_button(button: QPushButton, bg_color: RGB):
        r, g, b = bg_color
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb({r}, {g}, {b});
                color: {'black' if (r*0.299 + g*0.587 + b*0.114) > 160 else 'white'};
            }}
            """
        )

