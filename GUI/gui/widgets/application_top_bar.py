from __future__ import annotations

from PySide6 import QtWidgets, QtCore
from gui.widgets.connection_monitor import ConnectionMonitor
from gui.core.preview_util import preview_widget


class ApplicationTopBar(QtWidgets.QWidget):
    """Information and navigation bar shown at the top of the app.

    Pages are registered dynamically through `add_page()`, which keeps the
    widget scalable as the application grows.
    """

    page_selected = QtCore.Signal(str)

    def __init__(self, parent=None, pages: list[tuple[str, str]] | None = None):
        super().__init__(parent)



        self.tab_bar = QtWidgets.QTabBar()
        self.tab_bar.setObjectName("applicationTopBarTabs")
        self.tab_bar.setExpanding(False)
        self.tab_bar.setMovable(False)
        self.tab_bar.setDrawBase(False)
        self.tab_bar.setElideMode(QtCore.Qt.TextElideMode.ElideRight)

        self.connection_monitor = ConnectionMonitor()
        self.connection_monitor.setObjectName("applicationTopBarConnectionMonitor")
        self.connection_monitor.setMinimumWidth(180)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        layout.addWidget(self.tab_bar, 1)
        layout.addWidget(self.connection_monitor, 0)
        self.setLayout(layout)

        self.tab_bar.currentChanged.connect(self._handle_tab_changed)

        if pages:
            for page_id, label in pages:
                self.add_page(page_id, label)

    def add_page(self, page_id: str, label: str, select: bool = False) -> int:
        """Register a tab for a page widget and return its tab index."""
        existing_index = self._find_page_index(page_id)
        if existing_index >= 0:
            if select:
                self.tab_bar.setCurrentIndex(existing_index)
            return existing_index

        index = self.tab_bar.addTab(label)
        self.tab_bar.setTabData(index, page_id)

        if select or self.tab_bar.count() == 1:
            self.tab_bar.setCurrentIndex(index)

        return index

    def remove_page(self, page_id: str) -> bool:
        """Remove a registered page tab."""
        index = self._find_page_index(page_id)
        if index < 0:
            return False

        self.tab_bar.removeTab(index)
        return True

    def set_current_page(self, page_id: str) -> bool:
        """Switch to a page by its registered identifier."""
        index = self._find_page_index(page_id)
        if index < 0:
            return False

        self.tab_bar.setCurrentIndex(index)
        return True

    def current_page(self) -> str | None:
        index = self.tab_bar.currentIndex()
        if index < 0:
            return None

        page_id = self.tab_bar.tabData(index)
        return page_id if isinstance(page_id, str) else None

    def set_connection_state(self, connected: bool):
        self.connection_monitor.set_connected(connected)

    def _find_page_index(self, page_id: str) -> int:
        for index in range(self.tab_bar.count()):
            if self.tab_bar.tabData(index) == page_id:
                return index
        return -1

    @QtCore.Slot(int)
    def _handle_tab_changed(self, index: int):
        page_id = self.tab_bar.tabData(index)
        if isinstance(page_id, str):
            self.page_selected.emit(page_id)


def preview():
    preview_widget(
        ApplicationTopBar,
        pages=[
            ("connect", "Connect"),
            ("image_processing", "Image Processing"),
        ],
    )


if __name__ == "__main__":
    preview()
