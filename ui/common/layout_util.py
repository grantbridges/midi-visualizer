from typing import List

from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QBoxLayout,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from ui.common import SectionDivider

class LayoutUtil:
    def __new__(cls):
        raise TypeError("LayoutUtil is static")
    
    @staticmethod
    def section(parent_layout: QBoxLayout, label: str):
        parent_layout.addWidget(SectionDivider(label))

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
        h_layout.addWidget(QLabel(label))
        h_layout.addStretch()
        h_layout.addWidget(edit)
        parent_layout.addWidget(row)
        return row
    
    @staticmethod
    def line_edit_suffix(parent_layout: QBoxLayout, label: str, edit: QLineEdit, suffix: QLabel) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(QLabel(label))
        h_layout.addStretch()
        h_layout.addWidget(edit)
        h_layout.addWidget(suffix)
        parent_layout.addWidget(row)
        return row

    @staticmethod
    def spinbox(parent_layout: QBoxLayout, label: str, spinbox: QAbstractSpinBox) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(QLabel(label))
        h_layout.addWidget(spinbox)
        parent_layout.addWidget(row)
        return row
    
    @staticmethod
    def combobox(parent_layout: QBoxLayout, label: str, combobox: QComboBox) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(QLabel(label))
        h_layout.addWidget(combobox)
        parent_layout.addWidget(row)
        return row
    
    @staticmethod
    def button(parent_layout: QBoxLayout, label: str, button: QPushButton) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(QLabel(label))
        h_layout.addWidget(button)
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
    def file_picker(parent_layout: QBoxLayout, label: str, file_input: QLineEdit, browse_btn: QPushButton, clear_btn: QPushButton | None = None) -> QWidget:
        row = QWidget()
        h_layout = QHBoxLayout(row)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(QLabel(label))
        h_layout.addStretch()
        h_layout.addWidget(file_input)
        h_layout.addWidget(browse_btn)
        if clear_btn is not None:
            h_layout.addWidget(clear_btn)
        parent_layout.addWidget(row)
        return row