from PySide6 import QtCore
import serial


class SerialWorker(QtCore.QThread):
    data_received = QtCore.Signal(str)
    disconnected = QtCore.Signal()

    def __init__(self, port, baudrate=115200):
        super().__init__()

        self.port_name = port
        self.baudrate = baudrate

        self.running = False
        self.serial_port = None

    def run(self):
        self.running = True

        try:
            self.serial_port = serial.Serial(
                self.port_name,
                self.baudrate,
                timeout=1
            )

            while self.running:
                try:
                    line = self.serial_port.readline()

                    if line:
                        decoded = line.decode(errors="ignore").strip()
                        self.data_received.emit(decoded)

                except serial.SerialException:
                    self.disconnected.emit()
                    break

        except serial.SerialException:
            self.disconnected.emit()

        finally:
            self.cleanup()

    def cleanup(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def stop(self):
        self.running = False

    def send(self, text):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write((text + "\n").encode())

class SerialManager(QtCore.QObject):

    disconected = QtCore.Signal()
    data_received = QtCore.Signal(str)
    def __init__(self):
        super().__init__()
        self.worker = None

    def open_port(self, port):
        self.worker = SerialWorker(port)
        self.worker.data_received.connect(self.data_received.emit)
        self.worker.disconnected.connect(self.disconected.emit)
        self.worker.start()

    def send(self, text):
        self.worker.send(text)

    def handle_disconnect(self):
        self.close_port()
        self.disconnected.emit()

    def close_port(self):

        if not self.worker:
            return

        self.worker.stop()

        self.worker.wait()

        self.worker.deleteLater()

        self.worker = None