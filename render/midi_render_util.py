from dataclasses import dataclass, field
from typing import List
from PySide6.QtGui import QBrush, QLinearGradient, QPainter, QPen
from PySide6.QtCore import QRect, QRectF, Qt
from common import Const, Color, RGB
from models import VisConfig, BackgroundMode, Note
from render.video_provider import video_provider
from utility import QUtil
from utility.util import Util

@dataclass
class RenderTrack:
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    bar_height_ratio: float = .05
    bar_sec_across_screen: float = 2.0
    pitch_offset: int = 0
    notes: List[Note] = field(default_factory=list)

class MidiRenderUtil:
    def __new__(cls):
        raise TypeError("MidiRenderUtil is static")

    # translates a pitch to a y value for a given rect and offsets
    @staticmethod
    def pitch_to_y(pitch: int, pitch_min: int, pitch_max: int, rect: QRect, vert_padding_ratio: float, vert_offset_ratio: float) -> float:
        if pitch_max == pitch_min:
            return rect.height() / 2

        vert_padding = vert_padding_ratio * rect.height() / 2
        vert_offset = vert_offset_ratio * rect.height() / 2

        y_min = vert_padding + vert_offset
        y_max = rect.height() - vert_padding + vert_offset

        t = (pitch - pitch_min) / (pitch_max - pitch_min)

        return y_max + t * (y_min - y_max)
    
    @staticmethod
    def draw_preview_background(painter: QPainter, current_time: float, vis_config: VisConfig, rect: QRect, ignore_video: bool = False):
        # Note: only use this method for preview; bg renderer will only use color background
        if vis_config.bg_mode == BackgroundMode.Color:
            MidiRenderUtil.draw_color_background(painter, vis_config, rect)
        elif vis_config.bg_mode == BackgroundMode.Image:
            # TODO
            pass
        elif vis_config.bg_mode == BackgroundMode.Video:
            frame = video_provider.get_frame(current_time - vis_config.bg_video_time_offset, loop=vis_config.bg_video_loop)
            if frame is not None:
                painter.drawImage(rect, frame)
            else:
                painter.fillRect(rect, QUtil.rgb_to_qcolor(vis_config.bg_color))

    @staticmethod
    def draw_color_background(painter: QPainter, vis_config: VisConfig, rect: QRect):
        painter.fillRect(rect, QUtil.rgb_to_qcolor(vis_config.bg_color))
    
    @staticmethod
    def draw_notes(painter: QPainter, current_time: float, vis_config: VisConfig, pitch_min: int, pitch_max:int, rect: QRect):
        # convert ratios to pixel values
        playhead_x = rect.width() * vis_config.playhead_pos_ratio
        note_fade_distance = playhead_x * vis_config.note_fadeout_ratio

        # draw playhead line that notes will cross when they "play"
        if vis_config.show_playhead:
            color = QUtil.rgb_to_qcolor(vis_config.playhead_color)
            color.setAlpha(vis_config.playhead_alpha)
            pen = QPen(color)
            pen.setWidth(vis_config.playhead_thickness_ratio * rect.width())
            painter.setPen(pen)
            painter.drawLine(playhead_x, 0, playhead_x, rect.height())

        # build render tracks
        tracks: List[RenderTrack] = []
        track_groups = vis_config.track_groups[::-1]
        for tg in track_groups:
            if not tg.visible:
                continue

            group_tracks = vis_config.get_tracks_by_group_id(tg.group_id)
            for t in group_tracks:
                tracks.append(RenderTrack(
                    color = tg.color,
                    alpha = tg.alpha,
                    bar_height_ratio = tg.bar_height_ratio,
                    bar_sec_across_screen = tg.bar_sec_across_screen,
                    pitch_offset=tg.pitch_offset,
                    notes = t.notes
                ))

        # draw midi bars
        painter.setPen(Qt.NoPen)
        for track in tracks:
            pixels_per_sec = rect.width() / track.bar_sec_across_screen

            for note in track.notes:
                # x and width calc
                x = int(playhead_x + (note.start - current_time) * pixels_per_sec)
                w = int(note.duration * pixels_per_sec)
                x_right = x + w
                if x > rect.width() or x_right < 0:
                    # note isn't in visible area - skip rendering
                    continue

                # convert bar height ratio to pixels
                bar_height = int(rect.height() * track.bar_height_ratio * (1 - vis_config.vertical_padding_ratio))
                bar_height = max(bar_height, 1) # min of 1 pixel

                # y and height calc
                center_y = MidiRenderUtil.pitch_to_y(
                    note.pitch + track.pitch_offset,
                    pitch_min,
                    pitch_max,
                    rect,
                    vis_config.vertical_padding_ratio,
                    vis_config.vertical_offset_ratio,
                )
                y = center_y - bar_height / 2
                h = bar_height

                color = track.color
                alpha = track.alpha

                # start fading out only after the whole note has passed the playhead
                if x_right <= playhead_x:
                    fade_start_x = playhead_x - note_fade_distance
                    alpha = alpha * ((x_right - fade_start_x) / note_fade_distance)
                    alpha = max(0, min(255, alpha))

                # -- under glow --
                if x < playhead_x and vis_config.note_glow_enabled:
                    MidiRenderUtil._draw_note_glow(painter, playhead_x, x, y, w, h, color, alpha, bar_height, vis_config.note_glow_size, vis_config.note_glow_intensity)

                # -- note bar --
                MidiRenderUtil._draw_note(painter, x, y, w, h, color, alpha)

                # -- highlight --
                if x < playhead_x and vis_config.note_highlight_enabled:
                    MidiRenderUtil._draw_note_highlight(painter, playhead_x, x, y, w, h, color, alpha, vis_config.note_highlight_intensity)


    @staticmethod
    def draw_fade_overlay(painter: QPainter, current_time: float, start_time: float, end_time: float, vis_config: VisConfig, rect: QRect):
        if vis_config.fade_in_enabled and vis_config.fade_in_time > 0:
            # draw fade in
            fade_in_finish_time = start_time + vis_config.fade_in_time

            if start_time <= current_time <= fade_in_finish_time:
                t = (current_time - start_time) / vis_config.fade_in_time
                alpha = int(255 * (1.0 - t))
                alpha = Util.clamp(alpha, 0, 255)

                qcolor = QUtil.rgb_to_qcolor(vis_config.fade_in_color)
                qcolor.setAlpha(alpha)
                painter.fillRect(rect, qcolor)

        if vis_config.fade_out_enabled and vis_config.fade_out_time > 0:
            # draw fade out
            fade_out_start_time = end_time - vis_config.fade_out_time

            if fade_out_start_time <= current_time <= end_time:
                t = (current_time - fade_out_start_time) / vis_config.fade_out_time
                alpha = int(255 * t)
                alpha = Util.clamp(alpha, 0, 255)

                qcolor = QUtil.rgb_to_qcolor(vis_config.fade_out_color)
                qcolor.setAlpha(alpha)
                painter.fillRect(rect, qcolor)

    # -- Helpers
    @staticmethod
    def _draw_note_glow(
        painter: QPainter, 
        playhead_x: int, 
        x: int, y: int, w: int, h: int, color: RGB, alpha: int, 
        bar_height: int, glow_size: float, glow_intensity: float
    ):
        x_right = x + w
        glow_w = min(playhead_x, x_right) - x
        color_glow = Util.lighten_color(color, 0.75)

        pad_y: float = bar_height * glow_size

        glow_rect = QRectF(
            x,
            y - pad_y,
            glow_w,
            h + pad_y * 2,
        )

        gradient = QLinearGradient(
            glow_rect.left(),
            glow_rect.top(),
            glow_rect.left(),
            glow_rect.bottom(),
        )

        gradient.setColorAt(0.0, QUtil.rgb_to_qcolor_a(color_glow, 0))
        gradient.setColorAt(0.5, QUtil.rgb_to_qcolor_a(color_glow, int(alpha * glow_intensity))) # TODO: configure glow intesity (0.00 - 1.00)
        gradient.setColorAt(1.0, QUtil.rgb_to_qcolor_a(color_glow, 0))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))

        #radius = bar_height
        #painter.drawRoundedRect(glow_rect, radius, radius)
        painter.drawRect(glow_rect)

    @staticmethod
    def _draw_note(painter: QPainter, x: int, y: int, w: int, h: int, color: RGB, alpha: int):
        qcolor = QUtil.rgb_to_qcolor_a(color, alpha)
        color_light = Util.lighten_color(color, 0.4)
        qcolor_light = QUtil.rgb_to_qcolor_a(color_light, alpha)
        gradient = QLinearGradient(x, y, x, y + h)
        gradient.setColorAt(0.0, qcolor_light)
        gradient.setColorAt(0.5, qcolor)                
        painter.setBrush(QBrush(gradient))
        painter.drawRect(x, y, w, h)
        
    @staticmethod
    def _draw_note_highlight(
        painter: QPainter, 
        playhead_x: int, 
        x: int, y: int, w: int, h: int, 
        color: RGB, alpha: int, highlight_intensity: float
    ):
        x_right = x + w
        highlight_w = min(playhead_x, x_right) - x
        color_highlight = Util.lighten_color(color, highlight_intensity)
        qcolor = QUtil.rgb_to_qcolor_a(color_highlight, int(alpha / 2))
        painter.setBrush(qcolor)
        painter.drawRect(x, y, highlight_w, h)
