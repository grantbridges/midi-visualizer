from PySide6.QtCore import QStandardPaths

class FileUtil:
    def __new__(cls):
        raise TypeError("FileUtil is static")

    @staticmethod
    def get_app_data_dir():
        return QStandardPaths.writableLocation(
            QStandardPaths.AppDataLocation
        )