import tempfile
import shutil
import subprocess
import os
from pathlib import Path
from models import VisConfig
from render.resolution import Resolution
from render.midi_renderer import MidiRenderer
from PySide6.QtGui import QImage, QPainter, QColor, QPen
from PySide6.QtCore import Qt
from common import Color, Const

class VideoGenerator():
    def __init__(self, vis_config: VisConfig, resolution: Resolution, output_dir: str):
        self.vis_config: VisConfig = vis_config
        (self.width, self.height) = resolution.value
        self.output_dir = output_dir

    def generate_mp4(self):
        # create output filepath - delete if already exists
        output_file = Path(self.output_dir).joinpath(f"{self.vis_config.track_name}.mp4")
        output_file.unlink(missing_ok=True)

        frames_dir = tempfile.mkdtemp()

        try:
            midi_renderer = MidiRenderer(self.vis_config)
            midi_renderer.set_dimensions(self.width, self.height)

            start_time = midi_renderer.get_start_time()
            end_time = midi_renderer.get_end_time()
            current_time = start_time

            # generate all frames
            frame_index = 0
            while current_time <= end_time:
                image = QImage(self.width, self.height, QImage.Format_ARGB32)

                painter = QPainter(image)
                painter.setRenderHint(QPainter.Antialiasing)

                midi_renderer.draw(painter, current_time)

                painter.end()

                path = Path(frames_dir).joinpath(f"frame_{frame_index:05d}.png")
                image.save(str(path))

                percent = (current_time - start_time) / (end_time - start_time) * 100
                print(f"MP4 Generation | Created frame {frame_index} ({percent:0.2f}%)")

                frame_index += 1
                current_time += 1 / float(Const.FPS) # iterate one frame

            # encode video
            print(f"MP4 Generation | Creating MP4 file...")
            subprocess.run([
                "ffmpeg",
                "-y",
                "-framerate", str(Const.FPS),
                "-i", os.path.join(frames_dir, "frame_%05d.png"),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                str(output_file),
            ], check=True)

            print(f"MP4 Generation | Saved MP4")
        finally:
            shutil.rmtree(frames_dir)