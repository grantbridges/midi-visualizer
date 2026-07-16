from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from common import Const

import logging

from utility.file_util import FileUtil

SHORT_LEVEL_MAP = {
    "CRITICAL": "CRT",
    "ERROR": "ERR",
    "WARNING": "WRN",
    "INFO": "INF",
    "DEBUG": "DBG",
}

# utility formatter class to shorten the logging names
class ShortLevelFormatter(logging.Formatter):
    def format(self, record):
        original_levelname = record.levelname
        record.levelname = SHORT_LEVEL_MAP.get(record.levelname, record.levelname)
        try:
            return super().format(record)
        finally:
            record.levelname = original_levelname

# utility formatter class for console to color logging levels
class ColorShortLevelFormatter(logging.Formatter):
    COLORS = {
        "DBG": "\033[36m",  # cyan
        "INF": "\033[32m",  # green
        "WRN": "\033[33m",  # yellow
        "ERR": "\033[31m",  # red
        "CRT": "\033[35m",  # magenta
    }

    RESET = "\033[0m"

    def format(self, record):
        original_levelname = record.levelname
        short_level = SHORT_LEVEL_MAP.get(record.levelname, record.levelname)

        color = self.COLORS.get(short_level, "")
        record.levelname = f"{color}{short_level}{self.RESET}" if color else short_level

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
        log_dir = FileUtil.get_logs_dir()
        log_dir.mkdir(parents=True, exist_ok=True)

        log_level = logging.DEBUG if debug_enabled else logging.INFO

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers if configure_logging is called more than once
        logger.handlers.clear()

        # set up logging templates
        fmt_template = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        datemt_template = "%Y-%m-%d %H:%M:%S"

        file_formatter = ShortLevelFormatter(fmt=fmt_template, datefmt=datemt_template)

        # set up rolling log file handler
        file_handler = TimedRotatingFileHandler(
            filename=log_dir / f"{Const.APP_ALT_NAME}.log",
            when="midnight",
            interval=1,
            backupCount=retention_days,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)
        file_handler.suffix = "%Y-%m-%d"

        logger.addHandler(file_handler)

        # set up console handling
        console_formatter = ColorShortLevelFormatter(fmt=fmt_template, datefmt=datemt_template)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    @staticmethod
    def zip_logs_to_dir(output_dir: Path):
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_zip = FileUtil.get_unique_path(Path(output_dir) / f"{Const.APP_ALT_NAME}-logs-{date_str}.zip")

        # grab all log files from log dir
        log_files = [
            path for path in FileUtil.get_logs_dir().glob(f"{Const.APP_ALT_NAME}.log*")
            if path.is_file()
        ]

        with ZipFile(output_zip, "w", compression=ZIP_DEFLATED) as zip_file:
            for path in log_files:
                zip_file.write(path, arcname=path.name)
        