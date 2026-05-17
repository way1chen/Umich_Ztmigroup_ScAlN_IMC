from PySide6 import QtWidgets, QtCore
import serial.tools.list_ports
import sys


class PortChooser(QtWidgets.QWidget):

    port_chosen = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        #Compile list of available ports:
        self.list = QtWidgets.QListWidget()
        self.devices = []
        self.refresh_port_list()
        
        self.connect_button = QtWidgets.QPushButton("Connect")
        self.refresh_button = QtWidgets.QPushButton("Refresh")


        #Define Layout:
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.list)
        buttons = QtWidgets.QHBoxLayout()
        buttons.addWidget(self.connect_button)
        buttons.addWidget(self.refresh_button)
        buttons.setStretch(0,4)
        buttons.setStretch(4,5)
        layout.addLayout(buttons)
        self.setLayout(layout)

        

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred
        )

        #Define signal-slot connections:
        self.connect_button.pressed.connect(self.connect_pushed)
        self.refresh_button.pressed.connect(self.refresh_port_list)

    
    def refresh_port_list(self):
        self.devices = []
        self.list.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            description = port.description
            if(description == "n/a"): continue
            self.devices.append(port.device)
            portname = port.name
            QtWidgets.QListWidgetItem(portname + " - " + description, self.list)
        
    @QtCore.Slot()
    def connect_pushed(self):
        selected_index = self.list.currentRow()
        self.port_chosen.emit(self.devices[selected_index])

    def sizeHint(self):
        return QtCore.QSize(400, 250)



def preview():
    app = QtWidgets.QApplication.instance()

    owns_app = app is None

    if owns_app:
        app = QtWidgets.QApplication(sys.argv)

    widget = PortChooser()
    widget.resize(400, 400)
    widget.show()

    if owns_app:
        sys.exit(app.exec())


if __name__ == "__main__":
    preview()
