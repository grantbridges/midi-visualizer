from PySide6.QtWidgets import QComboBox

class TableComboBox(QComboBox):
    # Disable mouse wheel interaction when not focused cause I hate that
    def wheelEvent(self, event):
        if not self.hasFocus():
            event.ignore()