from PySide6 import QtWidgets, QtCore, QtGui
from gui.widgets.preview_util import preview_widget


class PaintingPalette(QtWidgets.QWidget):
    paint_enabled_changed = QtCore.Signal(bool)
    brush_size_changed = QtCore.Signal(int)
    brush_value_changed = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.paint_toggle = QtWidgets.QCheckBox("Enable paint")
        self.paint_toggle.setChecked(False)

        self.brush_size_label = QtWidgets.QLabel("Brush Size")
        self.brush_size_select = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.brush_size_select.setRange(1, 32)
        self.brush_size_select.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.brush_size_select.setTickInterval(1)
        self.brush_size_select.setSingleStep(1)
        self.brush_size_select.setPageStep(1)
        self.brush_size_select.setValue(8)
        self.brush_size_value_label = QtWidgets.QLabel("8")

        self.brush_value_label = QtWidgets.QLabel("Brush Value")
        self.brush_value_select = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.brush_value_select.setRange(0, 255)
        self.brush_value_select.setValue(0)
        self.brush_value_select.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.brush_value_select.setTickInterval(32)

        self.color_preview = QtWidgets.QFrame()
        self.color_preview.setFixedSize(28, 28)
        self.color_preview.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.color_preview.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self._update_color_preview(0)

        self.enabled_state_label = QtWidgets.QLabel("Paint mode is off")
        self.enabled_state_label.setWordWrap(True)

        controls_group = QtWidgets.QGroupBox("Painting Palette")
        controls_layout = QtWidgets.QGridLayout(controls_group)
        controls_layout.addWidget(self.paint_toggle, 0, 0, 1, 2)
        controls_layout.addWidget(self.brush_size_label, 1, 0)
        controls_layout.addWidget(self.brush_size_select, 1, 1)
        controls_layout.addWidget(self.brush_size_value_label, 1, 3)
        controls_layout.addWidget(self.brush_value_label, 2, 0)
        controls_layout.addWidget(self.brush_value_select, 2, 1)
        controls_layout.addWidget(self.color_preview, 2, 3)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(controls_group)
        layout.addWidget(self.enabled_state_label)
        layout.addStretch(1)
        self.setLayout(layout)

        self.paint_toggle.toggled.connect(self._handle_enabled_toggled)
        self.brush_size_select.valueChanged.connect(self._handle_brush_size_changed)
        self.brush_value_select.valueChanged.connect(self._handle_brush_value_changed)

        self._handle_enabled_toggled(self.paint_toggle.isChecked())
        self._handle_brush_size_changed(self.brush_size_select.value())
        self._handle_brush_value_changed(self.brush_value_select.value())

    def _update_color_preview(self, value):
        value = max(0, min(int(value), 255))
        self.color_preview.setStyleSheet(
            "background-color: rgb({0}, {0}, {0}); border: 1px solid #444;".format(value)
        )

    @QtCore.Slot(bool)
    def _handle_enabled_toggled(self, enabled):
        self.enabled_state_label.setText("Paint mode is on" if enabled else "Paint mode is off")
        self.paint_enabled_changed.emit(bool(enabled))

    @QtCore.Slot(int)
    def _handle_brush_size_changed(self, size):
        size = int(size)
        self.brush_size_value_label.setText(str(size))
        self.brush_size_changed.emit(size)

    @QtCore.Slot(int)
    def _handle_brush_value_changed(self, value):
        self.brush_value_label.setText(f"Brush Value: {value}")
        self._update_color_preview(value)
        self.brush_value_changed.emit(int(value))

    def set_paint_enabled(self, enabled):
        self.paint_toggle.setChecked(bool(enabled))

    def set_brush_size(self, size):
        self.brush_size_select.setValue(max(1, min(int(size), 32)))

    def set_brush_value(self, value):
        self.brush_value_select.setValue(int(value))


def preview():
    preview_widget(PaintingPalette)


if __name__ == "__main__":
    preview()
