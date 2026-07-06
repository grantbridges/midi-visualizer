from pathlib import Path
import sys
import logging
from PySide6.QtWidgets import QApplication
from common import Const
from ui import MainWindow
from utility import LogUtil, QUtil
from models import user_settings
from media import audio_provider, video_provider, image_provider

logger = logging.getLogger("Main")

# create main window and start
def main():
    app = QApplication(sys.argv)
    QUtil.apply_dark_theme(app)
    app.setApplicationName(Const.APP_NAME)

    # set up logger after app is created
    LogUtil.configure_logging(
        debug_enabled=True,
        retention_days=14
    )

    logger.info("%s started", Const.APP_NAME)

    # initial load of user settings
    user_settings.load()

    # initialize global media providers
    audio_provider.init()
    video_provider.init()
    image_provider.init()

    # start UI
    window = MainWindow()
    window.show()

    def run_app():
        exit_code = app.exec()
        logger.info("%s shutting down (code %d)", Const.APP_NAME, exit_code)
        return exit_code

    sys.exit(run_app())

if __name__ == "__main__":
    main()