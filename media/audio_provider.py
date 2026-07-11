import subprocess
import numpy as np
from pathlib import Path
from PySide6.QtCore import QObject, QUrl, Qt
from PySide6.QtGui import QImage, QBrush, QLinearGradient, QPainter, QPen
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from utility import Util
from models import user_settings
from common import Color
from utility import QUtil
import time

import logging
logger = logging.getLogger("AudioProvider")

class AudioProvider(QObject):
    '''
    Used for loading & playing audio in preview mode - NOT for rendering
    '''
    def __init__(self, parent=None):
        super().__init__(parent)

    def init(self):
        logger.info(f"Initializing")

        self.audio_output = QAudioOutput(self)
        self.audio_output.setVolume(1.0)

        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio_output)

        self.waveform_image: QImage | None = None

        self.refresh_mute_state()

    def refresh_mute_state(self):
        self.set_muted(user_settings.mute_audio)

    def clear(self):
        self.player.stop()
        self.player.setSource(QUrl())

    def load_audio(self, audio_path: str):
        try:
            if Path(audio_path).is_file():
                logger.info(f"Loading audio from \"{audio_path}\"")
                self.player.setSource(QUrl.fromLocalFile(audio_path))

                self._build_waveform_image(audio_path)
        except Exception:
            logger.exception("Failed to load audio")
            raise

    def is_playing(self) -> bool:
        return self.player.playbackState() == QMediaPlayer.PlayingState

    def play(self):
        self.player.play()

    def play_at(self, seconds: float):
        self.seek_seconds(seconds)
        if not self.is_playing():
            self.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def seek_seconds(self, seconds: float):
        self.player.setPosition(int(seconds * 1000))

    def get_position_seconds(self) -> float:
        return self.player.position() / 1000.0

    def get_duration_seconds(self) -> float:
        return self.player.duration() / 1000.0

    def set_volume(self, volume: float):
        self.audio_output.setVolume(Util.clamp(volume, 0.0, 1.0))

    def set_muted(self, muted: bool):
        self.audio_output.setMuted(muted)

    # --- waveform generation ---

    def get_img_px_per_sec(self):
        return 100

    def _build_waveform_image(self, audio_path: str):
        self.waveform_image = None

        start_time = time.perf_counter()

        sample_rate = 44100 # Hz

        try:
            # use ffmpeg to parse samples from audio file
            cmd = [
                "ffmpeg",
                "-i", audio_path,
                "-vn",
                "-f", "f32le",
                "-acodec", "pcm_f32le",
                "-ac", "1",
                "-ar", str(sample_rate),
                "-",
            ]

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=True,
            )

            samples = np.frombuffer(result.stdout, dtype=np.float32)

            samples_per_pixel = sample_rate / self.get_img_px_per_sec()
            total_pixels = int(len(samples) / samples_per_pixel)

            # draw image from amplitude min/max peaks over each sample window
            height_px = 100
            self.waveform_image = QImage(total_pixels, height_px, QImage.Format_RGBA8888)
            self.waveform_image.fill(Qt.transparent)

            painter = QPainter(self.waveform_image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

            pen = QPen(QUtil.rgb_to_qcolor(Color.WHITE, 25))
            pen.setStyle(Qt.SolidLine)
            pen.setWidth(1)
            painter.setPen(pen)

            center_y = height_px / 2

            for x in range(total_pixels):
                # grab window range of samples needed for each pixel
                start = int(x * samples_per_pixel)
                end = int((x + 1) * samples_per_pixel)

                chunk = samples[start:end]

                if len(chunk) == 0:
                    continue

                min_amp = float(chunk.min())
                max_amp = float(chunk.max())

                y1 = center_y - max_amp * (height_px / 2)
                y2 = center_y - min_amp * (height_px / 2)

                painter.drawLine(x, int(y1), x, int(y2))                
                
            painter.end()

            elapsed = time.perf_counter() - start_time
            logger.debug(f"Load Audio Image | Loaded in {elapsed:.3f} sec")
        except:
            logger.exception("Unable to load sample data from audio file")
            raise        


# module-level singleton instance
audio_provider = AudioProvider()