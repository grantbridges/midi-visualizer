from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QVBoxLayout
)

from common import Const
import build_info
from utility import FileUtil

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {Const.APP_NAME}")
        self.setModal(True)
        self.setFixedSize(360, 100)

        icon_label = QLabel()
        icon_path = FileUtil.get_assets_dir() / "illustri-icon.png"
        pixmap = QPixmap(str(icon_path))
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        name_label = QLabel(f"{Const.APP_NAME} by {Const.ORG_NAME}")
        version_label = QLabel(f"Version {build_info.VERSION} - Built {build_info.BUILD_DATE}")

        text_layout = QVBoxLayout()
        text_layout.addWidget(name_label)
        text_layout.addWidget(version_label)
        text_layout.addStretch(1)

        content_layout = QHBoxLayout()
        content_layout.addWidget(icon_label)
        content_layout.addLayout(text_layout, 1)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(content_layout)
        main_layout.addWidget(button_box)