import math
import threading

from PySide6.QtCore import QObject, QRect, Qt, Signal, Slot
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from models import VisConfig, RenderFormat, BackgroundMode
from pathlib import Path
from PySide6.QtGui import QImage, QPainter
from render.midi_render_util import MidiRenderUtil
from dataclasses import dataclass
import uuid
import tempfile
import subprocess
import os

import logging
logger = logging.getLogger("Render")

# If True and using a BG image, generate a fresh QImage from the 
# provided BG image filepath on each frame. Otherwise, layer in the
# image during video encoding. The latter is far more efficeint,
# but if we ever want to do fancier things with background images,
# we'll need to do the per-frame drawing.
RENDER_BG_IMAGE_EACH_FRAME = False

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

@dataclass(frozen=True)
class RenderFrameJobOutput:
    frame_index: int
    frame_bytes: bytes

class RenderWorker(QObject):
    progress = Signal(int, str) # percent, message
    finished = Signal()
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, vis_config: VisConfig):
        super().__init__()
        self.vis_config: VisConfig = vis_config
        (self.width, self.height) = self.vis_config.export_resolution.value
        self._cancel_requested = False
        self._cancel_event = threading.Event()

    @Slot()
    def run(self):
        try:
            success = False

            logger.info(
                f"Beginning output render of {self.vis_config.track_name} "
                f"to \"{self.vis_config.get_exported_filepath()}\" "
                f"(Res: {self.vis_config.export_resolution.name}; {self.vis_config.export_fps} FPS)"
            )

            # create output filepath
            temp_output_file = Path(tempfile.gettempdir()) / f"midi_render_{uuid.uuid4()}.{self.vis_config.export_format.value}"

            start_time = self.vis_config.get_min_time()
            end_time = self.vis_config.get_max_time()
            pitch_min = self.vis_config.get_min_pitch()
            pitch_max = self.vis_config.get_max_pitch()

            midi_delay_ms = max(0, int((-start_time) * 1000))
            ffmpeg = RenderWorker.open_ffmpeg_rawvideo_process(
                vis_config=self.vis_config,
                midi_delay_ms=midi_delay_ms,
                output_file=temp_output_file
            )
            logger.debug(f"Starting ffmpeg process (pid: {ffmpeg.pid})")

            # track next frame index to submit for rendering and next 
            # completed frame index to write to ffmpeg process sequentially
            next_frame_to_submit = 0
            next_frame_to_write = 0

            # set of render jobs to run
            pending_futures = set()
            # buffer of completed frame index and its raw bytes
            completed_buffer: dict[int, bytes] = {}

            max_workers = max(1, (os.cpu_count() or 1) // 2)
            max_buffered_frames = RenderWorker.get_max_buffered_frames(self.width, self.height, 512)
            logger.debug(f"Using {max_workers} workers; max {max_buffered_frames} buffered frames")

            total_frames = max(1, math.ceil((end_time - start_time) * self.vis_config.export_fps))
            
            def submit_frames_for_render(executor: ThreadPoolExecutor) -> None:
                '''
                Fills up frame buffer with as many render jobs as will fit
                '''
                nonlocal next_frame_to_submit

                while (
                    next_frame_to_submit < total_frames
                    and len(pending_futures) + len(completed_buffer) < max_buffered_frames
                    and not self._cancel_event.is_set()
                ):
                    # create new job for the next available frame and add to our tasks
                    job = RenderFrameJobInput(
                        frame_index = next_frame_to_submit,
                        vis_config=self.vis_config,
                        pitch_min=pitch_min,
                        pitch_max=pitch_max,
                        width=self.width,
                        height=self.height,
                        start_time=start_time,
                        end_time=end_time
                    )

                    future = executor.submit(
                        RenderWorker.render_frame_job,
                        job,
                        self._cancel_event,
                    )

                    pending_futures.add(future)
                    next_frame_to_submit += 1

            try:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    submit_frames_for_render(executor)

                    while next_frame_to_write < total_frames:
                        if self._cancel_event.is_set():
                            break

                        if not pending_futures:
                            if next_frame_to_write in completed_buffer:
                                pass
                            else:
                                raise RuntimeError(f"Missing frame {next_frame_to_write}")

                        done, pending_futures = wait(
                            pending_futures,
                            return_when=FIRST_COMPLETED,
                        )

                        for future in done:
                            output = future.result()

                            if output is None:
                                continue

                            completed_buffer[output.frame_index] = output.frame_bytes
                        
                        # Drain completed frames in strict order.
                        while next_frame_to_write in completed_buffer:
                            frame_bytes = completed_buffer.pop(next_frame_to_write)

                            expected_size = self.width * self.height * 4
                            if len(frame_bytes) != expected_size:
                                raise RuntimeError(
                                    f"Frame {next_frame_to_write} has invalid byte size. "
                                    f"Expected {expected_size}, got {len(frame_bytes)}."
                                )

                            try:
                                ffmpeg.stdin.write(frame_bytes)
                            except BrokenPipeError as exc:
                                raise RuntimeError(
                                    "FFmpeg closed stdin while frames were being written."
                                ) from exc

                            # emit progress event
                            next_frame_to_write += 1
                            percent = int((next_frame_to_write / total_frames) * 100)
                            self.progress.emit(percent, f"Rendering frames...")

                        submit_frames_for_render(executor)
            finally:
                try:
                    logger.info("Closing ffmpeg process")
                    ffmpeg.stdin.close()
                except Exception as e:
                    logger.warning(f"Unable to close ffmpeg stdin - ignoring: {str(e)}")
                    pass

                stderr = ffmpeg.stderr.read().decode("utf-8", errors="replace") if ffmpeg.stderr else ""

                return_code = ffmpeg.wait()

                if not self._cancel_event.is_set():
                    if return_code != 0:
                        raise RuntimeError(f"FFmpeg failed with exit code {return_code}.\n\n{stderr}")

            if self._cancel_requested:
                logger.info("Handling render cancel request")
                self.cancelled.emit()
                return

            # define output file path - delete if already exists
            output_file = self.vis_config.get_exported_filepath()
            output_file.unlink(missing_ok=True)
            # move temp file to output location and rename
            Path(temp_output_file).replace(output_file)

            logger.info(f"Finished output render to \"{self.vis_config.get_exported_filepath()}")

            success = True
            self.finished.emit()
        except Exception as e:
            logger.exception("Render failed")
            self.failed.emit(str(e))
        finally:
            if not success and temp_output_file is not None:
                logger.info("Cleaning up temp output file")
                # clean up temp output file if still hanging around
                temp_output_file.unlink(missing_ok=True)

    def cancel(self):
        self._cancel_requested = True
        self._cancel_event.set()

    @staticmethod
    def render_frame_job(job: RenderFrameJobInput, cancel_event) -> RenderFrameJobOutput | None:
        if cancel_event.is_set():
            return

        image = QImage(job.width, job.height, QImage.Format_RGBA8888)
        image.fill(Qt.transparent)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        try:
            current_time = job.start_time + job.frame_index / job.vis_config.export_fps
            rect = QRect(0, 0, job.width, job.height)

            if job.vis_config.bg_mode == BackgroundMode.Color:
                MidiRenderUtil.draw_color_background(painter, job.vis_config, rect)
            elif job.vis_config.bg_mode == BackgroundMode.Image:
                has_bg_image = (
                    RENDER_BG_IMAGE_EACH_FRAME
                    and bool(job.vis_config.bg_image_filepath)
                    and Path(job.vis_config.bg_image_filepath).is_file()
                )
                if has_bg_image:
                    painter.drawImage(rect, QImage(job.vis_config.bg_image_filepath))
            # don't handle BG video here - that will get layered in during video construction

            MidiRenderUtil.draw_background_tint(painter, job.vis_config, rect)
            MidiRenderUtil.draw_notes(painter, current_time, job.vis_config, job.pitch_min, job.pitch_max, rect)
            MidiRenderUtil.draw_waveform(painter, current_time, job.vis_config, rect)
            MidiRenderUtil.draw_fade_overlay(painter, current_time, job.start_time, job.end_time, job.vis_config, rect)
        except Exception:
            logger.exception("RenderFrame | Render frame failed")
            raise
        finally:
            painter.end()

        if cancel_event.is_set():
            return
        
        expected_size = job.width * job.height * 4
        frame_bytes = image.constBits().tobytes()

        if len(frame_bytes) != expected_size:
            raise RuntimeError(
                f"Invalid frame byte size. Expected {expected_size}, got {len(frame_bytes)}."
            )

        return RenderFrameJobOutput(
            frame_index=job.frame_index,
            frame_bytes=frame_bytes,
        )
    
    @staticmethod
    def open_ffmpeg_rawvideo_process(vis_config: VisConfig, midi_delay_ms: int, output_file: Path) -> subprocess.Popen:
        width, height = vis_config.export_resolution.value

        loop_video = vis_config.bg_video_loop
        bg_video_start_delay_sec = (midi_delay_ms / 1000 + vis_config.bg_video_time_offset)

        has_audio = vis_config.has_audio()

        has_bg_image = (
            not RENDER_BG_IMAGE_EACH_FRAME
            and vis_config.bg_mode == BackgroundMode.Image
            and bool(vis_config.bg_image_filepath)
            and Path(vis_config.bg_image_filepath).is_file()
        )

        has_bg_video = (
            vis_config.bg_mode == BackgroundMode.Video
            and bool(vis_config.bg_video_filepath)
            and Path(vis_config.bg_video_filepath).is_file()
        )

        has_background = has_bg_image or has_bg_video

        cmd = [
            "ffmpeg",
            "-y",

            # input 0: rendered MIDI overlay frames from stdin
            "-f", "rawvideo",
            "-pix_fmt", "rgba",
            "-s", f"{width}x{height}",
            "-r", str(vis_config.export_fps),
            "-i", "-",
        ]

        input_index = 1
        bg_image_input_index = None
        bg_video_input_index = None
        audio_input_index = None

        if has_bg_image:
            bg_image_input_index = input_index
            input_index += 1

            cmd += [
                "-loop", "1",
                "-i", str(vis_config.bg_image_filepath),
            ]

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

        filter_parts: list[str] = []

        if has_background:
            # MIDI overlay frames + transparent timing base
            filter_parts.append(
                "[0:v]format=rgba,split=2[midi][base0]"
            )

            filter_parts.append(
                "[base0]colorchannelmixer=aa=0[base]"
            )

            if has_bg_image:
                filter_parts.append(
                    f"[{bg_image_input_index}:v]"
                    f"scale={width}:{height},"
                    f"setsar=1,"
                    f"format=rgba"
                    f"[bg]"
                )

                # bg image is looped/infinite, so shortest=1 is important
                shortest_flag = 1

            elif has_bg_video:
                filter_parts.append(
                    f"[{bg_video_input_index}:v]"
                    f"scale={width}:{height},"
                    f"setsar=1,"
                    f"setpts=PTS+{bg_video_start_delay_sec}/TB,"
                    f"format=rgba"
                    f"[bg]"
                )

                # when looping, we need shortest so video won't loop forever
                shortest_flag = 1 if loop_video else 0

            filter_parts.append(
                f"[base][bg]overlay=0:0:"
                f"eof_action=repeat:"
                f"shortest={shortest_flag}"
                f"[bgbase]"
            )

            filter_parts.append(
                f"[bgbase][midi]overlay=0:0:"
                f"format=auto:"
                f"shortest={shortest_flag}"
                f"[v]"
            )

        if has_audio:
            filter_parts.append(
                f"[{audio_input_index}:a]"
                f"adelay={midi_delay_ms}:all=1"
                f"[a]"
            )

        if filter_parts:
            cmd += [
                "-filter_complex",
                ";".join(filter_parts),
            ]

            if has_background:
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
                raise ValueError(
                    f"Unsupported render format: {vis_config.export_format}"
                )

        cmd.append(str(output_file))

        return subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    
    # -- helpers --
    @staticmethod
    def get_max_buffered_frames(width: int, height: int, max_memory_mb: int) -> int:
        '''
        Computes ideal max computed frames such that we never exceed
        provided memory limit
        '''
        bytes_per_frame = width * height * 4
        max_bytes = max_memory_mb * 1024 * 1024

        return max(1, max_bytes // bytes_per_frame)