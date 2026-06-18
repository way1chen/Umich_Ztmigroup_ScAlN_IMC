from PySide6 import QtWidgets, QtCore, QtGui
from gui.widgets.processing_mode import ProcessingMode
from gui.widgets.mnist_random_picker import MnistRandomPicker
from gui.widgets.painting_palette import PaintingPalette
from gui.widgets.preview_util import preview_widget


class ImageProcessingSidebar(QtWidgets.QWidget):
    image_selected = QtCore.Signal(QtGui.QImage)
    paint_enabled_changed = QtCore.Signal(bool)
    brush_size_changed = QtCore.Signal(int)
    brush_value_changed = QtCore.Signal(int)
    mode_changed = QtCore.Signal(object)
    submit_requested = QtCore.Signal(object)
    error_occurred = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)


        self.selected_mode = ProcessingMode.BLUR_LIGHT

        self.file_label = QtWidgets.QLabel("No image selected")
        self.file_label.setWordWrap(True)

        self.load_button = QtWidgets.QPushButton("Load Image File")
        self.mnist_picker = MnistRandomPicker()
        self.painting_palette = PaintingPalette()
        self.mode_select = QtWidgets.QComboBox()
        for mode in ProcessingMode:
            self.mode_select.addItem(mode.display_text, userData=mode)
        self.mode_select.setCurrentIndex(0)

        self.submit_button = QtWidgets.QPushButton("Submit")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Selected Image"))
        layout.addWidget(self.file_label)
        layout.addWidget(self.load_button)
        layout.addSpacing(8)
        layout.addWidget(self.mnist_picker)
        layout.addSpacing(8)
        layout.addWidget(self.painting_palette)
        layout.addSpacing(8)
        layout.addWidget(QtWidgets.QLabel("Processing Mode"))
        layout.addWidget(self.mode_select)
        layout.addStretch(1)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

        self.load_button.pressed.connect(self.pick_image_file)
        self.mnist_picker.image_picked.connect(self.handle_mnist_image_picked)
        self.painting_palette.paint_enabled_changed.connect(self.paint_enabled_changed.emit)
        self.painting_palette.brush_size_changed.connect(self.brush_size_changed.emit)
        self.painting_palette.brush_value_changed.connect(self.brush_value_changed.emit)
        self.mode_select.currentTextChanged.connect(self.handle_mode_changed)
        self.submit_button.pressed.connect(self.request_submit)
        self.mnist_picker.error_occurred.connect(self.error_occurred.emit)
        self.painting_palette.error_occurred.connect(self.error_occurred.emit)

   



    @QtCore.Slot()
    def pick_image_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select an image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)",
        )

        if not file_path:
            return

        image = QtGui.QImage(file_path)
        if image.isNull():
            self.error_occurred.emit(f"Unable to load image file: {file_path}")
            return

        if image.width() != 20 or image.height() != 20:
            self.error_occurred.emit(
                f"Image must be 20x20 pixels, but got {image.width()}x{image.height()}: {file_path}"
            )
            return

        image = image.convertToFormat(QtGui.QImage.Format.Format_Grayscale8)
        self.image_selected.emit(image)


    @QtCore.Slot(QtGui.QImage)
    def handle_mnist_image_picked(self, image):
        if image is None or image.isNull():
            return

        self.image_selected.emit(image)


    def set_paint_enabled(self, enabled):
        self.painting_palette.set_paint_enabled(enabled)

    def set_brush_size(self, size):
        self.painting_palette.set_brush_size(size)

    def set_brush_value(self, value):
        self.painting_palette.set_brush_value(value)


    @QtCore.Slot(str)
    def handle_mode_changed(self, mode_text):
        self.selected_mode = ProcessingMode.from_display_text(mode_text)
        self.mode_changed.emit(self.selected_mode)


    @QtCore.Slot()
    def request_submit(self):
        self.submit_requested.emit(self.selected_mode)


def preview():
    preview_widget(ImageProcessingSidebar)


if __name__ == "__main__":
    preview()