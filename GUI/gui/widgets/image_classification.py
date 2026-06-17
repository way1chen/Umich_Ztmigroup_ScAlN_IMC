from PySide6 import QtWidgets, QtCore, QtGui
from gui.widgets.preview_util import preview_widget
from gui.widgets.edit_panel import EditPanel
from gui.widgets.classification_results_panel import ClassificationResultsPanel
from gui.widgets.image_classification_sidebar import ImageClassificationSidebar


class ImageClassification(QtWidgets.QWidget):

    error_occured = QtCore.Signal(str)
    request_classification = QtCore.Signal(QtGui.QImage)

    def __init__(self, parent=None):
        super().__init__(parent)

        #Define Child Widgets
        self.input_image = EditPanel()
        self.results_panel = ClassificationResultsPanel()
        self.sidebar = ImageClassificationSidebar()
        
        #Define Layout

        input_panel = QtWidgets.QWidget()
        input_layout = QtWidgets.QVBoxLayout(input_panel)
        input_layout.addWidget(QtWidgets.QLabel("Input Image"))
        input_layout.addWidget(self.input_image)

        results_panel = QtWidgets.QWidget()
        results_layout = QtWidgets.QVBoxLayout(results_panel)
        results_layout.addWidget(QtWidgets.QLabel("Results"))
        results_layout.addWidget(self.results_panel)

        image_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        image_splitter.addWidget(input_panel)
        image_splitter.addWidget(results_panel)
        image_splitter.setChildrenCollapsible(False)
        image_splitter.setStretchFactor(0, 1)
        image_splitter.setStretchFactor(1, 1)

        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.main_splitter.addWidget(image_splitter)
        self.main_splitter.addWidget(self.sidebar)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setStretchFactor(0, 4)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setSizes([900, 360])

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.main_splitter)
        self.setLayout(layout)

        #Define Signal-Slot Connections
        self.sidebar.image_selected.connect(self.handle_image_selected)
        self.sidebar.paint_enabled_changed.connect(self.input_image.set_edit_enabled)
        self.sidebar.brush_size_changed.connect(self.input_image.set_brush_radius)
        self.sidebar.brush_value_changed.connect(self.input_image.set_brush_value)
        self.input_image.image_changed.connect(self.sidebar.set_selected_image)
        self.sidebar.mnist_picker.digit_picked.connect(self.results_panel.set_actual_digit)
        self.sidebar.submit_requested.connect(self.handel_submit_requested)

        self.input_image.error_occurred.connect(self.error_occured.emit)

        

    @QtCore.Slot(QtGui.QImage)
    def handle_image_selected(self, image):
        if image is None or image.isNull():
            return

        self.input_image.set_image(image)
        self.sidebar.set_selected_image(image)
    
    
    @QtCore.Slot()
    def receive_results(self, results):
        if results is None:
            self.error_occured.emit("Results were Null")
        self.results_panel.set_confidences(results)

    @QtCore.Slot()
    def handel_submit_requested(self):
        current = self.input_image.current_image()
        if isinstance(current, QtGui.QImage) and not current.isNull():
            self.request_classification.emit(current)
            return
        
        self.error_occurred.emit("Unable to submit image: no valid image data was provided.")




def preview():
    preview_widget(ImageClassification)


if __name__ == "__main__":
    preview()
