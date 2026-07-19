from PySide6.QtWidgets import QSplashScreen
from PySide6.QtWidgets import QSplashScreen
from PySide6.QtGui import QFont, QPainter, QPixmap
from PySide6.QtCore import Qt

from common import Color, Const
from utility import QUtil

class SplashScreen(QSplashScreen):
    def mousePressEvent(self, event):
        # ignore mouse events
        event.ignore()

    @staticmethod
    def create():
        pixmap = QPixmap("assets/illustri-splash-screen.png")
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QUtil.rgb_to_qcolor(Color.SPLASH_SCREEN_TEXT))
        painter.setFont(QFont("Arial", 12))

        painter.drawText(
            pixmap.rect().adjusted(5, 0, 0, -5),
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
            f"Version {Const.VERSION} - Built {Const.BUILD_DATE}",
        )

        painter.drawText(
            pixmap.rect().adjusted(0, 0, -5, -5),
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
            f"by {Const.ORG_NAME}",
        )
        painter.end()

        splash = SplashScreen(pixmap)
        splash.show()
        splash.raise_()
        splash.activateWindow()
        splash.repaint()

        return splash