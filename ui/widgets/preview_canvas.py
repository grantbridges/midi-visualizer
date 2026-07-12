import math
from uuid import UUID

from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtGui import QFont, QPainter, QPen
from PySide6.QtCore import QRect, QRectF, Qt
from common import Const, Color
from models import VisConfig, user_settings
from render import MidiRenderUtil
from utility import QUtil, Util
from media.audio_provider import audio_provider

PREVIEW_MIN_HEIGHT = 100

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

        self.setMinimumHeight(PREVIEW_MIN_HEIGHT)

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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        try:
            rect = self._get_preview_rect()
            painter.setClipRect(rect)

            MidiRenderUtil.draw_preview_background(painter, self.current_time, self.vis_config, rect)
            MidiRenderUtil.draw_background_tint(painter, self.vis_config, rect)

            self._draw_guides(painter, rect)
            self._draw_pitches(painter, rect)

            MidiRenderUtil.draw_notes(painter, self.current_time, self.vis_config, self.pitch_min, self.pitch_max, rect)
            MidiRenderUtil.draw_waveform(painter, rect, self.current_time, self.vis_config)
            MidiRenderUtil.draw_fade_overlay(painter, self.current_time, self.start_time, self.end_time, self.vis_config, rect)

            self._draw_text(painter, rect)
        except Exception as e:
            QMessageBox.critical(self, "Preview Failed", f"Preview render failed: {str(e)}")

    def _draw_guides(self, painter: QPainter, rect: QRect):
        if not user_settings.show_guides:
            return

        vert_padding = self.vis_config.vertical_padding_ratio * rect.height() / 2
        vert_offset = self.vis_config.vertical_offset_ratio * rect.height() / 2

        # positions
        y_center = rect.height() / 2 + vert_offset
        y_min = vert_padding + vert_offset
        y_max = rect.height() - vert_padding + vert_offset

        # draw pitches
        color = QUtil.rgb_to_qcolor(Util.invert_color(self.vis_config.bg_color), 200)

        # draw vertical padding guides
        pen = QPen(color)
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(rect.left(), y_min, rect.right(), y_min)
        painter.drawLine(rect.left(), y_max, rect.right(), y_max)

        # draw center line
        pen.setStyle(Qt.DashLine)
        pen.setWidth(1)
        pen.setDashPattern([4, 8])  # 4px dash,8px gap
        painter.setPen(pen)
        painter.drawLine(rect.left(), y_center, rect.right(), y_center)

    def _draw_pitches(self, painter: QPainter, rect: QRect):
        # shorthand a few vars
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
                    painter.drawLine(rect.left(), y, rect.right(), y)

            # draw pitch guide lines for each track group
            if user_settings.show_track_groups:
                for track_group in sorted(
                    self.vis_config.get_visible_track_groups(),
                    # sort selected track (if available) to the end so it's drawn on top of the bunch
                    key=lambda tg: tg.group_id == self.selected_group_id,
                ):
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

                    painter.drawLine(rect.left(), pitch_min_y, rect.right(), pitch_min_y)
                    painter.drawLine(rect.left(), pitch_max_y, rect.right(), pitch_max_y)

                    # list track names
                    track_group_font_size = 8
                    track_font_size = 6
                    text_padding = 5
                    text_top = pitch_max_y + pen_width

                    font = QFont(Const.PRIMARY_FONT, track_group_font_size, 200)
                    painter.setFont(font)
                    painter.drawText(QRect(rect.left() + text_padding, text_top, 200, track_group_font_size), f'{track_group.name}')
                    text_top += track_group_font_size + 3

                    for track in self.vis_config.get_tracks_by_group_id(track_group.group_id):
                        font = QFont(Const.PRIMARY_FONT, track_font_size, 100)
                        painter.setFont(font)
                        painter.drawText(QRect(rect.left() + text_padding, text_top, 200, track_font_size), f'{track.name}')
                        text_top += track_font_size + 3

    def _draw_text(self, painter: QPainter, rect: QRect):
        text_padding = 5
        text_top = text_padding

        if user_settings.show_time_display:
            # draw text time display
            time_display_font_size = 10
            color = QUtil.rgb_to_qcolor(Color.WHITE, 200)
            font = QFont(Const.PRIMARY_FONT, time_display_font_size)
            painter.setPen(color)
            painter.setFont(font)
            sign = "-" if self.current_time < 0 else ""
            t_abs = abs(self.current_time)
            m = int(t_abs // 60)
            s = t_abs % 60
            painter.drawText(
                QRect(rect.left() + text_padding, rect.top() + text_padding, 130, time_display_font_size),
                f"{sign}{m:02d}:{s:05.2f}"
            )
            text_top += time_display_font_size + text_padding

    def _get_preview_rect(self) -> QRect:
        rect = self.contentsRect()

        if self.vis_config is None:
            return rect

        # size preview area - shape to fit orientation such that it will
        # fill vertically or horizontally in the available area, as much
        # as able
        aspect_width, aspect_height = self.vis_config.orientation.value
        aspect_ratio = aspect_width / aspect_height

        available_width = rect.width()
        available_height = rect.height()

        width = available_width
        height = int(width / aspect_ratio)

        if height > available_height:
            height = available_height
            width = int(height * aspect_ratio)

        x = rect.left() + int((available_width - width) / 2)
        y = rect.top() + int((available_height - height) / 2)

        return QRect(x, y, width, height)