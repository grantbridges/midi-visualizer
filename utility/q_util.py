from PySide6.QtGui import QColor
from common import RGB

class QUtil:
    def __new__(cls):
        raise TypeError("QUtil is static")
    
    @staticmethod
    def rgb_to_qcolor(rgb: RGB, alpha: int = 255) -> QColor:
        return QColor(*rgb, a=alpha)

    @staticmethod
    def qcolor_to_rgb(color: QColor) -> RGB:
        return (color.red(), color.green(), color.blue())