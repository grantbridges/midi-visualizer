from dataclasses import dataclass, field
import math
from pathlib import Path
import subprocess
import numpy as np
from utility import FileUtil
from typing import List

import logging

from pympler import asizeof
logger = logging.getLogger("Waveform")

@dataclass
class Waveform():
    # store min/max amplitudes in parallel arrays - will always be same size
    min_amps: np.ndarray = field(default_factory=lambda: np.array([], dtype=np.float32))
    max_amps: np.ndarray = field(default_factory=lambda: np.array([], dtype=np.float32))
    samples_px_per_sec: int = 120

    def get_sample_at_time(self, time: float) -> tuple[float, float] | None:
        '''
        Returns: (min amplitude, max amplitude) for given time, if available
        '''
        index = int(time * self.samples_px_per_sec)

        if 0 <= index < self.get_samples_length():
            return float(self.min_amps[index]), float(self.max_amps[index])

        return None
    
    def get_samples_length(self):
        return len(self.min_amps) # min/max are same size
    
    def clear(self):
        self.min_amps = []
        self.max_amps = []
    
    def load_from_audio(self, audio_path: str):
        self.clear()

        if not Path(audio_path).is_file():
            return

        sample_rate = 44100 # Hz

        # use ffmpeg to parse samples from audio file
        cmd = [
            FileUtil.get_ffmpeg_path(),
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

        raw_samples = np.frombuffer(result.stdout, dtype=np.float32)

        samples_per_pixel = sample_rate / self.samples_px_per_sec
        total_pixels = math.ceil(len(raw_samples) / samples_per_pixel)

        min_amps = []
        max_amps = []
        for x in range(total_pixels):
            # grab window range of samples needed for each pixel
            start = int(x * samples_per_pixel)
            end = int((x + 1) * samples_per_pixel)

            chunk = raw_samples[start:end]

            if len(chunk) == 0:
                min_amps.append(0.0)
                max_amps.append(0.0)
            else:
                min_amps.append(float(chunk.min()))
                max_amps.append(float(chunk.max()))

        self.min_amps = np.array(min_amps, dtype=np.float32)
        self.max_amps = np.array(max_amps, dtype=np.float32)

        size_bytes = asizeof.asizeof(self)
        logger.info(f"Loaded audio waveform sample data ({self.get_samples_length()} samples at {self.samples_px_per_sec} px/sec, {size_bytes / 1024 / 1024:.3f} MB)")