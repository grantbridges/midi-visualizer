from pathlib import Path
import platform
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
    def is_packaged_app() -> bool:
        return getattr(sys, "frozen", False)
    
    @staticmethod
    def get_root_app_dir() -> Path:
        if FileUtil.is_packaged_app():
            return Path(sys._MEIPASS)

        # up two levels to root project directory
        # a little hacky but uhh whatever
        return Path(__file__).resolve().parent.parent
    
    @staticmethod
    def get_assets_dir() -> Path:
        return FileUtil.get_root_app_dir() / "assets" 
    
    @staticmethod
    def get_logs_dir() -> Path:
        return Path(FileUtil.get_app_data_dir()) / "logs"

    @staticmethod
    def get_ffmpeg_path() -> str:
        '''
        Pulls ffmpeg executable from proper location based on whether running
        in debug or release, and on OS/arch
        '''
        exe_name = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"

        path = FileUtil.get_root_app_dir()

        if FileUtil.is_packaged_app():
            path = path / "bin" / exe_name
        else:
            path = path / "third-party" / "ffmpeg"

            if sys.platform == "win32":
                path = path / "win32-x64" / exe_name
            elif sys.platform == "darwin":
                arch = platform.machine()
                if arch == "arm64":
                    path = path / "darwin-arm64" / exe_name
                elif arch == "x86_64":
                    path = path / "darwin-x64" / exe_name
            else:
                raise RuntimeError(f"Unsupported platform: {sys.platform}")

        if not path.exists():
            raise FileNotFoundError(f"FFmpeg executable not found: {path}")

        return str(path)
    
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