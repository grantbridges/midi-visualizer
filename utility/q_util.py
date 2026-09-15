import sys
from PySide6.QtGui import QColor, QCursor, QFont, QFontDatabase, QPalette, Qt
from PySide6.QtWidgets import QApplication, QComboBox, QLabel, QLineEdit, QMenu, QProxyStyle, QPushButton, QStyle, QTableWidget, QToolTip
from PySide6.QtCore import QObject, QEvent, QPoint
from common import RGB, Color
from common.constants import Const
from utility.file_util import FileUtil

import logging
logger = logging.getLogger("QUtil")

class QUtil:
    def __new__(cls):
        raise TypeError("QUtil is static")
    
    # -- Theme helpers --

    def init_app_styles(app: QApplication):
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

        # Font
        #app.setFont(QFont(Const.PRIMARY_FONT))

        # Apply some general app styling
        class _style(QProxyStyle):
            def styleHint(self, hint, option=None, widget=None, returnData=None):
                # slightly faster tooltip delay response
                if hint == QStyle.StyleHint.SH_ToolTip_WakeUpDelay:
                    return 200 # ms, default 700
                return super().styleHint(hint, option, widget, returnData)

            # def polish(self, widget):
            #     # manually set font & default size on all widgets
            #     super().polish(widget)
            #     default_font_widgets = (QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QMenu)
            #     if isinstance(widget, default_font_widgets) and not widget.testAttribute(Qt.WidgetAttribute.WA_SetFont):
            #         widget.setFont(QFont(Const.PRIMARY_FONT, QUtil.scale_font_size(12)))

        class _tooltip(QLabel):
            def __init__(self):
                super().__init__(None, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
                self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                #self.setWordWrap(True)
                #self.setMaximumWidth(250)
                self.setStyleSheet(f"""
                    QLabel {{
                        background-color: rgba(38, 38, 38, 0.75);
                        color: #ccc;
                        border: 1px solid #222;
                        padding: 3px 4px;
                        border-radius: 3px;
                        font-family: {Const.PRIMARY_FONT};
                        font-size: {QUtil.scale_font_size(10)}pt;
                    }}
                """)

        class _tooltipFilter(QObject):
            def __init__(self, parent=None):
                super().__init__(parent)
                self._tip = _tooltip()

            def eventFilter(self, obj, event):
                if event.type() == QEvent.Type.ToolTip:
                    text = obj.toolTip()
                    if text:
                        self._tip.setText(text)
                        self._tip.adjustSize()
                        pos = QCursor.pos() + QPoint(10, 10) # offset
                        self._tip.move(pos)
                        self._tip.show()
                    else:
                        self._tip.hide()
                    return True
                if event.type() in (QEvent.Type.Leave, QEvent.Type.MouseButtonPress):
                    self._tip.hide()
                return super().eventFilter(obj, event)

        app.setStyle(_style(app.style()))
        app.installEventFilter(_tooltipFilter(app))

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

