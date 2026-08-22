from PySide6.QtWidgets import QWidget, QDoubleSpinBox

class ScaledDoubleSpinBox(QDoubleSpinBox):
    '''
    Simple wrapper around QDoubleSpinBox that handles converting from internal 
    values to display and pulling converted internal value back out.
    Note: It's okay to have internal_max < internal_min if you want an inverse 
    relationship with the display values.

    Note: Signal emitted value returns display value, not internal.
    '''
    def __init__(
        self, 
        display_min: float,
        display_max: float,
        internal_min: float,
        internal_max: float,
        # add more base class args here if needed
        internal_value: float | None = None,
        decimals: int | None = None,
        singleStep: float | None = None,
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

        if decimals is not None:
            self.setDecimals(decimals)
        if singleStep is not None:
            self.setSingleStep(singleStep)
        if suffix is not None:
            self.setSuffix(suffix)

        self.setRange(display_min, display_max)
        self.setInternalValue(internal_value)

    def wheelEvent(self, event):
        if self._disable_mouse_wheel:
            event.ignore()
            return

        super().wheelEvent(event)

    def setInternalValue(self, val: float | None) -> None:
        # store as internal and convert to display
        display_value = self._internal_to_display(val)
        if display_value is not None:
            self.setValue(display_value)

    def getInternalValue(self) -> float:
        # convert from stored display value back to internal
        internal_value = self._display_to_internal(self.value())
        return internal_value

    def _internal_to_display(self, internal_value: float | None) -> float | None:
        if internal_value is None:
            return None

        t = (internal_value - self._internal_min) / (self._internal_max - self._internal_min)
        display_value = self._display_min + t * (self._display_max - self._display_min)
        return display_value

    def _display_to_internal(self, display_value: float) -> float:
        if display_value is None:
            return None

        t = (display_value - self._display_min) / (self._display_max - self._display_min)
        internal_value = self._internal_min + t * (self._internal_max - self._internal_min)
        return internal_value