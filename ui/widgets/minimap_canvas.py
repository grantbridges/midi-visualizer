from uuid import UUID

from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtGui import QBrush, QFont, QPainter, QPen
from PySide6.QtCore import QRect, QRectF, Qt, Signal
from common import Const, Color
from models import VisConfig, user_settings
from render import MidiRenderUtil
from utility import QUtil, Util

import logging
logger = logging.getLogger("MinimapCanvas")

class MinimapCanvas(QWidget):
    valueChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        # set on each refresh by parent so always up to date
        # (cached as members for paintEvent to access)
        self.vis_config: VisConfig = None
        self.current_time: float = 0.0 # sec
        self.start_time: float = 0.0 # sec
        self.end_time: float = 1.0 # sec
        self.pitch_min: int = 0
        self.pitch_max: int = 0

        self.is_dragging: bool = False

    def refresh(self, current_time: float, vis_config: VisConfig, start_time: float, end_time: float, pitch_min: int, pitch_max: int):
        self.current_time = current_time
        self.vis_config = vis_config
        self.start_time = start_time
        self.end_time = end_time
        self.pitch_min = pitch_min
        self.pitch_max = pitch_max

        self.update() # queues paint event

    def isSliderDown(self) -> bool:
        return self.is_dragging

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True

            # calculate time from position and notify parent
            x = event.position().x()
            new_time = self._get_time_from_x_pos(x)
            self.valueChanged.emit(new_time)

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            # calculate time from position and notify parent
            x = event.position().x()
            new_time = self._get_time_from_x_pos(x)
            self.valueChanged.emit(new_time)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_dragging:
                self.is_dragging = False

                # calculate time from position and notify parent for final position
                x = event.position().x()
                new_time = self._get_time_from_x_pos(x)
                self.valueChanged.emit(new_time)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        try:
            rect = self.rect()
            preview_padding = 4
            preview_rect = self.rect().adjusted(
                0, 
                preview_padding, 
                0, 
                -preview_padding
            )

            # draw background
            painter.fillRect(preview_rect, QUtil.rgb_to_qcolor(self.vis_config.bg_color))

            # draw midi bars
            # TODO

            # draw cursor
            if self.end_time != self.start_time:
                time_ratio = (self.current_time - self.start_time) / (self.end_time - self.start_time)
                cursor_x = time_ratio * rect.width()

                cursor_width = 3
                cursor_border_thickness = 1

                cursor_rect = QRectF(
                    cursor_x - cursor_width / 2,
                    cursor_border_thickness,
                    cursor_width,
                    rect.height() - 2 * cursor_border_thickness,
                )

                border_color = QUtil.rgb_to_qcolor(Color.BLACK)
                fill_color = QUtil.rgb_to_qcolor(Color.WHITE)
                painter.setPen(QPen(border_color, cursor_border_thickness))
                painter.setBrush(QBrush(fill_color))
                painter.drawRect(cursor_rect)


        except Exception as e:
            logger.error(f"Minimap render failed: {str(e)}")

    # helpers
    def _get_time_from_x_pos(self, x_pos: float) -> float:
        ratio = x_pos / self.rect().width()
        new_time = ratio * (self.end_time - self.start_time)
        new_time = Util.clamp(new_time, self.start_time, self.end_time)
        return new_time