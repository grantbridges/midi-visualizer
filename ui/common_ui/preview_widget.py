import time
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QFont, QPainter, QColor, QPen
from PySide6.QtCore import QRect, QTimer, Qt
from common import Const, Color
from models import VisConfig
from utility import QUtil

class PreviewWidget(QWidget):
    PIXELS_PER_SECOND = 200
    PAD = Const.SCREEN_PADDING

    def __init__(self, vis_config: VisConfig, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.vis_config = vis_config
        self.playing = False
        self.start_time_ms = 0
        self.current_time = 0.0 # sec
        self.current_frame = 0

        self.pitch_min = 0
        self.pitch_max = 0
        self.time_min = 0.0
        self.time_max = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)

    def is_playing(self):
        return self.playing

    def start(self):
        if not self.playing:
            self.playing = True
            self.start_time_ms = time.time_ns() // 1_000_000 # ms
            self.current_frame = 0

            (self.pitch_min, self.pitch_max) = self.vis_config.get_pitch_bounds()
            (self.time_min, self.time_max) = self.vis_config.get_time_bounds()

            self.timer.start(int(1000 / Const.FPS))

    def stop(self):
        if self.playing:
            self.playing = False
            self.timer.stop()

    def _on_tick(self):
        time_offset = self.time_min - (self.width() - self._playhead_x()) / self.PIXELS_PER_SECOND #+ start_time_offset

        current_time_ms = time.time_ns() // 1_000_000 # ms
        elapsed = (current_time_ms - self.start_time_ms) / 1000.0 # sec
        self.current_time = time_offset + elapsed

        self.update() # queues paint event

    # line where notes cross when they play
    def _playhead_x(self):
        return self.width() / 2

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.is_playing():
            self._paint_playing(painter)
        else:
            self._paint_stopped(painter)

    def _paint_stopped(self, painter: QPainter):
        # background
        painter.fillRect(self.rect(), QUtil.rgb_to_qcolor(Color.DARKER_GRAY))

        color = QUtil.rgb_to_qcolor(Color.WHITE)
        color.setAlpha(200)
        font = QFont(Const.PRIMARY_FONT, 12)
        font.setItalic(True)
        painter.setPen(color)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, "Click \"Play\" to preview visualization")
            
    def _paint_playing(self, painter: QPainter):
        # background
        painter.fillRect(self.rect(), QUtil.rgb_to_qcolor(self.vis_config.bg_color))

        # draw time markers
        for i in range(int(self.time_min), int(self.time_max) + 1):
            x = self._playhead_x() + (i - self.current_time) * self.PIXELS_PER_SECOND
            if x >= 0 and x <= (self.width() + 25):
                painter.setPen(QUtil.rgb_to_qcolor(Color.DARKER_GRAY))
                painter.drawLine(x, 0, x, self.height())

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
                y_min = self.PAD
                y_max = self.height() - self.PAD
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