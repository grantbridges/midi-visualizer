from dataclasses import dataclass
from pathlib import Path
from PySide6.QtGui import QImage

'''
Used for loading background image in preview mode - NOT for rendering
'''
@dataclass
class ImageProvider:
    image: QImage | None = None

    def init(self):
        pass

    def clear(self):
        self.image = None

    def load_image(self, image_path: str):
        if Path(image_path).is_file():
            print(f"ImageProvider | Loading image from \"{image_path}\"")
            self.image = QImage(image_path)
            print(f"ImageProvider | Loaded image")

    def get_image(self) -> QImage | None:
        return self.image

# module-level singleton instance
image_provider = ImageProvider()