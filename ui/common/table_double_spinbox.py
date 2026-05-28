from PySide6.QtWidgets import QDoubleSpinBox

class TableDoubleSpinbox(QDoubleSpinBox):
    # Disable mouse wheel interaction cause I hate that
    def wheelEvent(self, event):
        event.ignore()