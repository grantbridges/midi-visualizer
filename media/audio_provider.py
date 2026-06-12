from pathlib import Path

from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from utility import Util
from models import user_settings

class AudioProvider(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.audio_output = QAudioOutput(self)
        self.audio_output.setVolume(1.0)

        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio_output)

    def init(self):
        self.refresh_mute_state()

    def refresh_mute_state(self):
        self.set_muted(user_settings.mute_audio)

    def clear(self):
        self.player.stop()
        self.player.setSource(QUrl())

    def load_audio(self, audio_path: str):
        if Path(audio_path).is_file():
            self.player.setSource(QUrl.fromLocalFile(audio_path))

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

# module-level singleton instance
audio_provider = AudioProvider()