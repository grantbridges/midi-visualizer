from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QFont, QPainter, QPen
from PySide6.QtCore import QRect, Qt
from common import Const, Color
from models import VisConfig, user_settings
from render import MidiRenderUtil
from utility import QUtil, Util

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

        MidiRenderUtil.draw_background(
            painter, 
            self.current_time, 
            self.vis_config,
            self.rect()
        )

        self._draw_guides(painter)
        self._draw_text(painter)

        MidiRenderUtil.draw_notes(
            painter, 
            self.current_time, 
            self.vis_config,
            self.pitch_min, 
            self.pitch_max, 
            self.rect()
        )

    def _draw_guides(self, painter: QPainter):
        vert_padding = self.vis_config.vertical_padding_ratio * self.rect().height() / 2
        vert_offset = self.vis_config.vertical_offset_ratio * self.rect().height() / 2
        rect = self.rect()

        # positions
        y_center = self.rect().height() / 2 + vert_offset
        y_min = vert_padding + vert_offset
        y_max = self.rect().height() - vert_padding + vert_offset

        # draw pitches
        color = QUtil.rgb_to_qcolor(Util.invert_color(self.vis_config.bg_color))
        color.setAlpha(30)
        pen = QPen(color)
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(1)
        painter.setPen(pen)        

        if user_settings.show_pitches:
            pitch_range = self.pitch_max - self.pitch_min
            if pitch_range > 0:
                for pitch in range(self.pitch_min, self.pitch_max + 1):
                    y = MidiRenderUtil.pitch_to_y(
                        pitch,
                        self.pitch_min,
                        self.pitch_max,
                        rect,
                        self.vis_config.vertical_padding_ratio,
                        self.vis_config.vertical_offset_ratio,
                    )

                    painter.drawLine(0, y, rect.width(), y)

        if user_settings.show_guides:
            # draw vertical padding guides
            color.setAlpha(200)
            pen = QPen(color)
            pen.setStyle(Qt.SolidLine)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(0, y_min, rect.width(), y_min)
            painter.drawLine(0, y_max, rect.width(), y_max)

            # draw center line
            pen.setStyle(Qt.DashLine)
            pen.setWidth(1)
            pen.setDashPattern([4, 8])  # 4px dash, 8px gap
            painter.setPen(pen)
            painter.drawLine(0, y_center, rect.width(), y_center)

    def _draw_text(self, painter: QPainter):
        text_padding = 5
        text_top = text_padding

        if user_settings.show_time_display:
            # draw text time display
            time_display_font_size = 12
            color = QUtil.rgb_to_qcolor(Color.WHITE)
            color.setAlpha(200)
            font = QFont(Const.PRIMARY_FONT, time_display_font_size)
            painter.setPen(color)
            painter.setFont(font)
            m = s = 0
            sign = "-" if self.current_time < 0 else ""
            t_abs = abs(self.current_time)
            m, s = divmod(int(t_abs), 60)
            painter.drawText(QRect(text_top, text_padding, 100, time_display_font_size), f'{sign}{m:02d}:{s:02d}')
            text_top += time_display_font_size + text_padding

        if user_settings.show_track_names:
            # list track names
            tg_font_size = 8
            t_font_size = 6
            for track_group in self.vis_config.track_groups:
                if not track_group.visible:
                    continue

                color = QUtil.rgb_to_qcolor(track_group.color)
                color.setAlpha(200)
                painter.setPen(color)

                font = QFont(Const.PRIMARY_FONT, tg_font_size, 200)
                painter.setFont(font)
                painter.drawText(QRect(text_padding, text_top, 200, tg_font_size), f'{track_group.name}')
                text_top += tg_font_size + 3

                for track in self.vis_config.get_tracks_by_group_id(track_group.group_id):
                    font = QFont(Const.PRIMARY_FONT, t_font_size, 100)
                    painter.setFont(font)
                    painter.drawText(QRect(text_padding, text_top, 200, t_font_size), f'{track.name}')
                    text_top += t_font_size + 3