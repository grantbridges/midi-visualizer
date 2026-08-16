from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSlider, QDoubleSpinBox

class SliderDoubleSpinbox(QWidget):
    valueChanged = Signal(float)

    SPINBOX_WIDTH = 90

    def __init__(
        self,
        minimum: float,
        maximum: float,
        value: float | None = None,
        decimals: int = 2,
        singleStep: float = 0.01,
        suffix: str | None = None,
        disable_mouse_wheel: bool = False,
        parent: QWidget | None = None
    ):
        super().__init__(parent)

        self._disable_mouse_wheel = disable_mouse_wheel

        # for scaling slider positioning and mapping values
        self._scale = 10 ** decimals 

        # configure spinbox
        self._spinbox = QDoubleSpinBox(self)
        self._spinbox.setDecimals(decimals)
        self._spinbox.setSingleStep(singleStep)
        if suffix is not None:
            self._spinbox.setSuffix(suffix)
        self._spinbox.setFixedWidth(self.SPINBOX_WIDTH)
        self._spinbox.setMinimum(minimum)
        self._spinbox.setMaximum(maximum)

        # configure slider
        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.setCursor(Qt.PointingHandCursor)
        self._slider.setMinimum(round(minimum * self._scale))
        self._slider.setMaximum(round(maximum * self._scale))

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

    def _on_slider_changed(self, int_value: int):
        float_value = int_value / self._scale

        # update spinbox
        self._spinbox.blockSignals(True)
        self._spinbox.setValue(float_value)
        self._spinbox.blockSignals(False)

        # emit internal value
        self.valueChanged.emit(float_value)

    def _on_spinbox_changed(self, float_value: float):
        int_value = round(float_value * self._scale)

        # update slider
        self._slider.blockSignals(True)
        self._slider.setValue(int_value)
        self._slider.blockSignals(False)

        # emit internal value
        self.valueChanged.emit(float_value)

    # --- Public API ---

    def value(self) -> float:
        return self._spinbox.value()

    def setValue(self, value: float):
        # Setting the spinbox triggers _on_spinbox_changed, which syncs the slider
        self._spinbox.setValue(value)
