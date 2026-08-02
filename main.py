from pathlib import Path
import time
import sys
import logging
from PySide6.QtWidgets import QApplication
from common import Const
from ui import MainWindow
from ui.common import SplashScreen
from utility import LogUtil, QUtil
from models import user_settings
from media import audio_provider, video_provider, image_provider
import build_info

logger = logging.getLogger("Main")

SPLASH_SCREEN_MIN_TIME_MS = 2000

# create main window and start
def main():
    app = QApplication(sys.argv)
    QUtil.apply_dark_theme(app)
    app.setApplicationName(Const.APP_NAME)

    LogUtil.configure_logging()
    logger.info("%s started - version %s, built %s", Const.APP_NAME, build_info.VERSION, build_info.BUILD_DATE)

    # show splash screen
    splash = SplashScreen.create()
    app.processEvents()
    
    user_settings.load()

    audio_provider.init()
    video_provider.init()
    image_provider.init()

    time.sleep(2) # block on splash screen for a moment

    #def show_main_window():
    window = MainWindow()
    window.show()
    splash.finish(window)

    exit_code = app.exec()
    logger.info("%s shutting down (code %d)", Const.APP_NAME, exit_code)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()