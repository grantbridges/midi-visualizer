from uuid import UUID

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
        self.start_time: float = 0.0 # sec
        self.end_time: float = 1.0 # sec
        self.pitch_min: int = 0
        self.pitch_max: int = 0

        self.selected_group_id: UUID | None = None

    def refresh(self, current_time: float, vis_config: VisConfig, start_time: float, end_time: float, pitch_min: int, pitch_max: int):
        self.current_time = current_time
        self.vis_config = vis_config
        self.start_time = start_time
        self.end_time = end_time
        self.pitch_min = pitch_min
        self.pitch_max = pitch_max

        self.update() # queues paint event

    def set_selected_group_id(self, group_id: UUID | None):
        self.selected_group_id = group_id
        self.update() # queues paint event

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        MidiRenderUtil.draw_preview_background(
            painter, 
            self.current_time, 
            self.vis_config,
            self.rect()
        )

        self._draw_guides(painter)
        self._draw_pitches(painter)

        MidiRenderUtil.draw_notes(
            painter, 
            self.current_time, 
            self.vis_config,
            self.pitch_min, 
            self.pitch_max, 
            self.rect()
        )

        MidiRenderUtil.draw_fade_overlay(
            painter,
            self.current_time,
            self.start_time,
            self.end_time,
            self.vis_config,
            self.rect()
        )

        self._draw_text(painter)

    def _draw_guides(self, painter: QPainter):
        if not user_settings.show_guides:
            return

        vert_padding = self.vis_config.vertical_padding_ratio * self.rect().height() / 2
        vert_offset = self.vis_config.vertical_offset_ratio * self.rect().height() / 2
        rect = self.rect()

        # positions
        y_center = self.rect().height() / 2 + vert_offset
        y_min = vert_padding + vert_offset
        y_max = self.rect().height() - vert_padding + vert_offset

        # draw pitches
        color = QUtil.rgb_to_qcolor(Util.invert_color(self.vis_config.bg_color), 200)

        # draw vertical padding guides
        pen = QPen(color)
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(0, y_min, rect.width(), y_min)
        painter.drawLine(0, y_max, rect.width(), y_max)

        # draw center line
        pen.setStyle(Qt.DashLine)
        pen.setWidth(1)
        pen.setDashPattern([4, 8])  # 4px dash,8px gap
        painter.setPen(pen)
        painter.drawLine(0, y_center, rect.width(), y_center)

    def _draw_pitches(self, painter: QPainter):
        
        # shorthand a few vars
        rect = self.rect()
        vpr = self.vis_config.vertical_padding_ratio
        vor = self.vis_config.vertical_offset_ratio
        pmin = self.pitch_min
        pmax = self.pitch_max

        # draw pitches
        color = QUtil.rgb_to_qcolor(Util.invert_color(self.vis_config.bg_color), 30)
        pen = QPen(color)
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(1)
        painter.setPen(pen)
        
        pitch_range = pmax - pmin
        if pitch_range > 0:
            if user_settings.show_pitches:
                for pitch in range(pmin, pmax + 1):
                    y = MidiRenderUtil.pitch_to_y(pitch, pmin, pmax, rect, vpr, vor)
                    painter.drawLine(0, y, rect.width(), y)

            # draw pitch guide lines for each track group
            if user_settings.show_track_groups:
                for track_group in self.vis_config.track_groups:
                    if not track_group.visible:
                        continue

                    is_selected = self.selected_group_id == track_group.group_id
                    color = QUtil.rgb_to_qcolor(track_group.color, 255 if is_selected else 70)
                    pen_width = 3 if is_selected else 1
                    pen = QPen(color)
                    pen.setStyle(Qt.SolidLine)
                    pen.setWidth(pen_width)
                    painter.setPen(pen)     

                    group_pmin = self.vis_config.get_min_pitch_for_track_group(track_group.group_id)
                    group_pmax = self.vis_config.get_max_pitch_for_track_group(track_group.group_id)

                    pitch_min_y = MidiRenderUtil.pitch_to_y(group_pmin, pmin, pmax, rect, vpr, vor)
                    pitch_max_y = MidiRenderUtil.pitch_to_y(group_pmax, pmin, pmax, rect, vpr, vor)

                    painter.drawLine(0, pitch_min_y, rect.width(), pitch_min_y)
                    painter.drawLine(0, pitch_max_y, rect.width(), pitch_max_y)

                    # list track names
                    track_group_font_size = 8
                    track_font_size = 6
                    text_padding = 5
                    text_top = pitch_max_y + pen_width

                    font = QFont(Const.PRIMARY_FONT, track_group_font_size, 200)
                    painter.setFont(font)
                    painter.drawText(QRect(text_padding, text_top, 200, track_group_font_size), f'{track_group.name}')
                    text_top += track_group_font_size + 3

                    for track in self.vis_config.get_tracks_by_group_id(track_group.group_id):
                        font = QFont(Const.PRIMARY_FONT, track_font_size, 100)
                        painter.setFont(font)
                        painter.drawText(QRect(text_padding, text_top, 200, track_font_size), f'{track.name}')
                        text_top += track_font_size + 3



    def _draw_text(self, painter: QPainter):
        text_padding = 5
        text_top = text_padding

        if user_settings.show_time_display:
            # draw text time display
            time_display_font_size = 12
            color = QUtil.rgb_to_qcolor(Color.WHITE, 200)
            font = QFont(Const.PRIMARY_FONT, time_display_font_size)
            painter.setPen(color)
            painter.setFont(font)
            m = s = 0
            sign = "-" if self.current_time < 0 else ""
            t_abs = abs(self.current_time)
            m, s = divmod(int(t_abs), 60)
            painter.drawText(QRect(text_top, text_padding, 100, time_display_font_size), f'{sign}{m:02d}:{s:02d}')
            text_top += time_display_font_size + text_padding