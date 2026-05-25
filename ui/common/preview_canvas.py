from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QFont, QPainter, QPen
from PySide6.QtCore import QRect
from common import Const, Color
from models import VisConfig
from render import MidiRenderUtil
from utility import QUtil

class PreviewCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # set on each refresh by parent so always up to date
        # (cached as members for paintEvent to access)
        self.vis_config: VisConfig = None
        self.current_time: float = 0.0 # sec
        self.pitch_min: int = 0
        self.pitch_max: int = 0

    def refresh(self, current_time: float, vis_config: VisConfig, pitch_min: int, pitch_max: int):
        self.current_time = current_time
        self.vis_config = vis_config
        self.pitch_min = pitch_min
        self.pitch_max = pitch_max

        self.update() # queues paint event

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        MidiRenderUtil.draw_frame(
            painter, 
            self.current_time, 
            self.vis_config,
            self.pitch_min, 
            self.pitch_max, 
            self.rect()
        )

        # draw text time display
        color = QUtil.rgb_to_qcolor(Color.WHITE)
        color.setAlpha(200)
        font = QFont(Const.PRIMARY_FONT, 12)
        painter.setPen(color)
        painter.setFont(font)
        m = s = 0
        sign = "-" if self.current_time < 0 else ""
        t_abs = abs(self.current_time)
        m, s = divmod(int(t_abs), 60)
        painter.drawText(QRect(5, 5, 100, 100), f'{sign}{m:02d}:{s:02d}')