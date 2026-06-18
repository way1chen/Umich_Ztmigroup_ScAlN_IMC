from PySide6 import QtWidgets, QtCore, QtGui
from gui.widgets.preview_util import preview_widget


class _EditCanvas(QtWidgets.QWidget):
    image_changed = QtCore.Signal(QtGui.QImage)
    error_occurred = QtCore.Signal(str)
    zoom_changed = QtCore.Signal(float)

    MAX_ZOOM_FACTOR = 256.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.edit_enabled = False
        self.brush_value = 0
        self.brush_radius = 8.0
        self.pixel_grid_visible = True
        self.zoom_factor = 1.0
        self.fit_zoom_factor = 1.0
        self.pan_offset = QtCore.QPointF(0.0, 0.0)

        self._dragging_paint = False
        self._dragging_pan = False
        self._pan_last_pos = None
        self._mouse_pos = None
        self._fit_pending = False
        self._fit_mode = True

        self.setMinimumSize(150, 150)
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

    def set_image(self, image):
        if image is None or image.isNull():
            self.image = None
            self.update()
            return

        self.image = image.convertToFormat(QtGui.QImage.Format.Format_Grayscale8)
        self._fit_pending = True
        self.fit_to_view()
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
        self.update()

    def set_brush_value(self, value):
        self.brush_value = max(0, min(int(value), 255))
        self.update()

    def set_brush_radius(self, radius):
        self.brush_radius = max(1.0, float(radius))
        self.update()

    def set_pixel_grid_visible(self, enabled):
        self.pixel_grid_visible = bool(enabled)
        self.update()

    def set_zoom_factor(self, zoom_factor, anchor=None, *, keep_fit_mode=False):
        if self.image is None or self.image.isNull():
            return

        old_zoom = self.zoom_factor
        new_zoom = max(0.1, min(float(zoom_factor), self.MAX_ZOOM_FACTOR))
        if abs(new_zoom - old_zoom) < 1e-6:
            return

        if anchor is None:
            anchor = QtCore.QPointF(self.width() / 2.0, self.height() / 2.0)
        elif isinstance(anchor, QtCore.QPoint):
            anchor = QtCore.QPointF(float(anchor.x()), float(anchor.y()))

        image_anchor_x = (anchor.x() - self.pan_offset.x()) / old_zoom
        image_anchor_y = (anchor.y() - self.pan_offset.y()) / old_zoom

        self.zoom_factor = new_zoom
        self.pan_offset = QtCore.QPointF(
            anchor.x() - image_anchor_x * new_zoom,
            anchor.y() - image_anchor_y * new_zoom,
        )
        self._fit_mode = bool(keep_fit_mode)
        self.zoom_changed.emit(self.zoom_factor)
        self.update()

    def zoom_in(self, anchor=None):
        self.set_zoom_factor(self.zoom_factor * 1.25, anchor=anchor)

    def zoom_out(self, anchor=None):
        self.set_zoom_factor(self.zoom_factor / 1.25, anchor=anchor)

    def fit_to_view(self):
        if self.image is None or self.image.isNull():
            return

        available_width = max(self.width() - 16, 1)
        available_height = max(self.height() - 16, 1)
        zoom_x = available_width / max(self.image.width(), 1)
        zoom_y = available_height / max(self.image.height(), 1)
        zoom = min(zoom_x, zoom_y)
        self.fit_zoom_factor = max(0.1, min(float(zoom), self.MAX_ZOOM_FACTOR))
        self.zoom_factor = self.fit_zoom_factor
        self.pan_offset = QtCore.QPointF(
            (self.width() - self.image.width() * self.zoom_factor) / 2.0,
            (self.height() - self.image.height() * self.zoom_factor) / 2.0,
        )
        self._fit_pending = False
        self._fit_mode = True
        self.zoom_changed.emit(self.zoom_factor)
        self.update()

    def reset_view(self):
        if self.image is None or self.image.isNull():
            return

        self.zoom_factor = self.fit_zoom_factor
        self.pan_offset = QtCore.QPointF(
            (self.width() - self.image.width() * self.zoom_factor) / 2.0,
            (self.height() - self.image.height() * self.zoom_factor) / 2.0,
        )
        self._fit_mode = False
        self.zoom_changed.emit(self.zoom_factor)
        self.update()

    def _image_rect(self):
        if self.image is None or self.image.isNull():
            return None

        width = self.image.width() * self.zoom_factor
        height = self.image.height() * self.zoom_factor
        return QtCore.QRectF(self.pan_offset.x(), self.pan_offset.y(), width, height)

    def _widget_point_to_image_point(self, point):
        image_rect = self._image_rect()
        if image_rect is None or not image_rect.contains(QtCore.QPointF(point)):
            return 0, 0

        rel_x = (point.x() - image_rect.x()) / max(self.zoom_factor, 1e-6)
        rel_y = (point.y() - image_rect.y()) / max(self.zoom_factor, 1e-6)

        image_x = rel_x
        image_y = rel_y



        image_x = max(0, min(image_x, self.image.width() - 1))
        image_y = max(0, min(image_y, self.image.height() - 1))
        return image_x, image_y

    def _brush_radius_in_image_pixels(self):
        return max(0, self.brush_radius / max(self.zoom_factor, 1e-6))

    def _paint_image_pixel(self, image_x, image_y, alpha):
        if image_x < 0 or image_y < 0:
            return
        if image_x >= self.image.width() or image_y >= self.image.height():
            return

        current_value = QtGui.QColor(self.image.pixel(image_x, image_y)).red()
        new_value = max(0, min(current_value * (1 - alpha) + self.brush_value * alpha, 255))

        self.image.setPixelColor(
            image_x,
            image_y,
            QtGui.QColor(new_value, new_value, new_value),
        )

    def _paint_at(self, point):
        if not self.edit_enabled or self.image is None or self.image.isNull():
            return

        center_x, center_y = self._widget_point_to_image_point(point)

        radius = max(1, self._brush_radius_in_image_pixels())

        

     

        for image_y in range(int(center_y - radius), int(center_y + radius + 1)):
            for image_x in range(int(center_x - radius), int(center_x + radius + 1)):
                delta_x = (image_x + 0.5) - center_x
                delta_y = (image_y + 0.5) - center_y
                distance_squared = delta_x * delta_x + delta_y * delta_y


                normalized_distance = (distance_squared ** 0.5) / radius
                falloff = max(0.0, 1.0 - normalized_distance)
               
                

        

                self._paint_image_pixel(image_x, image_y, falloff)

        self.update()
        self.image_changed.emit(self.image)

    def mousePressEvent(self, event):
        self._mouse_pos = event.position().toPoint()

        if event.button() == QtCore.Qt.MouseButton.MiddleButton or event.button() == QtCore.Qt.MouseButton.RightButton:
            self._dragging_pan = True
            self._pan_last_pos = event.position().toPoint()
            event.accept()
            return

        if event.button() == QtCore.Qt.MouseButton.LeftButton and self.edit_enabled:
            self._dragging_paint = True
            self._paint_at(event.position().toPoint())
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self._mouse_pos = event.position().toPoint()

        if self._dragging_pan and self._pan_last_pos is not None:
            delta = event.position().toPoint() - self._pan_last_pos
            self.pan_offset += QtCore.QPointF(float(delta.x()), float(delta.y()))
            self._pan_last_pos = event.position().toPoint()
            self.update()
            event.accept()
            return

        if self._dragging_paint and self.edit_enabled:
            self._paint_at(event.position().toPoint())
            event.accept()
            return

        self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._mouse_pos = event.position().toPoint()

        if event.button() in (QtCore.Qt.MouseButton.MiddleButton, QtCore.Qt.MouseButton.RightButton):
            self._dragging_pan = False
            self._pan_last_pos = None
            event.accept()
            return

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._dragging_paint = False
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if event.angleDelta().y() == 0:
            super().wheelEvent(event)
            return

        if event.angleDelta().y() > 0:
            self.zoom_in(anchor=event.position().toPoint())
        else:
            self.zoom_out(anchor=event.position().toPoint())
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image is not None and not self.image.isNull() and self._fit_mode:
            self.fit_to_view()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform, False)
        painter.fillRect(self.rect(), QtGui.QColor(28, 28, 28))

        if self.image is None or self.image.isNull():
            painter.setPen(QtGui.QColor(220, 220, 220))
            painter.drawText(self.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, "No image loaded")
            return

        image_rect = self._image_rect()
        if image_rect is None:
            return

        painter.drawImage(image_rect, self.image)

        if self.pixel_grid_visible and self.zoom_factor >= 1.0:
            grid_pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 70), 1)
            painter.setPen(grid_pen)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)

            left = int(round(image_rect.left()))
            top = int(round(image_rect.top()))
            right = int(round(image_rect.right()))
            bottom = int(round(image_rect.bottom()))

            for column in range(self.image.width() + 1):
                x = left + int(round(column * self.zoom_factor))
                painter.drawLine(x, top, x, bottom)

            for row in range(self.image.height() + 1):
                y = top + int(round(row * self.zoom_factor))
                painter.drawLine(left, y, right, y)

        if self.edit_enabled and self._mouse_pos is not None:
            brush_radius = self.brush_radius
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 220), 1, QtCore.Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawEllipse(
                QtCore.QPointF(float(self._mouse_pos.x()), float(self._mouse_pos.y())),
                brush_radius,
                brush_radius,
            )


