from pathlib import Path
import sys

from PySide6.QtCore import QStandardPaths

class FileUtil:
    def __new__(cls):
        raise TypeError("FileUtil is static")

    @staticmethod
    def get_app_data_dir():
        return QStandardPaths.writableLocation(
            QStandardPaths.AppDataLocation
        )
    
    @staticmethod
    def get_root_app_dir() -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys._MEIPASS)
    
        return Path(__file__).resolve().parent.parent
    
    @staticmethod
    def get_assets_dir() -> Path:
        return FileUtil.get_root_app_dir() / "assets" 
    
    @staticmethod
    def get_logs_dir() -> Path:
        return Path(FileUtil.get_app_data_dir()) / "logs"
    
    @staticmethod
    def get_unique_path(path: Path) -> Path:
        '''
        For a given path, add numbers to the end of the file name until it's
        unique in its directory. Used to ensure unique file generation.
        '''
        if not path.exists():
            return path

        # split path into relevant parts
        parent = path.parent
        stem = path.stem
        suffix = path.suffix

        counter = 1
        while True:
            # append (counter) to file name
            check_path = parent / f"{stem} ({counter}){suffix}"

            if not check_path.exists():
                return check_path

            counter += 1