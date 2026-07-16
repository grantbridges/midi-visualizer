from pathlib import Path
import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QElapsedTimer, QTimer
from common import Const
from ui import MainWindow
from ui.common import SplashScreen
from utility import LogUtil, QUtil
from models import user_settings
from media import audio_provider, video_provider, image_provider

logger = logging.getLogger("Main")

SPLASH_SCREEN_MIN_TIME_MS = 2000

# create main window and start
def main():
    app = QApplication(sys.argv)
    QUtil.apply_dark_theme(app)
    app.setApplicationName(Const.APP_NAME)

    logger.info("%s started", Const.APP_NAME)

    # show splash screen (for a minimum amount of time)
    splash = SplashScreen.create()
    splash_timer = QElapsedTimer()
    splash_timer.start()

    app.processEvents()

    # startup work happens after event loop has started
    LogUtil.configure_logging(
        debug_enabled=True,
        retention_days=14,
    )

    user_settings.load()

    audio_provider.init()
    video_provider.init()
    image_provider.init()


    def show_main_window():
        window = MainWindow()
        window.show()
        splash.finish(window)

    # hide splash screen after elapsed time
    elapsed_ms = splash_timer.elapsed()
    remaining_ms = max(0, SPLASH_SCREEN_MIN_TIME_MS - elapsed_ms)
    QTimer.singleShot(remaining_ms, show_main_window)

    exit_code = app.exec()
    logger.info("%s shutting down (code %d)", Const.APP_NAME, exit_code)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()