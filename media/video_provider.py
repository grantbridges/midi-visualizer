from dataclasses import dataclass, field
import math
import cv2
from PySide6.QtGui import QImage
from PySide6.QtCore import QObject, Signal, Slot, QThread
from utility.util import Util
from models import Resolution

import logging
logger = logging.getLogger("VideoProvider")

class VideoProvider(QObject):
    '''
    Used for loading background video into memory for preview purposes,
    NOT for ultimately rendering the final export - for that, we layer the
    original video (full resolution) underneath the rest of the rendered visuals. So to
    save on memory, we can take some shortcuts here like reducing FPS of loaded
    video and lowering resolution/quality of cached images.
    '''
    # signals for reporting load progress
    load_finished = Signal()
    load_failed = Signal(str) # error message
    load_progress = Signal(int) # percent

    def __init__(self):
        super().__init__()

        self.frames: list[QImage] = []
        self.duration_s: float = 0.0

        # preview limits
        self.preview_fps: float = 16.0
        self.preview_res: Resolution = Resolution.Low
        self.preview_res_pixels = math.prod(self.preview_res.value)

        # thread stuff
        self.video_load_thread: QThread | None = None
        self.video_load_worker: VideoLoadWorker | None = None

    def init(self):
        logger.info(f"Initializing")

    def clear(self):
        self.frames = []
        self.duration_s = 0.0

    def load_video(self, video_path: str):
        logger.info(f"Loading video preview data from \"{video_path}\"")
        self.clear()

        # Set up threaded worker to load video
        self.video_load_thread = QThread(self)
        self.video_load_worker = VideoLoadWorker(video_path, self.preview_fps, self.preview_res_pixels)

        self.video_load_worker.moveToThread(self.video_load_thread)
        self.video_load_thread.started.connect(self.video_load_worker.run)

        # connect callbacks
        self.video_load_worker.finished.connect(self._on_video_loaded)       
        self.video_load_worker.failed.connect(self._on_video_load_failed)
        self.video_load_worker.progress.connect(self._on_video_load_progress)

        # cleanup thread on any result
        self.video_load_worker.finished.connect(self.video_load_thread.quit)
        self.video_load_worker.failed.connect(self.video_load_thread.quit)

        self.video_load_thread.start()
    
    def get_frame(self, time_s: float, loop: bool) -> QImage | None:
        if not self.frames or self.duration_s <= 0:
            return None
        
        if not loop:
            # return first or last frame if at the end
            if time_s < 0.0:
                return self.frames[0]
            elif time_s > self.duration_s:
                return self.frames[-1]

        # apply loop
        t = time_s % self.duration_s

        index = int(t * self.preview_fps)
        index = Util.clamp(index, 0, len(self.frames) - 1)

        return self.frames[index]
    
    # video load worker event callbacks
    def _on_video_loaded(self, result: VideoLoadResult):
        self.frames = result.frames
        self.duration_s = result.duration_s
        logger.info(f"Loaded video preview ({len(self.frames)} frames, {self.duration_s:.2f} sec)")
        
        self.load_finished.emit()

    def _on_video_load_failed(self, error: str):
        logger.info(f"Failed to load video preview: {error}")
        self.load_failed.emit(error)

    def _on_video_load_progress(self, percent: int):
        self.load_progress.emit(percent)
    
@dataclass
class VideoLoadResult:
    frames: list[QImage] = field(default_factory=list)
    duration_s: float = 0.0
    
class VideoLoadWorker(QObject):
    finished = Signal(VideoLoadResult) # list[QImage]
    failed = Signal(str) # error message
    progress = Signal(int) # percent

    def __init__(self, video_path: str, preview_fps: float, preview_res_pixels: int):
        super().__init__()
        self.video_path = video_path
        self.preview_fps = preview_fps
        self.preview_res_pixels = preview_res_pixels

    @Slot()
    def run(self):
        try:
            result = VideoLoadResult()

            cap = cv2.VideoCapture(self.video_path)

            if not cap.isOpened():
                self.failed.emit(f"Could not open video file")
                return
            
            source_fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if source_fps <= 0:
                self.failed.emit(f"Video FPS could not be determined")
                return

            result.duration_s = frame_count / source_fps

            # only store frames that hit our preview fps
            frame_interval = source_fps / self.preview_fps
            source_frame_index = 0
            next_keep_frame = 0.0

            while True:
                success, frame = cap.read()
                if not success:
                    break

                if source_frame_index >= next_keep_frame:
                    # keep this frame - iterate for next one we want
                    next_keep_frame += frame_interval

                    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    frame_pixels = frame_width * frame_height

                    if frame_pixels > self.preview_res_pixels:
                        # need to scale down to reach preview resolution
                        scale = math.sqrt(self.preview_res_pixels / frame_pixels)

                        new_width = max(1, int(frame_width * scale))
                        new_height = max(1, int(frame_height * scale))

                        frame = cv2.resize(
                            frame,
                            (new_width, new_height),
                            interpolation=cv2.INTER_AREA,
                        )

                    # OpenCV gives BGR; Qt wants RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    h, w, ch = frame_rgb.shape
                    bytes_per_line = ch * w
                    image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()

                    result.frames.append(image)                
                    
                source_frame_index += 1
                percent = int((source_frame_index / frame_count) * 100)
                self.progress.emit(percent)

            cap.release()

            if not result.frames:
                self.failed.emit("No frames were loaded from video")
                return
            
            self.finished.emit(result)
        except Exception:
            logger.exception("Failed to load video")
            self.failed.emit("An unknown error occurred")

# module-level singleton instance
video_provider = VideoProvider()