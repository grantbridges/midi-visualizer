from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import QSpinBox, QWidget, QHBoxLayout
from ui.common.illustri_slider import IllustriSlider

class SliderSpinbox(QWidget):
    valueChanged = Signal(int)

    SPINBOX_WIDTH = 90

    def __init__(
        self,
        minimum: int,
        maximum: int,
        value: int | None = None,
        suffix: str | None = None,
        disable_mouse_wheel: bool = False,
        parent: QWidget | None = None
    ):
        super().__init__(parent)

        self._disable_mouse_wheel = disable_mouse_wheel

        # configure spinbox
        self._spinbox = QSpinBox(self)
        if suffix is not None:
            self._spinbox.setSuffix(suffix)
        self._spinbox.setFixedWidth(self.SPINBOX_WIDTH)
        self._spinbox.setMinimum(minimum)
        self._spinbox.setMaximum(maximum)

        # configure slider
        self._slider = IllustriSlider(Qt.Horizontal, self)
        self._slider.setMinimum(minimum)
        self._slider.setMaximum(maximum)

        # intercept events
        self._slider.installEventFilter(self)
        self._spinbox.installEventFilter(self)

        # layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._slider, stretch=1)
        layout.addWidget(self._spinbox, stretch=0)

        # sync signals
        self._slider.valueChanged.connect(self._on_slider_changed)
        self._spinbox.valueChanged.connect(self._on_spinbox_changed)

        if value is not None:
            self.setValue(value)

    def eventFilter(self, obj, event):
        if self._disable_mouse_wheel:
            if event.type() == QEvent.Wheel and obj in (self._slider, self._spinbox):
                return True  # swallow the event, don't propagate
        
        return super().eventFilter(obj, event)

    # --- Internal sync handlers ---

    def _on_slider_changed(self, value: int):
        # update spinbox
        self._spinbox.blockSignals(True)
        self._spinbox.setValue(value)
        self._spinbox.blockSignals(False)

        # emit internal value
        self.valueChanged.emit(value)

    def _on_spinbox_changed(self, value: int):
        # update slider
        self._slider.blockSignals(True)
        self._slider.setValue(value)
        self._slider.blockSignals(False)

        # emit internal value
        self.valueChanged.emit(value)

    # --- Public API ---

    def value(self) -> int:
        return self._spinbox.value()

    def setValue(self, value: int):
        # Setting the spinbox triggers _on_spinbox_changed, which syncs the slider
        self._spinbox.setValue(value)
