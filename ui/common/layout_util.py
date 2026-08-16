from typing import List

from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QBoxLayout,
    QCheckBox,
    QComboBox,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QWidget,
)
from PySide6.QtCore import Qt

from ui.common import SectionDivider

class LayoutUtil:
    '''
    Utility for cleanly laying out common widgets with labels.
    Used extensively throughout tab layouts & dialogs for easy, common styling.
    '''
    def __new__(cls):
        raise TypeError("LayoutUtil is static")
        
    @staticmethod
    def section(parent_layout: QBoxLayout, label: str):
        parent_layout.addWidget(SectionDivider(label))

    @staticmethod
    def label(parent_layout: QBoxLayout, label: QLabel) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(label)
        parent_layout.addWidget(row)
        return row

    @staticmethod
    def checkbox(parent_layout: QBoxLayout, label: str, checkbox: QCheckBox) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(QLabel(label))
        h_layout.addStretch()
        h_layout.addWidget(checkbox)
        parent_layout.addWidget(row)
        return row

    @staticmethod
    def line_edit(parent_layout: QBoxLayout, label: str, edit: QLineEdit) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(QLabel(label), 1)
        h_layout.addWidget(edit, 1)
        parent_layout.addWidget(row)
        return row
    
    @staticmethod
    def line_edit_suffix(parent_layout: QBoxLayout, label: str, edit: QLineEdit, suffix: QLabel) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(QLabel(label), 1)

        right_side = QWidget()
        right_layout = QHBoxLayout(right_side)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        right_layout.addWidget(edit)
        right_layout.addWidget(suffix)
        h_layout.addWidget(right_side, 1)
        
        parent_layout.addWidget(row)
        return row

    @staticmethod
    def spinbox(parent_layout: QBoxLayout, label: str, spinbox: QAbstractSpinBox) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(QLabel(label), 1)
        h_layout.addWidget(spinbox, 1)
        parent_layout.addWidget(row)
        return row
    
    @staticmethod
    def combobox(parent_layout: QBoxLayout, label: str, combobox: QComboBox) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(QLabel(label), 1)
        h_layout.addWidget(combobox, 1)
        parent_layout.addWidget(row)
        return row
    
    @staticmethod
    def button(parent_layout: QBoxLayout, label: str, button: QPushButton) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(QLabel(label), 1)
        h_layout.addWidget(button, 1)
        parent_layout.addWidget(row)
        return row
    
    @staticmethod
    def buttons(parent_layout: QBoxLayout, buttons: List[QPushButton]) -> QWidget:
        '''
        Shoves buttons to the right side - best used at the bottom of a dialog
        '''
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addStretch()
        for button in buttons:
            h_layout.addWidget(button)
        parent_layout.addWidget(row)
        return row
    
    @staticmethod
    def dialog_button_box(parent_layout: QBoxLayout, button_box: QDialogButtonBox) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(button_box)
        parent_layout.addWidget(row)
        return row
    
    @staticmethod
    def file_picker(parent_layout: QBoxLayout, label: str, file_input: QLineEdit, browse_btn: QPushButton, clear_btn: QPushButton | None = None) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(QLabel(label), 1)

        right_side = QWidget()
        right_layout = QHBoxLayout(right_side)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        right_layout.addWidget(file_input)
        right_layout.addWidget(browse_btn)
        if clear_btn is not None:
            right_layout.addWidget(clear_btn)

        h_layout.addWidget(right_side, 1)
        parent_layout.addWidget(row)
        return row
    
    @staticmethod
    def center(widget: QWidget) -> QWidget:
        '''
        Creates a generic wrapper widget, adds center
        alignment, adds input widget to wrapper, then returns wrapper
        '''
        wrapper = QWidget()

        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        layout.addWidget(widget)

        return wrapper