from dataclasses import dataclass, field
import cv2
from PySide6.QtGui import QImage

@dataclass
class VideoProvider:
    frames: list[QImage] = field(default_factory=list)
    fps: float = 0.0
    duration_s: float = 0.0 # seconds

    def clear(self):
        self.frames = []
        self.fps = 0.0
        self.duration_s = 0.0

    # loads provided video into array of frames
    def load(self, video_path: str):
        self.frames.clear()

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if self.fps <= 0:
            raise ValueError("Video FPS could not be determined")

        self.duration_s = frame_count / self.fps

        while True:
            success, frame = cap.read()
            if not success:
                break

            # OpenCV gives BGR; Qt wants RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w

            image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()  # important: detach from numpy buffer
            self.frames.append(image)

        cap.release()

        if not self.frames:
            raise ValueError("No frames were loaded from video")
    
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

        index = int(t * self.fps)
        index = max(0, min(len(self.frames) - 1, index))

        return self.frames[index]

# module-level singleton instance
video_provider = VideoProvider()