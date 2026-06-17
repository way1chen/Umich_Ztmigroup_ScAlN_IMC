from collections.abc import Mapping

from PySide6 import QtWidgets, QtCore
from gui.widgets.preview_util import preview_widget


class ClassificationResultsPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        #Define Child Widgets
        self.confidences = []
        self.predicted_digit = None
        self.actual_digit = None

        self.title_label = QtWidgets.QLabel("MNIST Classification Results")
        self.title_label.setObjectName("panelTitle")

        self.prediction_label = QtWidgets.QLabel("Predicted Digit")
        self.prediction_value = QtWidgets.QLabel("-")
        self.prediction_value.setObjectName("predictionValue")

        self.actual_label = QtWidgets.QLabel("Actual Digit")
        self.actual_digit_input = QtWidgets.QSpinBox()
        self.actual_digit_input.setRange(-1, 9)
        self.actual_digit_input.setSpecialValueText("-")
        self.actual_digit_input.setValue(-1)

        self.correctness_label = QtWidgets.QLabel("Correctness")
        self.correctness_value = QtWidgets.QLabel("Waiting for actual digit")
        self.correctness_value.setObjectName("correctnessValue")

        self.summary_card = QtWidgets.QFrame()
        self.summary_card.setObjectName("summaryCard")
        summary_layout = QtWidgets.QGridLayout(self.summary_card)
        summary_layout.setContentsMargins(12, 12, 12, 12)
        summary_layout.setHorizontalSpacing(16)
        summary_layout.setVerticalSpacing(10)
        summary_layout.addWidget(self.prediction_label, 0, 0)
        summary_layout.addWidget(self.prediction_value, 0, 1)
        summary_layout.addWidget(self.actual_label, 1, 0)
        summary_layout.addWidget(self.actual_digit_input, 1, 1)
        summary_layout.addWidget(self.correctness_label, 2, 0)
        summary_layout.addWidget(self.correctness_value, 2, 1)

        self.confidence_title = QtWidgets.QLabel("Confidence Ranking")
        self.confidence_title.setObjectName("sectionTitle")

        self.confidence_container = QtWidgets.QWidget()
        self.confidence_layout = QtWidgets.QVBoxLayout(self.confidence_container)
        self.confidence_layout.setContentsMargins(0, 0, 0, 0)
        self.confidence_layout.setSpacing(8)
        self.confidence_layout.addStretch(1)

        confidence_scroll = QtWidgets.QScrollArea()
        confidence_scroll.setWidgetResizable(True)
        confidence_scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        confidence_scroll.setWidget(self.confidence_container)

        #Define Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(self.title_label)
        layout.addWidget(self.summary_card)
        layout.addWidget(self.confidence_title)
        layout.addWidget(confidence_scroll, 1)

        #Define Signal-Slot Connections
        self.actual_digit_input.valueChanged.connect(self.set_actual_digit)

    def _clear_confidence_rows(self):
        while self.confidence_layout.count():
            item = self.confidence_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.confidence_layout.addStretch(1)

    def _format_confidence(self, value, normalized_value):
        if 0.0 <= value <= 1.0:
            return f"{value * 100:.1f}%"
        return f"{value:.3f}"

    def _update_summary(self):
        if self.predicted_digit is None:
            self.prediction_value.setText("-")
        else:
            self.prediction_value.setText(str(self.predicted_digit))

        if self.predicted_digit is None or self.actual_digit is None:
            self.correctness_value.setText("Waiting for actual digit")
            return

        is_correct = self.predicted_digit == self.actual_digit
        self.correctness_value.setText("Correct" if is_correct else "Incorrect")

    @QtCore.Slot(object)
    def set_confidences(self, confidences):
        if confidences is None:
            self.confidences = []
            self.predicted_digit = None
            self._clear_confidence_rows()
            self._update_summary()
            return

        if isinstance(confidences, Mapping):
            items = []
            for key, value in confidences.items():
                try:
                    digit = int(key)
                except (TypeError, ValueError):
                    continue
                items.append((digit, float(value)))
        else:
            values = list(confidences)
            items = [(index, float(value)) for index, value in enumerate(values)]

        items.sort(key=lambda item: item[1], reverse=True)
        self.confidences = items
        self.predicted_digit = items[0][0] if items else None

        self._clear_confidence_rows()

        if not items:
            self._update_summary()
            return

        total = sum(max(value, 0.0) for _, value in items)
        if total <= 0:
            total = 1.0

        for digit, value in items:
            normalized_value = max(value, 0.0) / total

            row = QtWidgets.QWidget()
            row_layout = QtWidgets.QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)

            digit_label = QtWidgets.QLabel(f"{digit}")
            digit_label.setMinimumWidth(24)
            digit_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            bar = QtWidgets.QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(round(normalized_value * 100))
            bar.setTextVisible(False)

            value_label = QtWidgets.QLabel(self._format_confidence(value, normalized_value))
            value_label.setMinimumWidth(64)
            value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)

            row_layout.addWidget(digit_label)
            row_layout.addWidget(bar, 1)
            row_layout.addWidget(value_label)
            self.confidence_layout.insertWidget(self.confidence_layout.count() - 1, row)

        self._update_summary()

    @QtCore.Slot(int)
    def set_actual_digit(self, digit):
        digit = int(digit)
        self.actual_digit = None if digit < 0 else digit

        if self.actual_digit_input.value() != digit:
            self.actual_digit_input.blockSignals(True)
            self.actual_digit_input.setValue(digit)
            self.actual_digit_input.blockSignals(False)

        self._update_summary()


def preview():
    preview_widget(ClassificationResultsPanel)


if __name__ == "__main__":
    preview()
