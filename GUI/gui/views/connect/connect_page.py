from PySide6 import QtWidgets, QtCore
from gui.widgets.connection_monitor import ConnectionMonitor
from gui.views.connect.port_chooser import PortChooser
from gui.core.preview_util import preview_widget


class ConnectPage(QtWidgets.QWidget):
    """Initial application screen for selecting and opening a serial port."""

    request_open_port = QtCore.Signal(str)
    error_occurred = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.title_label = QtWidgets.QLabel("Connect to Device")
        self.title_label.setObjectName("connectPageTitle")

        self.instructions_label = QtWidgets.QLabel(
            "Choose a serial port below, then press Connect to open the device."
        )
        self.instructions_label.setWordWrap(True)

        self.port_chooser = PortChooser()

        card = QtWidgets.QFrame()
        card.setObjectName("connectPageCard")
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.addWidget(self.title_label)
        card_layout.addWidget(self.instructions_label)
        card_layout.addSpacing(8)
        card_layout.addSpacing(8)
        card_layout.addWidget(self.port_chooser)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(card)
        layout.addStretch(1)
        self.setLayout(layout)

        self.port_chooser.port_chosen.connect(self.request_open_port.emit)

        self.port_chooser.error_occurred.connect(self.error_occurred.emit)



def preview():
    preview_widget(ConnectPage)


if __name__ == "__main__":
    preview()
