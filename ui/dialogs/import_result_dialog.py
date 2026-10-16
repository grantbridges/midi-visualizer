from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog, 
    QDialogButtonBox, 
    QHBoxLayout, 
    QHeaderView, 
    QTableWidget, 
    QTableWidgetItem,
    QVBoxLayout
)
from ui.common import WidgetUtil
from models import CreateFromMidiResult

import logging
logger = logging.getLogger("ImportResultDialog")

class ImportResultDialog(QDialog):
    def __init__(self, data: CreateFromMidiResult, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"Import Result")

        self.data = data

        self.setModal(True)
        min_width, min_height = 500, 400
        self.setFixedSize(min_width, min_height)

        # -- Create Controls --

        info_label = WidgetUtil.info_text(f"The following track(s) could not be imported from the provided MIDI file. Ensure all tracks are uniquely named and have note data present.")

        # table
        self.columns = ["Reason", "Name", "Notes Count"]
        self.table = QTableWidget(0, len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.horizontalHeader().resizeSection(0, 150)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().resizeSection(2, 80)
        # set whole-row multi-select
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        button_box = QDialogButtonBox()
        ok_btn = button_box.addButton("Ok", QDialogButtonBox.AcceptRole)
        ok_btn.setDefault(True)
        ok_btn.setAutoDefault(True)

        button_box.accepted.connect(self.accept)

        # -- Layout Controls --

        main_layout = QVBoxLayout(self)

        main_layout.addWidget(info_label)
        main_layout.addSpacing(5)
        main_layout.addWidget(self.table)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(button_box)

        main_layout.addLayout(bottom_layout)

        self._refresh_ui()

    def _refresh_ui(self):
         # prevent callbacks while populating table
        self.table.blockSignals(True)
        rows = sorted(self.data.skipped_tracks, key=lambda x: x.name)
        self.table.setRowCount(len(rows))
        for row in range(len(rows)):
            st = rows[row]

            col = 0

            # reason
            reason_item = QTableWidgetItem(st.reason)
            reason_item.setFlags(reason_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, col, reason_item)
            col += 1

            # name
            name_item = QTableWidgetItem(st.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, col, name_item)
            col += 1

            # notes count
            count_item = QTableWidgetItem(f"{st.notes_count}")
            count_item.setFlags(count_item.flags() & ~Qt.ItemIsEditable)
            count_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, count_item)
            col += 1

        # resume callbacks
        self.table.blockSignals(False)