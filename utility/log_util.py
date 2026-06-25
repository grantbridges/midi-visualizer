import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from common import Const

import logging

from utility.file_util import FileUtil

# utility formatter class to shorten the logging names
class ShortLevelFormatter(logging.Formatter):
    LEVEL_MAP = {
        "CRITICAL": "CRT",
        "ERROR": "ERR",
        "WARNING": "WRN",
        "INFO": "INF",
        "DEBUG": "DBG",
        "TRACE": "TRC",
    }

    def format(self, record):
        original_levelname = record.levelname
        record.levelname = self.LEVEL_MAP.get(record.levelname, record.levelname)
        try:
            return super().format(record)
        finally:
            record.levelname = original_levelname

class LogUtil:
    def __new__(cls):
        raise TypeError("LogUtil is static")

    @staticmethod
    def configure_logging(
        debug_enabled: bool = False,
        retention_days: int = 14,
    ):
        log_dir = Path(FileUtil.get_app_data_dir()) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_level = logging.DEBUG if debug_enabled else logging.INFO

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers if configure_logging is called more than once
        logger.handlers.clear()

        # set up logging template
        formatter = ShortLevelFormatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # set up rolling log file handler
        file_handler = TimedRotatingFileHandler(
            filename=log_dir / f"{Const.APP_ALT_NAME}.log",
            when="midnight",
            interval=1,
            backupCount=retention_days,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        file_handler.suffix = "%Y-%m-%d"

        logger.addHandler(file_handler)

        # set up console handling
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        