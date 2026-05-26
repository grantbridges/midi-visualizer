from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import QRect, Qt
from common import Const, Color
from models import VisConfig
from utility import QUtil

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
        values = [
            note.end + ratio * track.bar_sec_across_screen
            for track in vis_config.tracks
            if track.visible and track.notes
            for note in track.notes
        ]
        return max(values) if values else 0.0
    
    @staticmethod
    def draw_frame(painter: QPainter, current_time: float, vis_config: VisConfig, pitch_min: int, pitch_max:int, rect: QRect):
        # fill in bg color
        painter.fillRect(rect, QUtil.rgb_to_qcolor(vis_config.bg_color))

        # convert ratios to pixel values
        playhead_x = rect.width() * vis_config.playhead_pos_ratio
        vert_padding = vis_config.vertical_padding_ratio * rect.height() / 2
        vert_offset = vis_config.vertical_offset_ratio * rect.height() / 2
        note_fade_distance = playhead_x * vis_config.note_fadeout_ratio

        # draw playhead line that notes will cross when they "play"
        if vis_config.show_playhead:
            pen = QPen(QUtil.rgb_to_qcolor(vis_config.playhead_color))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(playhead_x, 0, playhead_x, rect.height())

        # draw midi bars
        for track in vis_config.tracks:
            if not track.visible:
                continue

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