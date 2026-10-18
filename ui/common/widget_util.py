from PySide6.QtGui import QIcon, QPalette, Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget
from ui.common.icons import Icons

class WidgetUtil:
    '''
    Utility for creating some common types of special case widgets
    '''
    def __new__(cls):
        raise TypeError("WidgetUtil is static")
        
    @staticmethod
    def hint_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignLeft)
        label.setForegroundRole(QPalette.PlaceholderText)

        font = label.font()
        font.setPointSizeF(font.pointSizeF() * 0.9)
        label.setFont(font)

        return label

    @staticmethod
    def info_text(text: str) -> QWidget:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignLeft)
        label.setContentsMargins(0, 1, 0, 0) # slight nudge down
        label.setForegroundRole(QPalette.PlaceholderText)

        font = label.font()
        font.setPointSizeF(font.pointSizeF() * 0.9)
        label.setFont(font)

        icon_label = QLabel()
        icon_size = int(font.pointSizeF() * 1.4)
        icon_label.setPixmap(Icons.info().pixmap(icon_size, icon_size))
        icon_label.setAlignment(Qt.AlignCenter)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(icon_label, 0, Qt.AlignVCenter)
        layout.addWidget(label, 1)

        return container
    
    @staticmethod
    def icon_btn(icon: QIcon, tooltip: str | None = None) -> QPushButton:
        btn = QPushButton()
        btn.setIcon(icon)
        btn.setStyleSheet("padding: 3px 3px")

        if tooltip is not None:
            btn.setToolTip(tooltip)

        return btn