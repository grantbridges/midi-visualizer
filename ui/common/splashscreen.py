from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtWidgets import QSplashScreen
from PySide6.QtGui import QFont, QPainter, QPixmap
from PySide6.QtCore import QSize, Qt
from common import Color, Const
import build_info
from utility import QUtil, FileUtil

class SplashScreen(QSplashScreen):
    def mousePressEvent(self, event):
        # ignore mouse events
        event.ignore()

    @staticmethod
    def create():
        # grab screen DPR for properly scaling splash to minimize blurriness/scaling artifacts
        screen = QApplication.primaryScreen()
        dpr = screen.devicePixelRatio() if screen else 1.0

        # load in splash screen image and grab dimenions to set up pixmap
        str_filepath = str(FileUtil.get_assets_dir() / "illustri-splash-screen.png")
        img = QPixmap(str_filepath)
        img_width = 720
        img_height = 405

        # scale pixmap for screen
        pixmap = QPixmap(int(img_width * dpr), int(img_height * dpr))
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.drawPixmap(0, 0, img_width, img_height, img)

        painter.setPen(QUtil.rgb_to_qcolor(Color.SPLASH_SCREEN_TEXT))
        painter.setFont(QFont(Const.PRIMARY_FONT, QUtil.scale_font_size(12)))

        rect = pixmap.rect()
        rect.setSize(QSize(img_width, img_height))

        # draw version text
        painter.drawText(
            rect.adjusted(5, 0, 0, -5),
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
            f"Version {build_info.VERSION} - Built {build_info.BUILD_DATE}",
        )

        # draw organization text
        painter.drawText(
            rect.adjusted(0, 0, -5, -5),
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