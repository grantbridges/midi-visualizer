from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSlider, QStyle, QStyleOptionSlider, QWidget

class IllustriSlider(QSlider):
    def __init__(self, orientation: Qt.Orientation, parent: QWidget | None = None):
        super().__init__(orientation, parent)

        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # jump the handle straight to the click position instead of a page-step
            new_value = self._value_from_pos(event.position().toPoint())
            self.setValue(new_value)
            event.accept()
            
        super().mousePressEvent(event)

    def _value_from_pos(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        groove_rect = self.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self
        )
        handle_rect = self.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self
        )

        if self.orientation() == Qt.Horizontal:
            slider_length = handle_rect.width()
            slider_min = groove_rect.x()
            slider_max = groove_rect.right() - slider_length + 1
            pos_value = pos.x() - slider_length // 2
        else:
            slider_length = handle_rect.height()
            slider_min = groove_rect.y()
            slider_max = groove_rect.bottom() - slider_length + 1
            pos_value = pos.y() - slider_length // 2

        return QStyle.sliderValueFromPosition(
            self.minimum(),
            self.maximum(),
            pos_value - slider_min,
            slider_max - slider_min,
        )