from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QDialog, QDialogButtonBox, QHBoxLayout, QHeaderView, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout
)
from common import Const
from ui.common import WidgetUtil, Icons, LayoutUtil
from models import presets_config

class ManageTrackPresetsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"Manage Track Presets")

        self.setModal(True)
        self.setFixedSize(800, 600)

        # -- Create Controls --

        info_label = WidgetUtil.info_text(f"Select tracks to save to track presets. Only current tracks with overridden values are shown.")

        # current tracks table
        current_tracks_label = QLabel("Current Tracks")
        self.current_tracks_columns = ["Name", "Pitch Min", "Pitch Max"]
        self.current_tracks_table = QTableWidget(0, len(self.current_tracks_columns))
        self.current_tracks_table.setHorizontalHeaderLabels(self.current_tracks_columns)
        self.current_tracks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.current_tracks_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.current_tracks_table.itemSelectionChanged.connect(self._on_selection_changed)
        # set whole-row multi-select
        self.current_tracks_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.current_tracks_table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # copy buttons
        self.copy_right_btn = WidgetUtil.icon_btn(Icons.chevron_right(), "Copy selected track(s) to presets")
        self.copy_right_btn.clicked.connect(self._copy_right)
        self.copy_all_btn = QPushButton() 
        self.copy_all_btn = WidgetUtil.icon_btn(Icons.chevron_double_right(), "Copy all tracks to presets")
        self.copy_all_btn.clicked.connect(self._copy_all_right)

        # track presets table
        track_presets_label = QLabel("Existing Track Presets")
        self.track_presets_columns = ["Name", "Pitch Min", "Pitch Max", ""]
        self.track_presets_table = QTableWidget(0, len(self.track_presets_columns))
        self.track_presets_table.setHorizontalHeaderLabels(self.track_presets_columns)
        self.track_presets_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.track_presets_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.track_presets_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        button_box = QDialogButtonBox()
        button_box.addButton("Cancel", QDialogButtonBox.RejectRole)
        apply_button = button_box.addButton("Save", QDialogButtonBox.AcceptRole)
        apply_button.setDefault(True)
        apply_button.setAutoDefault(True)

        button_box.accepted.connect(self._save)
        button_box.rejected.connect(self.reject)

        # -- Layout Controls --

        main_layout = QVBoxLayout(self)

        main_layout.addWidget(info_label)
        main_layout.addSpacing(5)

        # current tracks table
        current_tracks_layout = QVBoxLayout()
        current_tracks_layout.addWidget(current_tracks_label)
        current_tracks_layout.addWidget(self.current_tracks_table)

        # copy buttons
        copy_buttons_layout = QVBoxLayout()
        copy_buttons_layout.addStretch()
        copy_buttons_layout.addWidget(self.copy_right_btn)
        copy_buttons_layout.addWidget(self.copy_all_btn)
        copy_buttons_layout.addStretch()

        # track presets table
        track_presets_layout = QVBoxLayout()
        track_presets_layout.addWidget(track_presets_label)
        track_presets_layout.addWidget(self.track_presets_table)

        panels_layout = QHBoxLayout()
        panels_layout.addLayout(current_tracks_layout)
        panels_layout.addLayout(copy_buttons_layout)
        panels_layout.addLayout(track_presets_layout)

        main_layout.addLayout(panels_layout)
        main_layout.addWidget(button_box)

        self._refresh_ui()

    def _refresh_ui(self):
        # TODO populate tables - dummy data for now

        # prevent callbacks while populating table rows
        self.current_tracks_table.blockSignals(True)
        self.track_presets_table.blockSignals(True)

        # current tracks table
        self.current_tracks_table.setRowCount(12)
        for row in range(12):
            col = 0

            # name
            name_item = QTableWidgetItem("Track Name")
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.current_tracks_table.setItem(row, col, name_item)
            col += 1

            # pitch min
            pitch_min_item = QTableWidgetItem(f"{35}")
            pitch_min_item.setFlags(pitch_min_item.flags() & ~Qt.ItemIsEditable)
            pitch_min_item.setTextAlignment(Qt.AlignCenter)
            self.current_tracks_table.setItem(row, col, pitch_min_item)
            col += 1

            # pitch max
            pitch_max_item = QTableWidgetItem(f"{127}")
            pitch_max_item.setFlags(pitch_max_item.flags() & ~Qt.ItemIsEditable)
            pitch_max_item.setTextAlignment(Qt.AlignCenter)
            self.current_tracks_table.setItem(row, col, pitch_max_item)
            col += 1        

        # track presets table
        self.track_presets_table.setRowCount(24)
        for row in range(24):
            col = 0

            # name
            name_item = QTableWidgetItem("Track Name")
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.track_presets_table.setItem(row, col, name_item)
            col += 1

            # pitch min
            pitch_min_item = QTableWidgetItem(f"{35}")
            pitch_min_item.setFlags(pitch_min_item.flags() & ~Qt.ItemIsEditable)
            pitch_min_item.setTextAlignment(Qt.AlignCenter)
            self.track_presets_table.setItem(row, col, pitch_min_item)
            col += 1

            # pitch max
            pitch_max_item = QTableWidgetItem(f"{127}")
            pitch_max_item.setFlags(pitch_max_item.flags() & ~Qt.ItemIsEditable)
            pitch_max_item.setTextAlignment(Qt.AlignCenter)
            self.track_presets_table.setItem(row, col, pitch_max_item)
            col += 1

            # delete button
            delete_btn = QPushButton()
            delete_btn.setIcon(Icons.trash_can())
            delete_btn.clicked.connect(lambda _, row=row: self._on_remove_preset(row))
            self.track_presets_table.setCellWidget(row, col, LayoutUtil.center(delete_btn))
            col += 1

        # resume callbacks
        self.current_tracks_table.blockSignals(False)
        self.track_presets_table.blockSignals(False)

    def _on_selection_changed(self):
        pass

    def _copy_right(self):
        pass

    def _copy_all_right(self):
        pass

    def _on_remove_preset(self, row: int):
        pass

    def _save(self):
        # TODO save changes
        self.accept()
