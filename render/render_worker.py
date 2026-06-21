from PySide6.QtCore import QObject, QRect, Qt, Signal, Slot
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Manager
from common import Const
from models import VisConfig, RenderFormat, BackgroundMode
from pathlib import Path
from PySide6.QtGui import QImage, QPainter
from render.midi_render_util import MidiRenderUtil
from dataclasses import dataclass
import uuid
import tempfile
import shutil
import os
import subprocess

@dataclass(frozen=True)
class RenderFrameJobInput:
    frame_index: int
    vis_config: VisConfig
    pitch_min: int
    pitch_max: int
    width: int
    height: int
    start_time: float
    end_time: float
    frames_dir: str

class RenderWorker(QObject):
    progress = Signal(int, str) # percent, message
    finished = Signal()
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, vis_config: VisConfig):
        super().__init__()
        self.vis_config: VisConfig = vis_config
        (self.width, self.height) = self.vis_config.export_resolution
        self._cancel_requested = False

    @Slot()
    def run(self):
        try:
            with Manager() as manager:
                cancel_event = manager.Event()

                # build temp directory for storing image frames in
                frames_dir = tempfile.mkdtemp()

                try:
                    start_time = self.vis_config.get_min_time()
                    end_time = self.vis_config.get_max_time()
                    pitch_min = self.vis_config.get_min_pitch()
                    pitch_max = self.vis_config.get_max_pitch()

                    # build render frame job for every frame
                    total_frames = int((end_time - start_time) * self.vis_config.export_fps)
                    jobs = [
                        RenderFrameJobInput(
                            frame_index = i, 
                            vis_config=self.vis_config, 
                            pitch_min=pitch_min, 
                            pitch_max=pitch_max, 
                            width=self.width,
                            height=self.height,
                            start_time=start_time,
                            end_time=end_time,
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

                    if self._cancel_requested:
                        return

                    self.progress.emit(None, f"Encoding {self.vis_config.export_format.value} file...")

                    # create output filepath - delete if already exists
                    temp_output_file = Path(tempfile.gettempdir()) / f"midi_render_{uuid.uuid4()}.{self.vis_config.export_format.value}"

                    # delay until midi actually crosses playhead for first time
                    midi_delay_ms = max(0, int((-start_time) * 1000))
                    RenderWorker.encode_frames_to_video(frames_dir, self.vis_config, midi_delay_ms, temp_output_file)

                    if self._cancel_requested:
                        return

                    # define output file path - delete if already exists
                    output_file = self.vis_config.get_exported_filepath()
                    output_file.unlink(missing_ok=True)

                    # move temp file to output location and rename
                    Path(temp_output_file).replace(output_file)

                    self.finished.emit()
                finally:
                    shutil.rmtree(frames_dir)

        except Exception as e:
            self.failed.emit(str(e))

    def cancel(self):
        self._cancel_requested = True

    @staticmethod
    def render_frame_job(job: RenderFrameJobInput, cancel_event):
        if cancel_event.is_set():
            return

        try:
            current_time = job.start_time + job.frame_index / job.vis_config.export_fps

            image = QImage(job.width, job.height, QImage.Format_ARGB32)
            image.fill(Qt.transparent)
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)
            rect = QRect(0, 0, job.width, job.height)

            if job.vis_config.bg_mode == BackgroundMode.Color:
                MidiRenderUtil.draw_color_background(painter, job.vis_config, rect)
            elif job.vis_config.bg_mode == BackgroundMode.Image:
                has_bg_image = (
                    bool(job.vis_config.bg_image_filepath)
                    and Path(job.vis_config.bg_image_filepath).is_file()
                )
                if has_bg_image:
                    painter.drawImage(rect, QImage(job.vis_config.bg_image_filepath))
            # don't handle BG video here - that will get layered in during video construction

            MidiRenderUtil.draw_background_tint(painter, job.vis_config, rect)
            MidiRenderUtil.draw_notes(painter, current_time, job.vis_config, job.pitch_min, job.pitch_max, rect)
            MidiRenderUtil.draw_fade_overlay(painter, current_time, job.start_time, job.end_time, job.vis_config, rect)
            
            painter.end()

            if cancel_event.is_set():
                return

            # save image file to disk
            path = Path(job.frames_dir).joinpath(f"frame_{job.frame_index:05d}.png")
            image.save(str(path))
        except Exception as e:
            print(f'Render Frame | Error | {e}')

        return job.frame_index
    
    @staticmethod
    def encode_frames_to_video(frames_dir: str, vis_config: VisConfig, midi_delay_ms: int, output_file: Path):
        loop_video = vis_config.bg_video_loop
        bg_video_start_delay_sec = midi_delay_ms / 1000 + vis_config.bg_video_time_offset

        has_audio = vis_config.has_audio()

        has_bg_video = (
            vis_config.bg_mode == BackgroundMode.Video
            and bool(vis_config.bg_video_filepath)
            and Path(vis_config.bg_video_filepath).is_file()
        )

        cmd = [
            "ffmpeg",
            "-y",

            # input 0: rendered MIDI overlay frames
            "-framerate", str(vis_config.export_fps),
            "-i", os.path.join(frames_dir, "frame_%05d.png"),
        ]

        input_index = 1
        bg_video_input_index = None
        audio_input_index = None

        if has_bg_video:
            if loop_video:
                cmd += ["-stream_loop", "-1"]

            bg_video_input_index = input_index
            input_index += 1

            cmd += [
                "-i", str(vis_config.bg_video_filepath),
            ]

        if has_audio:
            audio_input_index = input_index
            input_index += 1

            cmd += [
                "-i", str(vis_config.audio_filepath),
            ]

        filter_parts = []

        # If using video background:
        # - create a transparent base using the rendered frame sequence
        # - draw bg video onto that base
        # - draw MIDI overlay frames on top
        if has_bg_video:
            width, height = vis_config.export_resolution.value

            filter_parts.append(
                "[0:v]format=rgba,split=2[midi][base0]"
            )

            filter_parts.append(
                "[base0]colorchannelmixer=aa=0[base]"
            )

            filter_parts.append(
                f"[{bg_video_input_index}:v]"
                f"scale={width}:{height},"
                f"setsar=1,"
                f"setpts=PTS+{bg_video_start_delay_sec}/TB,"
                f"format=rgba"
                f"[bg]"
            )

            # when looping, we need "shortest" so video won't loop forever
            shortest_flag = 1 if loop_video else 0
            filter_parts.append(
                f"[base][bg]overlay=0:0:eof_action=repeat:shortest={shortest_flag}[bgbase]"
            )

            filter_parts.append(
                f"[bgbase][midi]overlay=0:0:format=auto:shortest={shortest_flag}[v]"
            )

        # If using audio, delay it.
        if has_audio:
            filter_parts.append(
                f"[{audio_input_index}:a]adelay={midi_delay_ms}:all=1[a]"
            )

        if filter_parts:
            cmd += [
                "-filter_complex",
                ";".join(filter_parts),
            ]

            if has_bg_video:
                cmd += ["-map", "[v]"]
            else:
                cmd += ["-map", "0:v"]

            if has_audio:
                cmd += ["-map", "[a]"]

        match vis_config.export_format:
            case RenderFormat.MP4:
                cmd += [
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                ]
                if has_audio:
                    cmd += ["-c:a", "aac"]

            case RenderFormat.MOV:
                cmd += [
                    "-c:v", "prores_ks",
                    "-profile:v", "3",
                ]
                if has_audio:
                    cmd += ["-c:a", "aac"]

            case RenderFormat.WEBM:
                cmd += [
                    "-c:v", "libvpx-vp9",
                    "-b:v", "2M",
                ]
                if has_audio:
                    cmd += ["-c:a", "libopus"]

            case _:
                raise ValueError(f"Unsupported render format: {vis_config.export_format}")

        cmd.append(str(output_file))

        subprocess.run(cmd, check=True)