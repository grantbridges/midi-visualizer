import time
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QFont, QPainter, QColor, QPen
from PySide6.QtCore import QRect, QTimer, Qt
from common import Const, Color
from models import VisConfig
from render import MidiRenderer
from utility import QUtil

class PreviewWidget(QWidget):
    def __init__(self, vis_config: VisConfig, parent=None):
        super().__init__(parent)
        self.vis_config: VisConfig = vis_config

        self.midi_renderer: MidiRenderer = MidiRenderer(self.vis_config)

        self.current_time: float = 0.0 # sec

    def on_show(self):
        self.midi_renderer.set_dimensions(self.width(), self.height())
    
    def tick(self, current_time):
        self.current_time = current_time
        self.update() # queues paint event

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.midi_renderer.draw(painter, self.current_time)

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