from PySide6.QtGui import QFont, QPainter, QColor, QPen
from PySide6.QtCore import QRect, Qt
from common import Const, Color
from models import VisConfig
from utility import QUtil

class MidiRenderer:
    def __init__(self, vis_config: VisConfig):
        # set by parent
        self.width: int = 0
        self.height: int = 0

        # computed and cached for quick lookup
        self.playhead_x: float = 0
        self.rect: QRect = None
        self.pitch_min: int = 0
        self.pitch_max: int = 0

        self.set_vis_config(vis_config)

    def set_vis_config(self, vis_config: VisConfig):
        self.vis_config = vis_config

        if self.vis_config is not None:
            self.pitch_min = self.vis_config.get_min_pitch()
            self.pitch_max = self.vis_config.get_max_pitch()

    def set_dimensions(self, width: int, height: int):
        self.width = width
        self.height = height
        self.rect = QRect(0, 0, self.width, self.height)

        if self.vis_config is not None:
            self.playhead_x = self.width * self.vis_config.playhead_pos

    # calculated as function of screen width and playhead position
    def get_start_time(self) -> float:
        time_min = self.vis_config.get_min_time()
        max_sec = self.vis_config.get_max_sec_across_screen()
        return time_min - ((self.width - self.playhead_x) / self.width) * max_sec
    
    # calculated as function of screen width and playhead position
    def get_end_time(self) -> float:
        ratio = self.playhead_x / self.width
        values = [
            note.end + ratio * track.bar_sec_across_screen
            for track in self.vis_config.tracks
            if track.visible and track.notes
            for note in track.notes
        ]
        return max(values) if values else 0.0
    
    def draw(self, painter: QPainter, current_time: float):
        painter.fillRect(self.rect, QUtil.rgb_to_qcolor(self.vis_config.bg_color))

        # draw midi bars
        still_has_notes = False
        for track in self.vis_config.tracks:
            if not track.visible:
                continue

            pixels_per_sec = self.width / track.bar_sec_across_screen

            for note in track.notes:
                # x and width calc
                x = self.playhead_x + (note.start - current_time) * pixels_per_sec
                w = note.duration * pixels_per_sec
                x_right = x + w

                if x > self.width:
                    # note hasn't entered visible area yet - skip rendering
                    still_has_notes = True
                    continue

                # convert bar height ratio to pixels
                bar_height = self.height * track.bar_height_ratio

                # y and height calc
                t = (note.pitch - self.pitch_min) / (self.pitch_max - self.pitch_min)
                y_min = Const.SCREEN_PADDING
                y_max = self.height - Const.SCREEN_PADDING
                y = (y_max + t * (y_min - y_max)) - bar_height / 2
                h = bar_height

                color = track.color
                alpha = track.alpha
                if x <= self.playhead_x:
                    # turn white and start reducing alpha
                    color = Color.WHITE
                    alpha = 255 * (x_right / self.playhead_x)
                    alpha = max(0, min(255, alpha))  # clamp

                if x_right >= 0:
                    # still visible - draw
                    color = QUtil.rgb_to_qcolor(color)
                    color.setAlpha(alpha)
                    painter.setBrush(color)
                    painter.setPen(Qt.NoPen)
                    radius = int(bar_height * .5)
                    painter.drawRoundedRect(x, y, w, h, radius, radius) # TODO configurable
                    still_has_notes = True
                # else - note has fallen off screen, don't draw
            
        # draw playhead line that notes will cross when they "play"
        pen = QPen(QUtil.rgb_to_qcolor(Color.LIGHT_GRAY))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(self.playhead_x, 0, self.playhead_x, self.height)

        return still_has_notes