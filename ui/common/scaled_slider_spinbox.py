from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import QSpinBox, QWidget, QHBoxLayout, QSlider

class ScaledSliderSpinbox(QWidget):
    valueChanged = Signal(int)

    SPINBOX_WIDTH = 90

    def __init__(
        self,
        display_min: int,
        display_max: int,
        internal_min: int,
        internal_max: int,
        internal_value: int | None = None,
        suffix: str | None = None,
        disable_mouse_wheel: bool = False,
        parent: QWidget | None = None
    ):
        super().__init__(parent)

        if display_max == display_min:
            raise ValueError("display_max cannot equal display_min")

        if internal_max == internal_min:
            raise ValueError("internal_max cannot equal internal_min")

        # store internals
        self._display_min = display_min
        self._display_max = display_max
        self._internal_min = internal_min
        self._internal_max = internal_max
        self._disable_mouse_wheel = disable_mouse_wheel

        # configure spinbox
        self._spinbox = QSpinBox(self)
        if suffix is not None:
            self._spinbox.setSuffix(suffix)
        self._spinbox.setFixedWidth(self.SPINBOX_WIDTH)
        self._spinbox.setMinimum(self._display_min)
        self._spinbox.setMaximum(self._display_max)

        # configure slider
        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.setMinimum(self._display_min)
        self._slider.setMaximum(self._display_max)

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

        self.setInternalValue(internal_value)

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
        self.valueChanged.emit(self.getInternalValue())

    def _on_spinbox_changed(self, value: int):
        # update slider
        self._slider.blockSignals(True)
        self._slider.setValue(value)
        self._slider.blockSignals(False)

        # emit internal value
        self.valueChanged.emit(self.getInternalValue())

    # --- Public API ---

    def setInternalValue(self, val: int | None):
        # convert to display and set on spinbox
        if val is None:
            return

        t = (val - self._internal_min) / (self._internal_max - self._internal_min)
        display_value = self._display_min + t * (self._display_max - self._display_min)

        # Setting the spinbox triggers _on_spinbox_changed, which syncs the slider
        self._spinbox.setValue(int(round(display_value)))

    def getInternalValue(self) -> int:
        # convert from spinbox's stored display value back to internal
        t = (self._spinbox.value() - self._display_min) / (self._display_max - self._display_min)
        internal_value = self._internal_min + t * (self._internal_max - self._internal_min)

        return int(round(internal_value))