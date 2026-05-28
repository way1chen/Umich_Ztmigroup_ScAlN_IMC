from PySide6 import QtWidgets, QtCore

from gui.widgets.application_top_bar import ApplicationTopBar
from gui.widgets.connect_page import ConnectPage
from gui.widgets.image_processing import ImageProcessing
from gui.widgets.serial_manager import SerialManager
from gui.widgets.preview_util import preview_widget


class MainApplication(QtWidgets.QWidget):
    """Main application shell with a top navigation bar and page stack."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.serial_manager = SerialManager()
        self.connect_page = ConnectPage()
        self.image_processing = ImageProcessing()

        self.top_bar = ApplicationTopBar(
            pages=[
                ("connect", "Connect"),
                ("image_processing", "Image Processing"),
            ],
        )

        self.page_stack = QtWidgets.QStackedWidget()
        self.page_stack.addWidget(self.connect_page)
        self.page_stack.addWidget(self.image_processing)

        self._page_indices = {
            "connect": 0,
            "image_processing": 1,
        }

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.top_bar)
        layout.addWidget(self.page_stack, 1)
        self.setLayout(layout)

        # Navigation wiring.
        self.top_bar.page_selected.connect(self._handle_page_selected)
        self.top_bar.set_current_page("connect")

        # Shared connection status and connect-page wiring.
        self.connect_page.request_open_port.connect(self.serial_manager.open_port)
        self.connect_page.error_occurred.connect(self._handle_error)
        self.serial_manager.port_opened.connect(self._handle_port_opened)
        self.serial_manager.port_closed.connect(self._handle_port_closed)
        self.serial_manager.disconnected.connect(self._handle_port_closed)
        self.serial_manager.error_occurred.connect(self._handle_error)

        # Shared processing flow.
        self.image_processing.serial_submit_requested.connect(self.serial_manager.process_image_file)
        self.image_processing.error_occurred.connect(self._handle_error)
        self.serial_manager.image_received.connect(self.image_processing.receive_serial_image)

        self._handle_port_closed()

    @QtCore.Slot(str)
    def _handle_page_selected(self, page_id):
        page_index = self._page_indices.get(page_id)
        if page_index is None:
            return

        self.page_stack.setCurrentIndex(page_index)

    @QtCore.Slot(str)
    def _handle_port_opened(self, _port_name):
        self.top_bar.set_connection_state(True)

    @QtCore.Slot()
    def _handle_port_closed(self):
        self.top_bar.set_connection_state(False)
    
    @QtCore.Slot(str)
    def _handle_error(self, message):
        QtWidgets.QMessageBox.critical(self, "Application Error", message)


def preview():
    preview_widget(MainApplication)


if __name__ == "__main__":
    preview()