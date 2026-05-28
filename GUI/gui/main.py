from gui.widgets.main_application import MainApplication
from PySide6 import QtWidgets
import sys


if __name__ == "__main__":
    app = QtWidgets.QApplication.instance()

    owns_app = app is None

    if owns_app:
        app = QtWidgets.QApplication(sys.argv)

    widget = MainApplication()



    
    # Get the available screen geometry
    screen = app.primaryScreen()
    geometry = screen.availableGeometry()
    
    # Set widget to screen size and show
    widget.setGeometry(geometry)
    widget.show()

    if owns_app:
        sys.exit(app.exec())