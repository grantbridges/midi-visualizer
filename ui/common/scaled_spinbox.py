from PySide6.QtWidgets import QWidget, QSpinBox

class ScaledSpinbox(QSpinBox):
    '''
    Simple wrapper around QSpinBox that handles converting from internal 
    values to display and pulling converted internal value back out.
    Note: It's okay to have internal_max < internal_min if you want an inverse 
    relationship with the display values.
    '''
    def __init__(self, 
        display_min: int, 
        display_max: int, 
        internal_min: int, 
        internal_max: int, 
        # add more base class args here if needed
        internal_value: int | None = None,
        disable_mouse_wheel: bool = False,
        parent: QWidget | None = None
    ):
        super().__init__(parent)

        if display_max == display_min:
            raise ValueError("display_max cannot equal display_min")

        if internal_max == internal_min:
            raise ValueError("internal_max cannot equal internal_min")

        # store internals
        self.display_min = display_min
        self.display_max = display_max
        self.internal_min = internal_min
        self.internal_max = internal_max
        self.disable_mouse_wheel = disable_mouse_wheel

        self.setRange(display_min, display_max)
        self.setInternalValue(internal_value)

    def wheelEvent(self, event):
        if self.disable_mouse_wheel:
            event.ignore()
            return

        super().wheelEvent(event)

    def setInternalValue(self, val: int | None) -> None:
        # store as internal and convert to display
        display_value = self._internal_to_display(val)
        if display_value is not None:
            self.setValue(display_value)

    def getInternalValue(self) -> int:
        # convert from stored display value back to internal
        internal_value = self._display_to_internal(self.value())
        return internal_value

    def _internal_to_display(self, internal_value: int | None) -> int | None:
        if internal_value is None:
            return None

        t = (internal_value - self.internal_min) / (self.internal_max - self.internal_min)
        display_value = self.display_min + t * (self.display_max - self.display_min)
        return int(round(display_value))

    def _display_to_internal(self, display_value: int) -> int:
        t = (display_value - self.display_min) / (self.display_max - self.display_min)
        internal_value = self.internal_min + t * (self.internal_max - self.internal_min)
        return int(round(internal_value))