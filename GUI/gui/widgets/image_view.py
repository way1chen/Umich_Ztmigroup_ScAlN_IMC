from PySide6 import QtWidgets, QtCore, QtGui
from gui.widgets.preview_util import preview_widget


class ImageView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None

        self.setMinimumSize(150, 150)


    def set_image(self, image):
        self.image = image
        self.update()

    def open_image_file(self, file_path):
        if not file_path:
            return

        img = QtGui.QImage(file_path)
        if img.isNull():
            return

        self.set_image(img.convertToFormat(QtGui.QImage.Format.Format_Grayscale8))


    def clear_image(self):
        self.image = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.image is None:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        target = self.rect().adjusted(8, 8, -8, -8)
        scaled = self.image.scaled(
            target.size(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.FastTransformation,
        )

        x = target.x() + (target.width() - scaled.width()) // 2
        y = target.y() + (target.height() - scaled.height()) // 2

        painter.drawImage(x, y, scaled)

    

def preview():
    preview_widget(ImageView)


if __name__ == "__main__":
    preview()
