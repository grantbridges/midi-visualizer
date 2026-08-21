from dataclasses import dataclass, field
import math
import random
from typing import List
from PySide6.QtGui import QBrush, QLinearGradient, QPainter, QPen
from PySide6.QtCore import QRect, QRectF, Qt
from common import Color, RGB
from models import VisConfig, BackgroundMode, Note, Orientation
from media import video_provider, image_provider
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
    note_bounce_enabled: bool = False
    note_velocity_fx_enabled: bool = False
    velocity_min: int = 1
    velocity_max: int = 127
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

        y_min = rect.top() + vert_padding + vert_offset
        y_max = rect.top() + rect.height() - vert_padding + vert_offset

        t = (pitch - pitch_min) / (pitch_max - pitch_min)

        return y_max + t * (y_min - y_max)
    
    @staticmethod
    def playhead_x(rect: QRect, vis_config: VisConfig):
        return rect.left() + rect.width() * vis_config.playhead_pos_ratio
    
    @staticmethod
    def draw_preview_background(painter: QPainter, current_time: float, vis_config: VisConfig, rect: QRect, ignore_video: bool = False):
        # Note: only use this method for preview; bg renderer will only use color background
        match vis_config.bg_mode:
            case BackgroundMode.Color:
                MidiRenderUtil.draw_color_background(painter, vis_config, rect)
            case BackgroundMode.Image:
                image = image_provider.get_image()
                if image is not None:
                    painter.drawImage(rect, image)
            case BackgroundMode.Video:
                if ignore_video:
                    # fall through to black fill
                    painter.fillRect(rect, QUtil.rgb_to_qcolor(Color.BLACK))
                else:
                    frame = video_provider.get_frame(current_time - vis_config.bg_video_time_offset, loop=vis_config.bg_video_loop)
                    if frame is not None:
                        painter.drawImage(rect, frame)
            case BackgroundMode.NoBackground:
                pass
            case _:
                raise ValueError(f"Unsupported background mode: {vis_config.bg_mode}")

    @staticmethod
    def draw_color_background(painter: QPainter, vis_config: VisConfig, rect: QRect):
        painter.fillRect(rect, QUtil.rgb_to_qcolor(vis_config.bg_color))

    @staticmethod
    def draw_background_tint(painter: QPainter, vis_config: VisConfig, rect: QRect):        
        if vis_config.bg_tint_enabled:
            painter.fillRect(rect, QUtil.rgb_to_qcolor(vis_config.bg_tint_color, vis_config.bg_tint_alpha))
    
    @staticmethod
    def draw_waveform(painter: QPainter, current_time: float, vis_config: VisConfig, rect: QRect):
        if (not vis_config.show_waveform or
            not vis_config.play_audio or
            vis_config.waveform is None or
            vis_config.waveform.get_samples_length() == 0 or
            vis_config.waveform_sec_across_screen <= 0):
            return

        # convert ratios to pixels
        sec_per_px = vis_config.waveform_sec_across_screen / rect.width()
        waveform_height_px = rect.height() * vis_config.waveform_height_ratio
        waveform_center_y = rect.top() + (rect.height() * vis_config.waveform_pos_ratio)
        playhead_x = MidiRenderUtil.playhead_x(rect, vis_config)

        color = QUtil.rgb_to_qcolor(vis_config.waveform_color, vis_config.waveform_alpha)
        pen = QPen(color)
        pen.setWidth(1)
        painter.setPen(pen)

        audio_time = current_time - vis_config.audio_time_offset

        # draw waveform over current visible rect, position adjusted for current time
        for x in range(rect.left(), rect.right() + 1):
            time_at_x = audio_time + ((x - playhead_x) * sec_per_px)

            sample = vis_config.waveform.get_sample_at_time(time_at_x)
            if sample is None:
                continue

            min_amp, max_amp = sample
            y1 = waveform_center_y - (max_amp * waveform_height_px / 2)
            y2 = waveform_center_y - (min_amp * waveform_height_px / 2)

            painter.drawLine(x, y1, x, y2)

    @staticmethod
    def draw_notes(painter: QPainter, current_time: float, vis_config: VisConfig, pitch_min: int, pitch_max:int, rect: QRect):
        # convert ratios to pixel values
        playhead_x = MidiRenderUtil.playhead_x(rect, vis_config)
        
        # compute fade start/end positions
        note_fadein_start_x = playhead_x + (rect.right() - playhead_x) * vis_config.note_fadein_start_ratio
        note_fadein_end_x = playhead_x + (rect.right() - playhead_x) * vis_config.note_fadein_end_ratio
        note_fadeout_start_x = rect.left() + (playhead_x - rect.left()) * vis_config.note_fadeout_start_ratio
        note_fadeout_end_x = rect.left() + (playhead_x - rect.left()) * vis_config.note_fadeout_end_ratio

        # draw playhead line that notes will cross when they "play"
        if vis_config.show_playhead:
            color = QUtil.rgb_to_qcolor(vis_config.playhead_color, vis_config.playhead_alpha)
            pen = QPen(color)
            pen.setWidth(vis_config.playhead_thickness_ratio * rect.width())
            painter.setPen(pen)
            painter.drawLine(playhead_x, rect.top(), playhead_x, rect.bottom())

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
                    note_sparks_enabled=vis_config.note_sparks_enabled and tg.note_sparks_enabled,
                    note_bounce_enabled=vis_config.note_bounce_enabled and tg.note_bounce_enabled,
                    note_velocity_fx_enabled=tg.note_velocity_fx_enabled,
                    velocity_min=t.velocity_min,
                    velocity_max=t.velocity_max,
                    notes = t.notes
                ))

        # In order to make note speed feel consistent between different
        # orientations, create a normalized "baseline_width" for computing
        # pixels per second instead of just dumbly using the rect.width()
        LANDSCAPE_W = Orientation.Landscape.value[0]
        LANDSCAPE_H = Orientation.Landscape.value[1]
        short_side = min(rect.width(), rect.height())
        baseline_width = short_side * ( LANDSCAPE_W / LANDSCAPE_H )

        # draw midi bars
        painter.setPen(Qt.NoPen)
        for track in tracks:
            pixels_per_sec = baseline_width / track.bar_sec_across_screen

            for note in track.notes:
                # x and width calc
                x_left = int(playhead_x + (note.start - current_time) * pixels_per_sec)
                w = int(note.duration * pixels_per_sec)
                x_right = x_left + w
                if x_left > rect.right() or x_right < rect.left():
                    # note isn't in visible area - skip rendering
                    continue

                # y and height calc
                # convert bar height ratio to pixels
                bar_height_px = int(rect.height() * track.bar_height_ratio * (1 - vis_config.vertical_padding_ratio))

                if track.note_bounce_enabled and x_left <= playhead_x:
                    # expand note on play
                    bar_height_px += bar_height_px * vis_config.note_bounce_height_ratio

                bar_height_px = max(bar_height_px, 1) # min of 1 pixel
                
                y_center = MidiRenderUtil.pitch_to_y(
                    note.pitch + track.pitch_offset,
                    pitch_min,
                    pitch_max,
                    rect,
                    vis_config.vertical_padding_ratio,
                    vis_config.vertical_offset_ratio,
                )
                y_top = y_center - bar_height_px / 2
                h = bar_height_px

                color = track.color
                alpha = track.alpha

                # start fading in when note is within range of playhead
                if vis_config.note_fadein_enabled and x_left >= playhead_x:
                    alpha = alpha * (1 - ((x_left - note_fadein_end_x) / (note_fadein_start_x - note_fadein_end_x)))
                    alpha = Util.clamp(alpha, 0, track.alpha)

                # start fading out when right edge of note has passed the playhead
                if vis_config.note_fadeout_enabled and x_right <= playhead_x:
                    alpha = alpha * (x_right - note_fadeout_end_x) / (note_fadeout_start_x - note_fadeout_end_x)
                    alpha = Util.clamp(alpha, 0, track.alpha)

                # -- note sparks --
                if vis_config.note_sparks_enabled and track.note_sparks_enabled:
                    MidiRenderUtil._draw_note_sparks(
                        painter, vis_config, playhead_x, note.pitch, note.start, y_center, bar_height_px, pixels_per_sec,
                        current_time, color, alpha
                    )

                # -- under glow --
                if vis_config.note_glow_enabled and x_left <= playhead_x:
                    MidiRenderUtil._draw_note_glow(painter, vis_config, playhead_x, x_left, y_top, w, h, color, alpha, bar_height_px)

                # -- note bar --
                MidiRenderUtil._draw_note(painter, x_left, y_top, w, h, color, alpha, vis_config.note_enhance_color)

                # -- highlight --
                if vis_config.note_highlight_enabled and x_left <= playhead_x:
                    MidiRenderUtil._draw_note_highlight(painter, vis_config, track, note, playhead_x, x_left, y_top, w, h, color, alpha)


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
        glow_w = min(playhead_x, x_right) - x if vis_config.note_glow_played_region else w
        color_glow = Util.mix_colors(color, vis_config.note_glow_color, 0.75)

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
    def _draw_note(painter: QPainter, x: int, y: int, w: int, h: int, color: RGB, alpha: int, use_gradient: bool):
        qcolor = QUtil.rgb_to_qcolor(color, alpha)

        painter.setPen(Qt.NoPen)
        if use_gradient:
            color_light = Util.lighten_color(color, 0.4)
            qcolor_light = QUtil.rgb_to_qcolor(color_light, alpha)
            gradient = QLinearGradient(x, y, x, y + h)
            gradient.setColorAt(0.0, qcolor_light)
            gradient.setColorAt(0.5, qcolor)       
            painter.setBrush(QBrush(gradient))
        else:
            painter.setBrush(qcolor)
        
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

            # calculate speed and randomize a bit
            base_speed_px_per_sec = vis_config.note_sparks_speed_ratio * bar_px_per_sec
            speed_px_per_sec = seed.uniform(base_speed_px_per_sec, vis_config.note_sparks_speed_var_ratio * base_speed_px_per_sec)

            # calculate positions, adjusted over animation period
            x = playhead_x - (start_dist_px + speed_px_per_sec * anim_time) * math.cos(angle)
            y = note_center_y - (start_dist_px + speed_px_per_sec * anim_time) * math.sin(angle)

            # draw (matching highlight lightening)
            color_highlight = Util.mix_colors(color, vis_config.note_highlight_color, vis_config.note_highlight_intensity)
            qcolor = QUtil.rgb_to_qcolor(color_highlight, int(alpha * vis_config.note_sparks_alpha_ratio))
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
        track: RenderTrack, note: Note,
        playhead_x: int, x: int, y: int, w: int, h: int, 
        color: RGB, alpha: int
    ):
        # draw transparent overlay over played note area to brighten
        x_right = x + w
        highlight_w = min(playhead_x, x_right) - x if vis_config.note_highlight_played_region else w

        highlight_factor = vis_config.note_highlight_intensity

        if vis_config.note_highlight_use_velocity and track.note_velocity_fx_enabled:
            vel_ratio = 1
            if track.velocity_min != track.velocity_max:
                vel_ratio = (note.velocity - track.velocity_min) / (track.velocity_max - track.velocity_min)
            
            min_h_i = vis_config.note_highlight_min_intensity
            max_h_i = vis_config.note_highlight_max_intensity

            highlight_factor = min_h_i + vel_ratio * (max_h_i - min_h_i)
        
        color_highlight = Util.mix_colors(color, vis_config.note_highlight_color, highlight_factor)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QUtil.rgb_to_qcolor(color_highlight, alpha * .8))
        painter.drawRect(x, y, highlight_w, h)
