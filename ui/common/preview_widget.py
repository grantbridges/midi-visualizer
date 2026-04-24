import time
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QFont, QPainter, QColor, QPen
from PySide6.QtCore import QRect, QTimer, Qt
from common import Const, Color
from models import VisConfig
from utility import QUtil

class PreviewWidget(QWidget):
    def __init__(self, vis_config: VisConfig, parent=None):
        super().__init__(parent)
        self.vis_config: VisConfig = vis_config
        self.active: bool = False

        self.current_time: float = 0.0 # sec
        self.pitch_min = 0
        self.pitch_max = 0

    def set_active(self, active: bool):
        self.active = active

    def calculate_start_time_offset(self):
        time_min = self.vis_config.get_min_time()

        min_pps = self.vis_config.get_min_pixels_per_second()
        #return time_min - ((self.width() - self._playhead_x()) / min_pps)
        return (self.width() - self._playhead_x()) / min_pps
    
    def calculate_end_time(self):
        return max(
            note.end + (self._playhead_x() / track.bar_pixels_per_second)
            for track in self.vis_config.tracks
            for note in track.notes
        )

    def reset(self):
        self.pitch_min = self.vis_config.get_min_pitch()
        self.pitch_max = self.vis_config.get_max_pitch()

    def tick(self, current_time):
        self.current_time = current_time
        self.update() # queues paint event

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.active:
            still_has_notes = self._paint_active(painter)
            if not still_has_notes:
                pass # TODO notify
        else:
            self._paint_inactive(painter)

    def _paint_inactive(self, painter: QPainter):
        # background
        painter.fillRect(self.rect(), QUtil.rgb_to_qcolor(Color.DARKER_GRAY))

        color = QUtil.rgb_to_qcolor(Color.WHITE)
        color.setAlpha(200)
        font = QFont(Const.PRIMARY_FONT, 12)
        font.setItalic(True)
        painter.setPen(color)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, "Click \"Play\" to preview visualization")
            
    def _paint_active(self, painter: QPainter):
        # background
        painter.fillRect(self.rect(), QUtil.rgb_to_qcolor(self.vis_config.bg_color))

        # draw midi bars
        still_has_notes = False
        for track in self.vis_config.tracks:
            if not track.visible:
                continue

            for note in track.notes:
                # x and width calc
                x = self._playhead_x() + (note.start - self.current_time) * track.bar_pixels_per_second
                w = note.duration * track.bar_pixels_per_second
                x_right = x + w

                if x > self.width():
                    # note hasn't entered visible area yet - skip rendering
                    still_has_notes = True
                    continue

                # y and height calc
                t = (note.pitch - self.pitch_min) / (self.pitch_max - self.pitch_min)
                y_min = Const.SCREEN_PADDING
                y_max = self.height() - Const.SCREEN_PADDING
                y = (y_max + t * (y_min - y_max)) - track.bar_height / 2
                h = track.bar_height

                color = track.color
                alpha = track.alpha
                if x <= self._playhead_x():
                    # turn white and start reducing alpha
                    color = Color.WHITE
                    alpha = 255 * (x_right / self._playhead_x())
                    alpha = max(0, min(255, alpha))  # clamp

                if x_right >= 0:
                    # still visible - draw
                    color = QUtil.rgb_to_qcolor(color)
                    color.setAlpha(alpha)
                    painter.setBrush(color)
                    painter.setPen(Qt.NoPen)
                    radius = int(track.bar_height * .5)
                    painter.drawRoundedRect(x, y, w, h, radius, radius)
                    still_has_notes = True
                # else - note has fallen off screen, don't draw
            
        # draw playhead line that notes will cross when they "play"
        pen = QPen(QUtil.rgb_to_qcolor(Color.LIGHT_GRAY))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(self._playhead_x(), 0, self._playhead_x(), self.height())

        # draw text time display
        color = QUtil.rgb_to_qcolor(Color.WHITE)
        color.setAlpha(200)
        font = QFont(Const.PRIMARY_FONT, 12)
        painter.setPen(color)
        painter.setFont(font)
        m = s = 0
        if self.current_time > 0:
            m, s = divmod(int(self.current_time), 60)
        painter.drawText(QRect(5, 5, 100, 100), f'{m:02d}:{s:02d}')

        return still_has_notes

    # line where notes cross when they play
    def _playhead_x(self):
        return self.width() * self.vis_config.playhead_pos