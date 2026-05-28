from PySide6 import QtWidgets, QtCore, QtGui

from gui.widgets.preview_util import preview_widget


class _ImageCanvas(QtWidgets.QWidget):
    image_changed = QtCore.Signal(QtGui.QImage)
    error_occurred = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.edit_enabled = False
        self.brush_value = 0
        self.brush_radius = 8
        self._dragging = False

        self.setMinimumSize(150, 150)
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.CursorShape.CrossCursor)

    def set_image(self, image):
        if image is None or image.isNull():
            self.image = None
            self.update()
            return

        self.image = image.convertToFormat(QtGui.QImage.Format.Format_Grayscale8)
        self.update()
        self.image_changed.emit(self.image)

    def open_image_file(self, file_path):
        if not file_path:
            return

        image = QtGui.QImage(file_path)
        if image.isNull():
            self.error_occurred.emit(f"Unable to load image file: {file_path}")
            return

        self.set_image(image)

    def clear_image(self):
        self.image = None
        self.update()
        self.image_changed.emit(QtGui.QImage())

    def set_edit_enabled(self, enabled):
        self.edit_enabled = bool(enabled)
        self.setCursor(
            QtCore.Qt.CursorShape.CrossCursor
            if self.edit_enabled
            else QtCore.Qt.CursorShape.ArrowCursor
        )

    def set_brush_value(self, value):
        self.brush_value = max(0, min(int(value), 255))

    def set_brush_radius(self, radius):
        self.brush_radius = max(1, int(radius))

    def _display_geometry(self):
        if self.image is None or self.image.isNull():
            return None, None

        target = self.rect().adjusted(8, 8, -8, -8)
        if target.width() <= 0 or target.height() <= 0:
            return None, None

        scaled = self.image.scaled(
            target.size(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.FastTransformation,
        )
        if scaled.isNull():
            return None, None

        x = target.x() + (target.width() - scaled.width()) // 2
        y = target.y() + (target.height() - scaled.height()) // 2
        return scaled, QtCore.QRect(x, y, scaled.width(), scaled.height())

    def _widget_point_to_image_point(self, point):
        scaled, image_rect = self._display_geometry()
        if image_rect is None or scaled is None or not image_rect.contains(point):
            return None

        rel_x = (point.x() - image_rect.x()) / max(image_rect.width(), 1)
        rel_y = (point.y() - image_rect.y()) / max(image_rect.height(), 1)

        image_x = int(rel_x * self.image.width())
        image_y = int(rel_y * self.image.height())

        image_x = max(0, min(image_x, self.image.width() - 1))
        image_y = max(0, min(image_y, self.image.height() - 1))
        return QtCore.QPoint(image_x, image_y)

    def _paint_at(self, point):
        if not self.edit_enabled or self.image is None or self.image.isNull():
            return

        image_point = self._widget_point_to_image_point(point)
        if image_point is None:
            return

        painter = QtGui.QPainter(self.image)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(self.brush_value, self.brush_value, self.brush_value))
        radius = max(1, int(self.brush_radius))
        painter.drawEllipse(image_point, radius, radius)
        painter.end()

        self.update()
        self.image_changed.emit(self.image)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self.edit_enabled:
            self._dragging = True
            self._paint_at(event.position().toPoint())
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self.edit_enabled:
            self._paint_at(event.position().toPoint())
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        if self.image is None or self.image.isNull():
            painter.drawText(self.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, "No image loaded")
            return

        scaled, image_rect = self._display_geometry()
        if scaled is None or image_rect is None:
            return

        painter.drawImage(image_rect.topLeft(), scaled)


class ImageEdit(QtWidgets.QWidget):
    image_changed = QtCore.Signal(QtGui.QImage)
    error_occurred = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.canvas = _ImageCanvas()
        self.canvas.image_changed.connect(self.image_changed.emit)
        self.canvas.error_occurred.connect(self.error_occurred.emit)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    @QtCore.Slot(bool)
    def set_edit_enabled(self, enabled):
        self.canvas.set_edit_enabled(enabled)

    def set_image(self, image):
        self.canvas.set_image(image)

    def open_image_file(self, file_path):
        self.canvas.open_image_file(file_path)

    def clear_image(self):
        self.canvas.clear_image()

    def set_brush_value(self, value):
        self.canvas.set_brush_value(value)

    def set_brush_radius(self, radius):
        self.canvas.set_brush_radius(radius)

    def current_image(self):
        return self.canvas.image


def preview():
    preview_widget(ImageEdit)


if __name__ == "__main__":
    preview()
