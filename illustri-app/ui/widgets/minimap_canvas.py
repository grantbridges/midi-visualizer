from uuid import UUID
import time
from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtGui import QBrush, QFont, QImage, QPainter, QPen
from PySide6.QtCore import QRect, QRectF, Qt, Signal
from common import Const, Color
from media import image_provider
from models import VisConfig, user_settings, BackgroundMode
from render import MidiRenderUtil
from utility import QUtil, Util

import logging
logger = logging.getLogger("MinimapCanvas")

MINIMAP_HEIGHT = 32

class MinimapCanvas(QWidget):
    '''
    Shows a visual preview of the entire midi track with a cursor
    showing playback position and allowing interaction
    '''
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

        # cache the preview data (background, notes) and only redraw
        # when model changes or screen is resized
        self._preview_cache: QImage | None = None
        self._preview_cache_dirty: bool = True

        self.is_dragging: bool = False

        self.setFixedHeight(MINIMAP_HEIGHT)

    # parent API
    def refresh(self, current_time: float, vis_config: VisConfig, start_time: float, end_time: float, pitch_min: int, pitch_max: int):
        self.current_time = current_time
        self.vis_config = vis_config
        self.start_time = start_time
        self.end_time = end_time
        self.pitch_min = pitch_min
        self.pitch_max = pitch_max

        self.update() # queues paint event

    def set_dirty(self):
        self._preview_cache_dirty = True

    def is_slider_down(self) -> bool:
        return self.is_dragging
    
    # events
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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        try:
            if self._preview_cache_dirty or self._preview_cache is None:
               self._rebuild_preview_cache()
            
            # draw preview data
            rect = self.rect()
            painter.drawImage(rect.x(), rect.y(), self._preview_cache)
            #self._draw_preview_data(painter, self.rect())

            # draw cursor
            self._draw_cursor(painter)

        except Exception as e:
            logger.error(f"Minimap render failed: {str(e)}")

    # draw helpers
    def _rebuild_preview_cache(self):       
        rect = self.rect()

        # set up QImage for cache
        self._preview_cache = QImage(
            rect.width(),
            rect.height(),
            QImage.Format_ARGB32_Premultiplied,
        )

        painter = QPainter(self._preview_cache)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        self._draw_preview_data(painter, rect)

        painter.end()

        self._preview_cache_dirty = False

    def _draw_preview_data(self, painter: QPainter, rect: QRect):
        # fill background
        painter.fillRect(rect, QUtil.rgb_to_qcolor(self.vis_config.bg_color))
        
        # iterate backwards so first groups are drawn on top
        track_groups = self.vis_config.get_visible_track_groups()[::-1]

        for tg in track_groups:
            tracks = self.vis_config.get_tracks_by_group_id(tg.group_id)

            painter.setPen(QPen(QUtil.rgb_to_qcolor(tg.color), 1))
            
            # draw notes for each track in group
            for t in tracks:
                for n in t.notes:
                    x1 = self._get_x_pos_from_time(n.start)
                    x2 = self._get_x_pos_from_time(n.end)
                    y = MidiRenderUtil.pitch_to_y(
                        n.pitch + tg.pitch_offset, 
                        self.pitch_min, 
                        self.pitch_max, 
                        rect, 
                        self.vis_config.vertical_padding_ratio, 
                        self.vis_config.vertical_offset_ratio
                    )
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
        fill_color = QUtil.rgb_to_qcolor(Color.WHITE)
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
