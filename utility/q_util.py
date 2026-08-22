import sys
from PySide6.QtGui import QColor, QFontDatabase, QPalette, Qt
from PySide6.QtWidgets import QApplication
from common import RGB, Color
from utility.file_util import FileUtil

import logging
logger = logging.getLogger("QUtil")

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
        palette.setColor(QPalette.Highlight, QUtil.rgb_to_qcolor(Color.ILLUSTRI_TEXT_DARKER))
        palette.setColor(QPalette.HighlightedText, QUtil.rgb_to_qcolor(Color.DARKER_GRAY))
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

    @staticmethod
    def load_fonts():
        loaded_fonts: list[str] = []
        for font_path in FileUtil.get_fonts_dir().glob("*.ttf"):
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id == -1:
                logger.warning(f"Failed to load font {font_path}")
                continue

            family_list = QFontDatabase.applicationFontFamilies(font_id)
            if family_list:
                loaded_fonts.append(family_list[0])

        logger.info(f"Load Fonts | Loaded {len(loaded_fonts)} font(s): {", ".join(loaded_fonts)}")

    # -- Color helpers --
    @staticmethod
    def rgb_to_qcolor(rgb: RGB, alpha: int = 255) -> QColor:
        return QColor(*rgb, a=alpha)

    @staticmethod
    def qcolor_to_rgb(color: QColor) -> RGB:
        return (color.red(), color.green(), color.blue())

    @staticmethod
    def scale_font_size(base_pt: float) -> float:
        if sys.platform == "darwin":
            return base_pt

        return base_pt * (72 / 96) # ~0.75x on Windows

