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

            # draw background
            self._draw_background(painter)

            # draw midi notes
            self._draw_notes(painter)

            # draw cursor
            self._draw_cursor(painter)


        except Exception as e:
            logger.error(f"Minimap render failed: {str(e)}")

    # draw helpers
    def _draw_background(self, painter: QPainter):
        rect = self._get_preview_rect()
        painter.fillRect(rect, QUtil.rgb_to_qcolor(self.vis_config.bg_color))

    def _draw_notes(self, painter: QPainter):
        rect = self._get_preview_rect()
        # iterate backwards so first groups are drawn on top
        track_groups = self.vis_config.get_visible_track_groups()[::-1]

        for tg in track_groups:
            tracks = self.vis_config.get_tracks_by_group_id(tg.group_id)

            painter.setPen(QPen(QUtil.rgb_to_qcolor(tg.color), 1))
            
            for t in tracks:
                for n in t.notes:
                    x1 = self._get_x_pos_from_time(n.start)
                    x2 = self._get_x_pos_from_time(n.end)
                    y = MidiRenderUtil.pitch_to_y(n.pitch, self.pitch_min, self.pitch_max, rect, 0, 0.5)
                    painter.drawLine(x1, y, x2, y)

    def _draw_cursor(self, painter: QPainter):
        rect = self.rect()
        cursor_x = self._get_x_pos_from_time(self.current_time)

        cursor_width = 3
        cursor_border_thickness = 1
        cursor_rect = QRectF(
            cursor_x - cursor_width / 2,
            cursor_border_thickness,
            cursor_width,
            rect.height() - 2 * cursor_border_thickness,
        )

        border_color = QUtil.rgb_to_qcolor(Color.BLACK)
        fill_color = QUtil.rgb_to_qcolor(Color.LIGHT_GRAY)
        painter.setPen(QPen(border_color, cursor_border_thickness))
        painter.setBrush(QBrush(fill_color))
        painter.drawRect(cursor_rect)

    # helpers
    def _get_time_from_x_pos(self, x_pos: int) -> float:
        ratio = x_pos / self.rect().width()
        new_time = ratio * (self.end_time - self.start_time)
        new_time = Util.clamp(new_time, self.start_time, self.end_time)
        return new_time
    
    def _get_x_pos_from_time(self, time: float) -> int:
        if self.start_time == self.end_time:
            return 0
        
        ratio = (time - self.start_time) / (self.end_time - self.start_time)
        x_pos = int(ratio * self.rect().width())
        return x_pos
    
    def _get_y_pos_from_pitch(self, pitch: int) -> int:
        height = self.rect().height()
        if self.pitch_min == self.pitch_max:
            return height / 2

        ratio = (pitch - self.pitch_min) / (self.pitch_max - self.pitch_min)
        return ratio * height
        
    def _get_preview_rect(self) -> QRect:
        '''
        A height-reduced rect for the actual midi minimap drawing. The cursor 
        is the only thing that gets the full canvas height.
        '''
        preview_padding = 4
        return self.rect().adjusted(
            0, preview_padding, 
            0, -preview_padding
        )
