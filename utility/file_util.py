from pathlib import Path

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
    def get_logs_dir() -> Path:
        return Path(FileUtil.get_app_data_dir()) / "logs"
    
    @staticmethod
    def get_unique_path(path: Path) -> Path:
        '''
        For a given path, add numbers to the end of the file name
        until it is unique in its directory. Used for unique file
        generation.
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