from PySide6.QtCore import QItemSelection, QItemSelectionModel, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QTableWidget
)

class TableComboBox(QComboBox):
    '''
    QComboBox override for use in tables. Prevents clearing out table row selection
    when clicking on dropdown (only an issue on Windows).
    '''
    def __init__(self, table: QTableWidget, parent=None):
        super().__init__(parent)
        self._table = table
        self._selected_rows: list[int] | None = None

    def mousePressEvent(self, event) -> None:
        # grab selected table rows and store before letting event propagate
        selected_rows = {index.row() for index in self._table.selectionModel().selectedRows()}
        if len(selected_rows) > 1:
            self._selected_rows = sorted(selected_rows)

        super().mousePressEvent(event)

    def focusInEvent(self, event) -> None:
        super().focusInEvent(event)

        # queue up event to reapply row selection to table
        if self._selected_rows:
            QTimer.singleShot(0, self._restore_selected_rows)

    def _restore_selected_rows(self) -> None:
        if self._selected_rows is None:
            return

        selection = QItemSelection()
        last_column = self._table.columnCount() - 1
        for row in self._selected_rows:
            # add each previously selected rows to selection context
            top_left = self._table.model().index(row, 0)
            bottom_right = self._table.model().index(row, last_column)
            selection.select(top_left, bottom_right)

        # apply selection to table
        self._table.selectionModel().select(
            selection,
            QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows,
        )
        self._selected_rows = None
