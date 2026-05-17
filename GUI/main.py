from widgets.main_window import MainWindow
from PySide6 import QtWidgets
import sys


if __name__ == "__main__":
    app = QtWidgets.QApplication.instance()

    owns_app = app is None

    if owns_app:
        app = QtWidgets.QApplication(sys.argv)

    widget = MainWindow()

    widget.show()

    if owns_app:
        sys.exit(app.exec())