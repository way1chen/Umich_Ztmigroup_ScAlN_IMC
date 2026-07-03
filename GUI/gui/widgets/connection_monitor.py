from PySide6 import QtWidgets, QtCore
from gui.core.preview_util import preview_widget


class ConnectionMonitor(QtWidgets.QWidget):
    """Display the current serial connection state."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.status_label = QtWidgets.QLabel()
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_label.setMinimumHeight(40)
        self.status_label.setObjectName("connectionStatusLabel")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        self.set_connected(False)

    @QtCore.Slot(bool)
    def set_connected(self, connected):
        if connected:
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet(
                "QLabel { color: #1B5E20; background: #DFF5E1; border: 1px solid #81C784; "
                "border-radius: 8px; font-weight: 600; padding: 10px; }"
            )
        else:
            self.status_label.setText("No Connection")
            self.status_label.setStyleSheet(
                "QLabel { color: #B71C1C; background: #FDE0E0; border: 1px solid #E57373; "
                "border-radius: 8px; font-weight: 600; padding: 10px; }"
            )

    @QtCore.Slot()
    def set_disconnected(self):
        self.set_connected(False)


def preview():
    preview_widget(ConnectionMonitor)


if __name__ == "__main__":
    preview()
