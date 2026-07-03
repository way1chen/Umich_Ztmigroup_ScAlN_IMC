from PySide6 import QtWidgets, QtCore, QtGui
from gui.widgets.mnist_random_picker import MnistRandomPicker
from gui.widgets.painting_palette import PaintingPalette
from gui.core.preview_util import preview_widget


class ImageClassificationSidebar(QtWidgets.QWidget):
    image_selected = QtCore.Signal(QtGui.QImage)
    paint_enabled_changed = QtCore.Signal(bool)
    brush_size_changed = QtCore.Signal(int)
    brush_value_changed = QtCore.Signal(int)
    submit_requested = QtCore.Signal()
    error_occurred = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        #Define Child Widgets
        self.selected_input = None

        self.title_label = QtWidgets.QLabel("MNIST Classification Controls")
        self.title_label.setObjectName("panelTitle")

        self.selected_label = QtWidgets.QLabel("No image selected")
        self.selected_label.setWordWrap(True)

        self.mnist_picker = MnistRandomPicker()
        self.painting_palette = PaintingPalette()

        self.summary_card = QtWidgets.QFrame()
        self.summary_card.setObjectName("sidebarCard")
        summary_layout = QtWidgets.QVBoxLayout(self.summary_card)
        summary_layout.setContentsMargins(12, 12, 12, 12)
        summary_layout.addWidget(QtWidgets.QLabel("Selected Image"))
        summary_layout.addWidget(self.selected_label)

        controls_card = QtWidgets.QFrame()
        controls_card.setObjectName("sidebarCard")
        controls_layout = QtWidgets.QVBoxLayout(controls_card)
        controls_layout.setContentsMargins(12, 12, 12, 12)
        controls_layout.addWidget(self.mnist_picker)
        controls_layout.addSpacing(8)
        controls_layout.addWidget(self.painting_palette)

        self.submit_button = QtWidgets.QPushButton("Submit")
        controls_layout.addSpacing(12)
        controls_layout.addWidget(self.submit_button)

        #Define Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(self.title_label)
        layout.addWidget(self.summary_card)
        layout.addWidget(controls_card)
        layout.addStretch(1)

        #Define Signal-Slot Connections
        self.mnist_picker.image_picked.connect(self.handle_mnist_image_picked)
        self.mnist_picker.error_occurred.connect(self.error_occurred.emit)
        self.painting_palette.paint_enabled_changed.connect(self.paint_enabled_changed.emit)
        self.painting_palette.brush_size_changed.connect(self.brush_size_changed.emit)
        self.painting_palette.brush_value_changed.connect(self.brush_value_changed.emit)
        self.submit_button.pressed.connect(self.submit_requested.emit)

    def set_selected_image(self, image, label_text=None):
        self.selected_input = image
        if label_text is not None:
            self.selected_label.setText(label_text)

    @QtCore.Slot(QtGui.QImage)
    def handle_mnist_image_picked(self, image):
        if image is None or image.isNull():
            return

        self.set_selected_image(image, "MNIST test sample selected")
        self.image_selected.emit(image)

    def set_paint_enabled(self, enabled):
        self.painting_palette.set_paint_enabled(enabled)

    def set_brush_size(self, size):
        self.painting_palette.set_brush_size(size)

    def set_brush_value(self, value):
        self.painting_palette.set_brush_value(value)


def preview():
    preview_widget(ImageClassificationSidebar)


if __name__ == "__main__":
    preview()
