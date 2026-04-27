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
        return MidiRenderer.draw_frame(
            painter, 
            current_time, 
            self.vis_config, 
            self.pitch_min, 
            self.pitch_max,
            self.width, 
            self.height
        )
    
    @staticmethod
    def draw_frame(painter: QPainter, current_time: float, vis_config: VisConfig, pitch_min: int, pitch_max:int, width: int, height: int):
        painter.fillRect(QRect(0, 0, width, height), QUtil.rgb_to_qcolor(vis_config.bg_color))

        playhead_x = width * vis_config.playhead_pos

        # draw midi bars
        for track in vis_config.tracks:
            if not track.visible:
                continue

            pixels_per_sec = width / track.bar_sec_across_screen

            for note in track.notes:
                # x and width calc
                x = playhead_x + (note.start - current_time) * pixels_per_sec
                w = note.duration * pixels_per_sec
                x_right = x + w

                if x > width:
                    # note hasn't entered visible area yet - skip rendering
                    continue

                # convert bar height ratio to pixels
                bar_height = height * track.bar_height_ratio

                # y and height calc
                t = (note.pitch - pitch_min) / (pitch_max - pitch_min)
                y_min = Const.SCREEN_PADDING
                y_max = height - Const.SCREEN_PADDING
                y = (y_max + t * (y_min - y_max)) - bar_height / 2
                h = bar_height

                color = track.color
                alpha = track.alpha
                if x <= playhead_x:
                    # turn white and start reducing alpha
                    color = Color.WHITE
                    alpha = 255 * (x_right / playhead_x)
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
        painter.drawLine(playhead_x, 0, playhead_x, height)