class EditPanel(QtWidgets.QWidget):
    image_changed = QtCore.Signal(QtGui.QImage)
    error_occurred = QtCore.Signal(str)
    zoom_changed = QtCore.Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.canvas = _EditCanvas()

        self.zoom_out_button = QtWidgets.QToolButton()
        self.zoom_out_button.setText("-")
        self.zoom_in_button = QtWidgets.QToolButton()
        self.zoom_in_button.setText("+")
        self.fit_button = QtWidgets.QToolButton()
        self.fit_button.setText("Fit")
        self.reset_button = QtWidgets.QToolButton()
        self.reset_button.setText("100%")
        self.blank_canvas_button = QtWidgets.QToolButton()
        self.blank_canvas_button.setText("Blank Canvas")
        self.pixel_grid_toggle = QtWidgets.QCheckBox("Show pixel grid")
        self.pixel_grid_toggle.setChecked(False)
        self.zoom_label = QtWidgets.QLabel("Zoom: 100%")
        self.state_label = QtWidgets.QLabel("Brush: 8 px")
        self.help_label = QtWidgets.QLabel("Wheel to zoom. Middle or right drag to pan.")
        self.help_label.setWordWrap(True)
        self.help_label.setStyleSheet("color: #777;")

        toolbar = QtWidgets.QWidget()
        toolbar_layout = QtWidgets.QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.addWidget(self.zoom_out_button)
        toolbar_layout.addWidget(self.zoom_in_button)
        toolbar_layout.addWidget(self.fit_button)
        toolbar_layout.addWidget(self.reset_button)
        toolbar_layout.addWidget(self.blank_canvas_button)
        toolbar_layout.addWidget(self.pixel_grid_toggle)
        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(self.zoom_label)
        toolbar_layout.addSpacing(12)
        toolbar_layout.addWidget(self.state_label)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas, 1)
        layout.addWidget(self.help_label)
        self.setLayout(layout)

        self.zoom_in_button.pressed.connect(self.canvas.zoom_in)
        self.zoom_out_button.pressed.connect(self.canvas.zoom_out)
        self.fit_button.pressed.connect(self.canvas.fit_to_view)
        self.reset_button.pressed.connect(self.canvas.reset_view)
        self.blank_canvas_button.pressed.connect(self.create_blank_canvas)
        self.pixel_grid_toggle.toggled.connect(self.canvas.set_pixel_grid_visible)

        self.canvas.image_changed.connect(self.image_changed.emit)
        self.canvas.error_occurred.connect(self.error_occurred.emit)
        self.canvas.zoom_changed.connect(self._handle_zoom_changed)

        self.canvas.set_pixel_grid_visible(self.pixel_grid_toggle.isChecked())

    @QtCore.Slot(float)
    def _handle_zoom_changed(self, zoom_factor):
        fit_zoom = max(self.canvas.fit_zoom_factor, 1e-6)
        relative_zoom = zoom_factor / fit_zoom
        self.zoom_label.setText(f"Zoom: {int(round(relative_zoom * 100))}%")
        self._update_state_label()
        self.zoom_changed.emit(zoom_factor)

    def _update_state_label(self):
        screen_radius = self.canvas.brush_radius
        image_radius = self.canvas._brush_radius_in_image_pixels()

        self.state_label.setText(
            f"Brush: {screen_radius:.0f}px screen / {image_radius:.2f}px image"
        )

    def set_image(self, image):
        self.canvas.set_image(image)

    def open_image_file(self, file_path):
        self.canvas.open_image_file(file_path)

    def clear_image(self):
        self.canvas.clear_image()

    def create_blank_canvas(self):
        blank_image = QtGui.QImage(20, 20, QtGui.QImage.Format.Format_Grayscale8)
        blank_image.fill(0)
        self.set_image(blank_image)

    def set_edit_enabled(self, enabled):
        self.canvas.set_edit_enabled(enabled)

    def set_brush_value(self, value):
        self.canvas.set_brush_value(value)
        self._update_state_label()

    def set_brush_radius(self, radius):
        self.canvas.set_brush_radius(radius)
        self._update_state_label()

    def set_pixel_grid_visible(self, enabled):
        self.pixel_grid_toggle.setChecked(bool(enabled))

    def fit_to_view(self):
        self.canvas.fit_to_view()

    def zoom_in(self):
        self.canvas.zoom_in()

    def zoom_out(self):
        self.canvas.zoom_out()

    def reset_view(self):
        self.canvas.reset_view()

    def current_image(self):
        return self.canvas.image


def preview():
    preview_widget(EditPanel)


if __name__ == "__main__":
    preview()
