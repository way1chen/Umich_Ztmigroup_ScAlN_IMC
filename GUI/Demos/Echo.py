#Demonstrates the ability to connect, send, and recieve serial data from microcontroller

from PySide6 import QtWidgets, QtCore
import sys
from pathlib import Path

from gui.widgets.port_chooser import PortChooser
from gui.widgets.serial_monitor import SerialMonitor
from gui.widgets.serial_manager import SerialManager


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.serial_manager = SerialManager()


        self.port_chooser = PortChooser()
        self.serial_monitor = SerialMonitor()
        self.port_chooser.port_chosen.connect(self.chosen)

        #Define Layout:
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.port_chooser)
        layout.addWidget(self.serial_monitor)

        self.port_chooser.setMaximumHeight(400)
        
        self.serial_monitor.setMaximumHeight(600)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        

        layout.setStretch(1, 2)
        layout.setStretch(2, 5)

        

        self.setLayout(layout)

        #Define Signal-Slot Connections:
        self.port_chooser.port_chosen.connect(self.serial_manager.open_port)
        self.serial_manager.data_received.connect(self.serial_monitor.receive_output)
        self.serial_monitor.input_submitted.connect(self.serial_manager.send)
        

    
    @QtCore.Slot()
    def chosen(self, port):
        print(port)



def preview():
    app = QtWidgets.QApplication.instance()

    owns_app = app is None

    if owns_app:
        app = QtWidgets.QApplication(sys.argv)

    widget = MainWindow()
    widget.resize(400, 400)
    widget.show()

    if owns_app:
        sys.exit(app.exec())


if __name__ == "__main__":
    preview()
