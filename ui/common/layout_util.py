from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QBoxLayout,
    QCheckBox,
    QHBoxLayout,
    QLabel,
)

from ui.common import SectionDivider

class LayoutUtil:
    def __new__(cls):
        raise TypeError("LayoutUtil is static")
    
    @staticmethod
    def layout_section(parent_layout: QBoxLayout, label: str):
        parent_layout.addWidget(SectionDivider(label))

    @staticmethod
    def layout_checkbox(parent_layout: QBoxLayout, label: str, checkbox: QCheckBox):
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel(label))
        h_layout.addStretch()
        h_layout.addWidget(checkbox)
        parent_layout.addLayout(h_layout)

    @staticmethod
    def layout_spinbox(parent_layout: QBoxLayout, label: str, spinbox: QAbstractSpinBox):
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel(label))
        h_layout.addWidget(spinbox)
        parent_layout.addLayout(h_layout)