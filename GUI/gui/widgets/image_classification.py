from PySide6 import QtWidgets, QtCore
from gui.widgets.preview_util import preview_widget


class ImageClassification(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        #Define Child Widgets

        #Define Layout

        #Define Signal-Slot Connections


def preview():
    preview_widget(ImageClassification)


if __name__ == "__main__":
    preview()
