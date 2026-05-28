from PySide6 import QtWidgets, QtCore, QtGui
import sys


class InputImage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None



@QtCore.Slot()
def open_image_file(self, file_path):
    img = QtGui.QImage(file_path, QtGui.QImage.Format.Format_Grayscale8)
    self.image = img


def preview():
    app = QtWidgets.QApplication.instance()

    owns_app = app is None

    if owns_app:
        app = QtWidgets.QApplication(sys.argv)

    widget = InputImage()
    widget.resize(400, 400)
    widget.show()

    if owns_app:
        sys.exit(app.exec())


if __name__ == "__main__":
    preview()
