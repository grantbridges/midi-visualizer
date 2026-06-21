from dataclasses import dataclass, field
import math
import cv2
from PySide6.QtGui import QImage
from utility.util import Util
from models import Resolution

'''
Used for loading background video into memory for preview purposes,
NOT for ultimately rendering the final export - for that, we layer the
original video underneath the rest of the rendered visuals. So to
save on memory, we can take some shortcuts here like reducing FPS of loaded
video and lowering quality of cached images.
'''
@dataclass
class VideoProvider:
    # calculated from loaded video
    frames: list[QImage] = field(default_factory=list)
    source_fps: float = 0.0
    duration_s: float = 0.0

    # preview limits
    preview_fps: float = 16.0
    preview_res: Resolution = Resolution.Low
    preview_res_pixels: int = 0 # computed on init

    def init(self):
        self.preview_res_pixels = math.prod(self.preview_res.value)

    def clear(self):
        self.frames = []
        self.source_fps = 0.0
        self.duration_s = 0.0

    # loads provided video into array of frames
    def load_video(self, video_path: str):
        print(f"VideoProvider | Loading video data from \"{video_path}\"")
        self.clear()

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"VideoProvider | Error | Could not open video file: {video_path}")
        
        self.source_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if self.source_fps <= 0:
            raise ValueError("VideoProvider | Error | Video FPS could not be determined")

        self.duration_s = frame_count / self.source_fps

        # only store frames that hit our preview fps
        frame_interval = self.source_fps / self.preview_fps
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

                self.frames.append(image)                
                
            source_frame_index += 1

        cap.release()

        if not self.frames:
            raise ValueError("VideoProvider | Error | No frames were loaded from video")
        
        print(f"VideoProvider | Loaded video ({len(self.frames)} frames, {self.duration_s:.2f} sec)")
    
    def get_frame(self, time_s: float, loop: bool) -> QImage | None:
        if not self.frames or self.duration_s <= 0:
            return None
        
        if not loop:
            if time_s < 0.0:
                return self.frames[0]
            elif time_s > self.duration_s:
                return self.frames[-1]

        # loop
        t = time_s % self.duration_s

        index = int(t * self.preview_fps)
        index = Util.clamp(index, 0, len(self.frames) - 1)

        return self.frames[index]

# module-level singleton instance
video_provider = VideoProvider()