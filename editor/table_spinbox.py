from PySide6.QtWidgets import QSpinBox

class TableSpinbox(QSpinBox):
    # Disable mouse wheel interaction cause I hate that
    def wheelEvent(self, event):
        event.ignore()