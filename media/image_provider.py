from dataclasses import dataclass
from pathlib import Path
from PySide6.QtGui import QImage

import logging
logger = logging.getLogger("ImageProvider")

'''
Used for loading background image in preview mode - NOT for rendering
'''
@dataclass
class ImageProvider:
    image: QImage | None = None

    def init(self):
        logger.info(f"Initializing")

    def clear(self):
        self.image = None

    def load_image(self, image_path: str):
        try:
            if Path(image_path).is_file():
                logger.info(f"Loading image from \"{image_path}\"")
                self.image = QImage(image_path)
        except Exception:
            logger.exception("Failed to load image")
            raise

    def get_image(self) -> QImage | None:
        return self.image

# module-level singleton instance
image_provider = ImageProvider()