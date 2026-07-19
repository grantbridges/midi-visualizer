from PySide6.QtGui import QColor, QPalette, Qt
from PySide6.QtWidgets import (
    QApplication,
    QPushButton
)
from common import RGB

class QUtil:
    def __new__(cls):
        raise TypeError("QUtil is static")
    
    # -- Theme helpers --

    def apply_dark_theme(app: QApplication):
        '''
        Utility to force style & base colors throughout application
        Allows consistent color/styling between Mac and OS (always in dark mode)
        '''
        app.setStyle("Fusion")

        palette = QPalette()

        # Normal colors
        palette.setColor(QPalette.Window, QColor(37, 37, 37))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor(90, 120, 180))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        palette.setColor(QPalette.PlaceholderText, QColor(160, 160, 160))

        # Disabled colors
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(120, 120, 120))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(120, 120, 120))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(120, 120, 120))
        palette.setColor(QPalette.Disabled, QPalette.PlaceholderText, QColor(100, 100, 100))

        palette.setColor(QPalette.Disabled, QPalette.Base, QColor(38, 38, 38))
        palette.setColor(QPalette.Disabled, QPalette.Button, QColor(38, 38, 38))
        palette.setColor(QPalette.Disabled, QPalette.Window, QColor(37, 37, 37))

        palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(55, 55, 55))
        palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(130, 130, 130))

        app.setPalette(palette)
    

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

