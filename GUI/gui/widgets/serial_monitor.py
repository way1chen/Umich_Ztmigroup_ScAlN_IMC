from PySide6 import QtWidgets, QtGui, QtCore
from gui.core.preview_util import preview_widget


class SerialMonitor(QtWidgets.QWidget):

    input_submitted = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Define Atomic Widgets:
        self.text_viewport = QtWidgets.QTextEdit()
        self.input = QtWidgets.QLineEdit()

        self.text_viewport.setReadOnly(True)

        self.input.setPlaceholderText("Serial Input...")

        # Define layout:
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.text_viewport)
        layout.addWidget(self.input)
        self.setLayout(layout)

        # Define Signal-Slot connections:
        self.input.returnPressed.connect(self.send_input)

    @QtCore.Slot()
    def send_input(self):
        text = self.input.text()

        if not text:
            return

        self.input.clear()

        self.display_outgoing_text(text)
        self.input_submitted.emit(text)

    @QtCore.Slot(str)
    def receive_output(self, text):
        self.display_incoming_text(text)

    def append_colored_text(self, text, color):
        cursor = self.text_viewport.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)

        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor(color))

        cursor.insertText(text + "\n", fmt)

        self.text_viewport.setTextCursor(cursor)
        self.text_viewport.ensureCursorVisible()

    def display_outgoing_text(self, text):
        self.append_colored_text(f">> {text}", "#4FC3F7")

    def display_incoming_text(self, text):
        self.append_colored_text(f"<< {text}", "#81C784")



    


def preview():
    preview_widget(SerialMonitor)


if __name__ == "__main__":
    preview()
