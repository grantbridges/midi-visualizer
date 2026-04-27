from PySide6.QtCore import QObject, QThread, Signal, Slot
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Event, Manager
from common import Const
from models import VisConfig
from pathlib import Path
from PySide6.QtGui import QImage, QPainter
from render.midi_renderer import MidiRenderer
from dataclasses import dataclass
import tempfile
import shutil
import os
import subprocess
from render.resolution import Resolution

@dataclass(frozen=True)
class RenderFrameJobInput:
    frame_index: int
    vis_config: VisConfig
    pitch_min: int
    pitch_max: int
    width: int
    height: int
    start_time: float
    frames_dir: str

class RenderWorker(QObject):
    progress = Signal(int, str) # percent, message
    finished = Signal(str) # output path
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, vis_config: VisConfig, resolution: Resolution, output_dir: str):
        super().__init__()
        self.vis_config: VisConfig = vis_config
        (self.width, self.height) = resolution.value
        self.output_dir = output_dir
        self.output_file = ""
        self._cancel_requested = False

    @Slot()
    def run(self):
        try:
            with Manager() as manager:
                cancel_event = manager.Event()

                # create output filepath - delete if already exists
                # TODO do this to a temp file
                # TODO extension support
                self.output_file = Path(self.output_dir).joinpath(f"{self.vis_config.track_name}.mp4")
                self.output_file.unlink(missing_ok=True)

                # build temp directory for storing image frames in
                frames_dir = tempfile.mkdtemp()

                try:
                    midi_renderer = MidiRenderer(self.vis_config)
                    midi_renderer.set_dimensions(self.width, self.height)

                    start_time = midi_renderer.get_start_time()
                    end_time = midi_renderer.get_end_time()

                    # build render frame job for every frame
                    total_frames = int((end_time - start_time) * Const.FPS)
                    jobs = [
                        RenderFrameJobInput(
                            frame_index = i, 
                            vis_config=self.vis_config, 
                            pitch_min=midi_renderer.pitch_min, 
                            pitch_max=midi_renderer.pitch_max, 
                            width=self.width, 
                            height=self.height, 
                            start_time=start_time,
                            frames_dir=frames_dir
                        )
                        for i in range(total_frames)
                    ]

                    # fire off process workers
                    with ProcessPoolExecutor() as executor:
                        futures = [executor.submit(RenderWorker.render_frame_job, j, cancel_event) for j in jobs]

                        completed = 0

                        for future in as_completed(futures):
                            if self._cancel_requested:
                                cancel_event.set()

                                for f in futures:
                                    f.cancel()

                                self.cancelled.emit()
                                return

                            future.result()  # raises if frame failed

                            completed += 1
                            percent = int((completed / total_frames) * 100)
                            self.progress.emit(percent, f"Rendering frames...")

                    self.progress.emit(None, "Encoding MP4...")
                    RenderWorker.encode_frames_to_mp4(frames_dir, self.output_file)
                finally:
                    shutil.rmtree(frames_dir)

            self.finished.emit(str(self.output_file))
        except Exception as e:
            self.failed.emit(str(e))

    def cancel(self):
        self._cancel_requested = True

    @staticmethod
    def render_frame_job(job: RenderFrameJobInput, cancel_event):
        if cancel_event.is_set():
            return

        current_time = job.start_time + job.frame_index / Const.FPS

        image = QImage(job.width, job.height, QImage.Format_ARGB32)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        MidiRenderer.draw_frame(painter, current_time, job.vis_config, job.pitch_min, job.pitch_max, job.width, job.height)
        painter.end()

        if cancel_event.is_set():
            return

        # save image file to disk
        path = Path(job.frames_dir).joinpath(f"frame_{job.frame_index:05d}.png")
        image.save(str(path))

        return job.frame_index
    
    @staticmethod
    def encode_frames_to_mp4(frames_dir: str, output_file: Path):
        subprocess.run([
            "ffmpeg",
            "-y",
            "-framerate", str(Const.FPS),
            "-i", os.path.join(frames_dir, "frame_%05d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(output_file),
        ], check=True)

    @staticmethod
    def encode_frames_to_mov(frames_dir: str, output_file: Path):
        subprocess.run([
            "ffmpeg",
            "-y",
            "-framerate", str(Const.FPS),
            "-i", os.path.join(frames_dir, "frame_%05d.png"),
            "-c:v", "prores_ks",
            "-profile:v", "3",  # 3 = standard ProRes 422
            str(output_file.with_suffix(".mov")),
        ], check=True)

    @staticmethod
    def encode_frames_to_webm(frames_dir: str, output_file: Path):
        subprocess.run([
            "ffmpeg",
            "-y",
            "-framerate", str(Const.FPS),
            "-i", os.path.join(frames_dir, "frame_%05d.png"),
            "-c:v", "libvpx-vp9",
            "-b:v", "2M",
            str(output_file.with_suffix(".webm")),
        ], check=True)

    @staticmethod
    def encode_frames_to_avi(frames_dir: str, output_file: Path):
        subprocess.run([
            "ffmpeg",
            "-y",
            "-framerate", str(Const.FPS),
            "-i", os.path.join(frames_dir, "frame_%05d.png"),
            "-c:v", "mpeg4",
            str(output_file.with_suffix(".avi")),
        ], check=True)