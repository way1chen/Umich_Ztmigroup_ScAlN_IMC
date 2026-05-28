from PySide6 import QtWidgets, QtCore, QtGui
from gui.widgets.image_view import ImageView
from gui.widgets.edit_panel import EditPanel
from gui.widgets.image_processing_sidebar import ImageProcessingSidebar
from gui.widgets.processing_mode import ProcessingMode
from gui.widgets.preview_util import preview_widget


class ImageProcessing(QtWidgets.QWidget):
    """Main image-processing selection widget.

    Signals:
        - `serial_submit_requested(object, ProcessingMode)`: emits
            (QImage|bytes, mode enum)
        intended to be connected to `SerialManager.request_process_image`.
    """

    # Emit a `QtGui.QImage` or raw bytes for serial submission.
    serial_submit_requested = QtCore.Signal(object, object)
    error_occurred = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = ProcessingMode.BLUR_LIGHT

        #Define Widgets
        self.input_image = EditPanel()
        self.output_image = ImageView()
        self.sidebar = ImageProcessingSidebar()

        self.input_title = QtWidgets.QLabel("Input Image")
        self.output_title = QtWidgets.QLabel("Output Image")

        #Define Layout
        input_panel = QtWidgets.QWidget()
        input_layout = QtWidgets.QVBoxLayout(input_panel)
        input_layout.addWidget(self.input_title)
        input_layout.addWidget(self.input_image)

        output_panel = QtWidgets.QWidget()
        output_layout = QtWidgets.QVBoxLayout(output_panel)
        output_layout.addWidget(self.output_title)
        output_layout.addWidget(self.output_image)

        image_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        image_splitter.addWidget(input_panel)
        image_splitter.addWidget(output_panel)
        image_splitter.setChildrenCollapsible(False)
        image_splitter.setStretchFactor(0, 1)
        image_splitter.setStretchFactor(1, 1)

        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.main_splitter.addWidget(image_splitter)
        self.main_splitter.addWidget(self.sidebar)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setStretchFactor(0, 4)
        self.main_splitter.setStretchFactor(1, 1)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.main_splitter)
        self.setLayout(layout)
        
        #Define Signal-Slot Connections
        self.sidebar.image_selected.connect(self.handle_image_selected)
        self.sidebar.paint_enabled_changed.connect(self.input_image.set_edit_enabled)
        self.sidebar.brush_size_changed.connect(self.input_image.set_brush_radius)
        self.sidebar.brush_value_changed.connect(self.input_image.set_brush_value)
        self.input_image.image_changed.connect(self.sidebar.set_selected_image)
        self.sidebar.mode_changed.connect(self.handle_mode_changed)
        self.sidebar.submit_requested.connect(self.handle_submit_requested)
        self.sidebar.error_occurred.connect(self.error_occurred.emit)


    @QtCore.Slot(QtGui.QImage)
    def receive_serial_image(self, image):
        """Slot to receive processed images from the serial manager.

        Connect `SerialManager.image_received` to this slot to display remote
        results in the output pane.
        """
        if image is None:
            return

        self.output_image.set_image(image)


    @QtCore.Slot(QtGui.QImage)
    def handle_image_selected(self, image):
        if image is None or image.isNull():
            return

        self.input_image.set_image(image)
        self.sidebar.set_selected_image(image)


    @QtCore.Slot(object)
    def handle_mode_changed(self, mode):
        self.current_mode = mode


    @QtCore.Slot(object, object)
    def handle_submit_requested(self, image_source, mode):
        """Handle submit events from the sidebar.


        If the selected source is empty and the input image widget contains an image,
        the current `QImage` will be emitted.
        """

        if isinstance(image_source, QtGui.QImage) and not image_source.isNull():
            self.serial_submit_requested.emit(image_source, mode)
            return

        # If no image provided, attempt to submit the in-memory image.
        current = self.input_image.current_image()
        if isinstance(current, QtGui.QImage) and not current.isNull():
            self.serial_submit_requested.emit(current, mode)
            return

        self.error_occurred.emit("Unable to submit image: no valid image data was provided.")

def preview():
    preview_widget(ImageProcessing)


if __name__ == "__main__":
    preview()
