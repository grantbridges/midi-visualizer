from dataclasses import dataclass, field
import math
from pathlib import Path
import subprocess
import numpy as np
from typing import List

import logging

from pympler import asizeof
logger = logging.getLogger("Waveform")

@dataclass
class WaveformSample():
    min_amp: float = 0.0
    max_amp: float = 0.0

@dataclass
class Waveform():
    samples: List[WaveformSample] = field(default_factory=list)
    samples_px_per_sec: int = 100

    def get_sample_at_time(self, time: float) -> WaveformSample | None:
        index = int(time * self.samples_px_per_sec)

        if 0 <= index < len(self.samples):
            return self.samples[index]
        
        return None
    
    def clear(self):
        self.samples.clear()
    
    def load_from_audio(self, audio_path: str):
        self.clear()

        if not Path(audio_path).is_file():
            return

        sample_rate = 44100 # Hz

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

        samples_per_pixel = sample_rate / self.samples_px_per_sec
        total_pixels = math.ceil(len(samples) / samples_per_pixel)

        for x in range(total_pixels):
            # grab window range of samples needed for each pixel
            start = int(x * samples_per_pixel)
            end = int((x + 1) * samples_per_pixel)

            chunk = samples[start:end]

            sample = WaveformSample()
            if len(chunk) != 0:
                sample.min_amp = float(chunk.min())
                sample.max_amp = float(chunk.max())   
            
            self.samples.append(sample)

        size_bytes = asizeof.asizeof(self.samples)
        logger.info(f"Loaded audio waveform sample data ({len(self.samples)} samples at {self.samples_px_per_sec} px/sec, {size_bytes / 1024 / 1024:.3f} MB)")