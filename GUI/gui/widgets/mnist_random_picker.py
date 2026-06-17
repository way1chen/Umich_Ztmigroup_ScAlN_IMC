from __future__ import annotations

import random
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from gui.utils.mnist_idx import load_mnist_labels, load_mnist_samples
from gui.widgets.preview_util import preview_widget


class MnistRandomPicker(QtWidgets.QWidget):
    """Pick a random image from the MNIST test set and emit it as QImage."""

    image_picked = QtCore.Signal(QtGui.QImage)
    digit_picked = QtCore.Signal(int)
    error_occurred = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        archive_dir = Path(__file__).resolve().parents[1] / "archive"
        self._image_idx_path = archive_dir / "t10k-images.idx3-ubyte"
        self._label_idx_path = archive_dir / "t10k-labels.idx1-ubyte"

        self._labels: list[int] | None = None
        self._sample_count: int | None = None
        self._indices_by_digit: dict[int, list[int]] = {}

        self.mode_select = QtWidgets.QComboBox()
        self.mode_select.addItem("Random image", userData="any")
        self.mode_select.addItem("Random number", userData="digit")
        self.mode_select.addItem("Choose index", userData="index")

        self.digit_select = QtWidgets.QComboBox()
        for digit in range(10):
            self.digit_select.addItem(str(digit), userData=digit)
        self.digit_select.setEnabled(False)

        self.index_select = QtWidgets.QSpinBox()
        self.index_select.setEnabled(False)
        self.index_select.setRange(0, 0)
        self.index_select.setSingleStep(1)
        self.index_select.setPrefix("Index: ")

        self.pick_button = QtWidgets.QPushButton("Pick Image")
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("MNIST Test Dataset"))
        layout.addWidget(self.mode_select)
        layout.addWidget(self.digit_select)
        layout.addWidget(self.index_select)
        layout.addWidget(self.pick_button)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        self.mode_select.currentIndexChanged.connect(self._handle_mode_changed)
        self.pick_button.pressed.connect(self.pick_random_image)

    @QtCore.Slot()
    def _handle_mode_changed(self):
        current_mode = self.mode_select.currentData()
        choose_digit = current_mode == "digit"
        choose_index = current_mode == "index"
        self.digit_select.setEnabled(choose_digit)
        self.index_select.setEnabled(choose_index)

        if choose_index:
            self._ensure_labels_loaded()

    def _ensure_labels_loaded(self):
        if self._labels is not None:
            return
        try:
            labels = load_mnist_labels(self._label_idx_path)
        except Exception as exc:
            msg = f"Failed to load MNIST labels: {exc}"
            self.status_label.setText(msg)
            self.error_occurred.emit(msg)
            return

        self._labels = labels
        self._sample_count = len(labels)
        self.index_select.setRange(0, max(self._sample_count - 1, 0))

        indices_by_digit: dict[int, list[int]] = {digit: [] for digit in range(10)}
        for index, label in enumerate(labels):
            if 0 <= label <= 9:
                indices_by_digit[label].append(index)

        self._indices_by_digit = indices_by_digit

    @QtCore.Slot()
    def pick_random_image(self):
        try:
            self._ensure_labels_loaded()
            if not self._labels:
                msg = "MNIST labels are empty."
                self.status_label.setText(msg)
                self.error_occurred.emit(msg)
                return

            mode = self.mode_select.currentData()
            if mode == "digit":
                digit = int(self.digit_select.currentData())
                candidates = self._indices_by_digit.get(digit, [])
                if not candidates:
                    msg = f"No test images found for digit {digit}."
                    self.status_label.setText(msg)
                    self.error_occurred.emit(msg)
                    return
                sample_index = random.choice(candidates)
            elif mode == "index":
                sample_index = int(self.index_select.value())
            else:
                sample_index = random.randrange(len(self._labels))

            if self._sample_count is not None:
                sample_index = max(0, min(sample_index, self._sample_count - 1))

            samples = load_mnist_samples(
                image_path=self._image_idx_path,
                label_path=self._label_idx_path,
                start=sample_index,
                limit=1,
            )
            if not samples:
                msg = "Failed to load a MNIST sample."
                self.status_label.setText(msg)
                self.error_occurred.emit(msg)
                return

            sample = samples[0]
            self.image_picked.emit(sample.image)
            self.digit_picked.emit(int(sample.label))
            self.status_label.setText(
                f"Loaded test sample index {sample_index} (digit {sample.label})."
            )
        except Exception as exc:
            msg = f"MNIST load error: {exc}"
            self.status_label.setText(msg)
            self.error_occurred.emit(msg)


def preview():
    preview_widget(MnistRandomPicker)


if __name__ == "__main__":
    preview()
