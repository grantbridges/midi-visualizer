from typing import Tuple
from PySide6.QtGui import QColor

class QtUtil:
    def __new__(cls):
        raise TypeError("QtUtil is static")

    @staticmethod
    def rgb_to_qcolor(rgb: Tuple[int, int, int]) -> QColor:
        return QColor(*rgb)

    @staticmethod
    def qcolor_to_rgb(color: QColor) -> Tuple[int, int, int]:
        return (color.red(), color.green(), color.blue())