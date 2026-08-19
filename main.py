import time
import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from common import Const
from ui import MainWindow
from ui.common import SplashScreen
from utility import LogUtil, QUtil, FileUtil
from models import user_settings
from media import audio_provider, video_provider, image_provider
import build_info

logger = logging.getLogger("Main")

SPLASH_SCREEN_SHOW_TIME_SEC = 2

# create main window and start
def main():
    app = QApplication(sys.argv)
    app.setApplicationName(Const.APP_NAME)
    app.setWindowIcon(QIcon(str(FileUtil.get_assets_dir() / "icons" / "illustri.ico")))

    LogUtil.configure_logging()
    logger.info("%s started - version %s, built %s", Const.APP_NAME, build_info.VERSION, build_info.BUILD_DATE)

    QUtil.apply_dark_theme(app)
    QUtil.load_fonts()

    # show splash screen
    splash = SplashScreen.create()
    app.processEvents()
    
    user_settings.load()

    audio_provider.init()
    video_provider.init()
    image_provider.init()

    time.sleep(SPLASH_SCREEN_SHOW_TIME_SEC) # block on splash screen for a moment

    #def show_main_window():
    window = MainWindow()
    window.show()
    splash.finish(window)

    exit_code = app.exec()
    logger.info("%s shutting down (code %d)", Const.APP_NAME, exit_code)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()