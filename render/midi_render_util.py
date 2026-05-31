from dataclasses import dataclass, field
from typing import List
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import QRect, Qt
from common import Const, Color
from common.types import RGB
from models import VisConfig
from models.note import Note
from utility import QUtil

@dataclass
class RenderTrack:
    color: RGB = Color.KAYLA_1
    alpha: int = 255
    bar_height_ratio: float = .05
    bar_sec_across_screen: float = 2.0
    vertical_padding_ratio: float = 0.0
    vertical_offset_ratio: float = 0.0
    notes: List[Note] = field(default_factory=list)

class MidiRenderUtil:
    def __new__(cls):
        raise TypeError("MidiRenderUtil is static")

    # calculated as function of view area width and playhead position such
    # that the first note bar appears just to the right of the right edge of
    # the view area
    @staticmethod
    def calc_start_time(vis_config: VisConfig, view_width: int) -> float:
        time_min = vis_config.get_min_time()
        max_sec = vis_config.get_max_sec_across_screen()
        playhead_x = view_width * vis_config.playhead_pos_ratio
        return time_min - ((view_width - playhead_x) / view_width) * max_sec
    
    # calculated as function of view area width and playhead position such
    # that the last note bar will end just to the left of the left edge of
    # the view area
    @staticmethod
    def calc_end_time(vis_config: VisConfig, view_width: int) -> float:
        playhead_x = view_width * vis_config.playhead_pos_ratio
        ratio = playhead_x / view_width

        values = []
        for track in vis_config.get_visible_tracks():
            group = vis_config.get_track_group_by_id(track.group_id)
            values.append(
                track.time_max + ratio * group.bar_sec_across_screen
            )

        return max(values) if values else 0.0
    
    @staticmethod
    def draw_frame(painter: QPainter, current_time: float, vis_config: VisConfig, pitch_min: int, pitch_max:int, rect: QRect):
        # fill in bg color
        painter.fillRect(rect, QUtil.rgb_to_qcolor(vis_config.bg_color))

        # convert ratios to pixel values
        playhead_x = rect.width() * vis_config.playhead_pos_ratio
        note_fade_distance = playhead_x * vis_config.note_fadeout_ratio

        # draw playhead line that notes will cross when they "play"
        if vis_config.show_playhead:
            pen = QPen(QUtil.rgb_to_qcolor(vis_config.playhead_color))
            pen.setWidth(2)
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
                    vertical_padding_ratio = tg.vertical_padding_ratio,
                    vertical_offset_ratio = tg.vertical_offset_ratio,
                    notes = t.notes
                ))

        # draw midi bars
        for track in tracks:
            vert_padding = track.vertical_padding_ratio * rect.height() / 2
            vert_offset = track.vertical_offset_ratio * rect.height() / 2

            pixels_per_sec = rect.width() / track.bar_sec_across_screen

            for note in track.notes:
                # x and width calc
                x = playhead_x + (note.start - current_time) * pixels_per_sec
                w = note.duration * pixels_per_sec
                x_right = x + w

                if x > rect.width():
                    # note hasn't entered visible area yet - skip rendering
                    continue

                # convert bar height ratio to pixels
                bar_height = rect.height() * track.bar_height_ratio

                # y and height calc
                t = (note.pitch - pitch_min) / (pitch_max - pitch_min)
                y_min = vert_padding + vert_offset
                y_max = rect.height() - vert_padding + vert_offset
                y = (y_max + t * (y_min - y_max)) - bar_height / 2
                h = bar_height

                color = track.color
                alpha = track.alpha

                if x_right >= 0:
                    radius = int(bar_height * 0)

                    # start fading out only after the whole note has passed the playhead
                    if x_right <= playhead_x:
                        fade_start_x = playhead_x - note_fade_distance
                        alpha = 255 * ((x_right - fade_start_x) / note_fade_distance)
                        alpha = max(0, min(255, alpha))

                    # left side of playhead - show play color
                    if x < playhead_x:
                        played_x = x
                        played_w = min(x_right, playhead_x) - x

                        if played_w > 0:
                            qcolor = QUtil.rgb_to_qcolor(vis_config.note_play_color)
                            qcolor.setAlpha(alpha)
                            painter.setBrush(qcolor)
                            painter.setPen(Qt.NoPen)
                            painter.drawRoundedRect(played_x, y, played_w, h, radius, radius)

                    # right side of playhead - show track color
                    if x_right > playhead_x:
                        color_x = max(x, playhead_x)
                        color_w = x_right - color_x

                        if color_w > 0:
                            qcolor = QUtil.rgb_to_qcolor(color)
                            qcolor.setAlpha(alpha)
                            painter.setBrush(qcolor)
                            painter.setPen(Qt.NoPen)
                            painter.drawRoundedRect(color_x, y, color_w, h, radius, radius)