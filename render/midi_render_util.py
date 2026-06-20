from dataclasses import dataclass, field
import math
import random
from typing import List
from PySide6.QtGui import QBrush, QLinearGradient, QPainter, QPen
from PySide6.QtCore import QRect, QRectF, Qt
from common import Const, Color, RGB
from models import VisConfig, BackgroundMode, Note
from media import video_provider
from utility import QUtil
from utility.util import Util

@dataclass
class RenderTrack:
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    bar_height_ratio: float = .05
    bar_sec_across_screen: float = 2.0
    pitch_offset: int = 0
    note_sparks_enabled: bool = False
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
            color = QUtil.rgb_to_qcolor(vis_config.playhead_color, vis_config.playhead_alpha)
            pen = QPen(color)
            pen.setWidth(vis_config.playhead_thickness_ratio * rect.width())
            painter.setPen(pen)
            painter.drawLine(playhead_x, 0, playhead_x, rect.height())

        # build render tracks
        tracks: List[RenderTrack] = []

        # iterate backwards so first groups are drawn on top
        track_groups = vis_config.get_visible_track_groups()[::-1] 

        for tg in track_groups:
            group_tracks = vis_config.get_tracks_by_group_id(tg.group_id)
            for t in group_tracks:
                tracks.append(RenderTrack(
                    color = tg.color,
                    alpha = tg.alpha,
                    bar_height_ratio = tg.bar_height_ratio,
                    bar_sec_across_screen = tg.bar_sec_across_screen,
                    pitch_offset=tg.pitch_offset,
                    note_sparks_enabled=tg.note_sparks_enabled,
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
                bar_height_px = int(rect.height() * track.bar_height_ratio * (1 - vis_config.vertical_padding_ratio))
                bar_height_px = max(bar_height_px, 1) # min of 1 pixel

                # y and height calc
                note_center_y = MidiRenderUtil.pitch_to_y(
                    note.pitch + track.pitch_offset,
                    pitch_min,
                    pitch_max,
                    rect,
                    vis_config.vertical_padding_ratio,
                    vis_config.vertical_offset_ratio,
                )
                y = note_center_y - bar_height_px / 2
                h = bar_height_px

                color = track.color
                alpha = track.alpha

                # start fading out only after the whole note has passed the playhead
                if x_right <= playhead_x:
                    fade_start_x = playhead_x - note_fade_distance
                    alpha = alpha * ((x_right - fade_start_x) / note_fade_distance)
                    alpha = max(0, min(255, alpha))

                # -- note sparks --
                if vis_config.note_sparks_enabled and track.note_sparks_enabled:
                    MidiRenderUtil._draw_note_sparks(
                        painter, vis_config, playhead_x, note.pitch, note.start, note_center_y, bar_height_px, pixels_per_sec,
                        current_time, color, alpha
                    )

                # -- under glow --
                if x < playhead_x and vis_config.note_glow_enabled:
                    MidiRenderUtil._draw_note_glow(painter, vis_config, playhead_x, x, y, w, h, color, alpha, bar_height_px)

                # -- note bar --
                MidiRenderUtil._draw_note(painter, x, y, w, h, color, alpha)

                # -- highlight --
                if x < playhead_x and vis_config.note_highlight_enabled:
                    MidiRenderUtil._draw_note_highlight(painter, vis_config, playhead_x, x, y, w, h, color, alpha)


    @staticmethod
    def draw_fade_overlay(painter: QPainter, current_time: float, start_time: float, end_time: float, vis_config: VisConfig, rect: QRect):
        if vis_config.fade_in_enabled and vis_config.fade_in_time > 0:
            # draw fade in
            fade_in_finish_time = start_time + vis_config.fade_in_time

            if start_time <= current_time <= fade_in_finish_time:
                t = (current_time - start_time) / vis_config.fade_in_time
                alpha = int(255 * (1.0 - t))
                alpha = Util.clamp(alpha, 0, 255)

                qcolor = QUtil.rgb_to_qcolor(vis_config.fade_in_color, alpha)
                painter.fillRect(rect, qcolor)

        if vis_config.fade_out_enabled and vis_config.fade_out_time > 0:
            # draw fade out
            fade_out_start_time = end_time - vis_config.fade_out_time

            if fade_out_start_time <= current_time <= end_time:
                t = (current_time - fade_out_start_time) / vis_config.fade_out_time
                alpha = int(255 * t)
                alpha = Util.clamp(alpha, 0, 255)

                qcolor = QUtil.rgb_to_qcolor(vis_config.fade_out_color, alpha)
                painter.fillRect(rect, qcolor)

    # -- Helpers
    @staticmethod
    def _draw_note_glow(
        painter: QPainter, vis_config: VisConfig, playhead_x: int, 
        x: int, y: int, w: int, h: int, color: RGB, alpha: int, 
        bar_height: int
    ):
        x_right = x + w
        glow_w = min(playhead_x, x_right) - x
        color_glow = Util.lighten_color(color, 0.75)

        # padding for how far glow extends vertically
        pad_y: float = bar_height * vis_config.note_glow_size

        # draw rect for glow area and define linear gradient over it
        glow_rect = QRectF(x, y - pad_y, glow_w, h + pad_y * 2)
        gradient = QLinearGradient(
            glow_rect.left(),
            glow_rect.top(),
            glow_rect.left(),
            glow_rect.bottom(),
        )

        # set linear gradient from top to bottom
        gradient.setColorAt(0.0, QUtil.rgb_to_qcolor(color_glow, 0))
        gradient.setColorAt(0.5, QUtil.rgb_to_qcolor(color_glow, int(alpha * vis_config.note_glow_intensity)))
        gradient.setColorAt(1.0, QUtil.rgb_to_qcolor(color_glow, 0))

        # draw glow
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(glow_rect)

    @staticmethod
    def _draw_note(painter: QPainter, x: int, y: int, w: int, h: int, color: RGB, alpha: int):
        qcolor = QUtil.rgb_to_qcolor(color, alpha)
        color_light = Util.lighten_color(color, 0.4)
        qcolor_light = QUtil.rgb_to_qcolor(color_light, alpha)
        gradient = QLinearGradient(x, y, x, y + h)
        gradient.setColorAt(0.0, qcolor_light)
        gradient.setColorAt(0.5, qcolor)       
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(x, y, w, h)
        

    @staticmethod
    def _draw_note_sparks(
        painter: QPainter, 
        vis_config: VisConfig,
        playhead_x: float, 
        note_pitch: int,
        note_start_time: float,
        note_center_y: float,
        bar_height_px: float,
        bar_px_per_sec: float,
        current_time: float,
        color: RGB, 
        alpha: int
    ):
        # how long has it been since note has been played?
        anim_time = current_time - note_start_time
        if anim_time <= 0:
            return # only spark once we've played the note
        
        start_dist_px = bar_height_px * vis_config.note_sparks_start_dist_ratio
        start_length_px = bar_height_px * vis_config.note_sparks_start_length_ratio

        # calculate length of sparks - shrinks the more time has passed
        length_px = start_length_px * (1 - anim_time / vis_config.note_sparks_time_to_fade_sec)
        if length_px < 1:
            return # too small - skip

        for i in range(vis_config.note_sparks_count):
            # calculate angle of spark using deterministic random value seeded by note 
            # properties and spark count
            seed = random.Random(note_pitch * note_start_time + 100 * i)
            angle_d = seed.uniform(-vis_config.note_sparks_max_angle_deg, vis_config.note_sparks_max_angle_deg)
            angle = math.radians(angle_d)

            # randomize speed a bit
            speed_rand = seed.uniform(bar_px_per_sec, bar_px_per_sec * 1.2)
            speed_px_per_sec = speed_rand

            # calculate positions, adjusted over animation period
            x = playhead_x - (start_dist_px + speed_px_per_sec * anim_time) * math.cos(angle)
            y = note_center_y - (start_dist_px + speed_px_per_sec * anim_time) * math.sin(angle)

            # draw (lighter)
            color_highlight = Util.lighten_color(color, vis_config.note_highlight_intensity)
            qcolor = QUtil.rgb_to_qcolor(color_highlight, int(alpha / 2))
            painter.setPen(Qt.NoPen)
            painter.setBrush(qcolor)
            painter.drawRect(x - length_px / 2, y - length_px / 2, length_px, length_px)

            # old code for drawing as line - boxes look cleaner but 
            # leaving this here in case I ever want to try it out again
            # x2 = x - length_px * math.cos(angle)
            # y2 = y - length_px * math.sin(angle)
            # pen = QPen(qcolor)
            # pen.setWidth(1)
            # painter.setPen(pen)
            # painter.drawLine(x, y, x2, y2)

        
    @staticmethod
    def _draw_note_highlight(
        painter: QPainter, vis_config: VisConfig, 
        playhead_x: int, x: int, y: int, w: int, h: int, 
        color: RGB, alpha: int
    ):
        # draw transparent overlay over played note area to brighten
        x_right = x + w
        highlight_w = min(playhead_x, x_right) - x
        color_highlight = Util.lighten_color(color, vis_config.note_highlight_intensity)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QUtil.rgb_to_qcolor(color_highlight, int(alpha / 2)))
        painter.drawRect(x, y, highlight_w, h)
