from PySide6 import QtCore, QtGui
import serial

from gui.widgets.processing_mode import ProcessingMode

"""Serial manager for communicating with the image-processing MCU.

This module provides two Qt-friendly components:
- `SerialWorker`: runs in a background `QThread`, performs non-blocking serial I/O,
    and emits Qt signals for incoming data and images.
- `SerialManager`: a main-thread facade that creates the worker thread and
    exposes simple slots/signals for the rest of the application to use.

Protocol (simple line-based header + raw payload):
- The app sends a command line (e.g. "BLUR_LIGHT\n"), followed immediately by
    exactly 400 bytes of 8-bit grayscale image data (20x20).
- The MCU responds with a newline-terminated header like "OK|400\n" then
    exactly 400 bytes of grayscale image data.

The worker handles assembling partial reads and emits `image_received` when
an entire processed frame is available as `QImage`.
"""


class SerialWorker(QtCore.QObject):
    """Background worker that performs serial reads/writes.

    Signals:
    - `data_received(str)`: arbitrary text lines received when not part of image flow.
    - `image_received(QImage)`: emitted when a full 20x20 processed image arrives.
    - `error_occurred(str)`: non-fatal error messages.
    - `port_opened(str)`, `port_closed()`, `disconnected()`: lifecycle events.
    """

    data_received = QtCore.Signal(str)
    image_received = QtCore.Signal(QtGui.QImage)
    error_occurred = QtCore.Signal(str)
    port_opened = QtCore.Signal(str)
    port_closed = QtCore.Signal()
    disconnected = QtCore.Signal()

    def __init__(self, baudrate=115200, parent=None):
        super().__init__(parent)

        self.baudrate = baudrate
        self.serial_port = None

        # Receiving state -------------------------------------------------
        # _rx_buffer: accumulated bytes read from the serial port
        # _awaiting_image_reply: True when we've sent an image and expect a framed reply
        # _awaiting_image_header: True while waiting for the newline-terminated header
        # _expected_image_size: how many raw payload bytes to wait for (400)
        self._rx_buffer = bytearray()
        self._awaiting_image_reply = False
        self._awaiting_image_header = False
        self._expected_image_size = 0

        self.poll_timer = QtCore.QTimer(self)
        self.poll_timer.setInterval(10)
        self.poll_timer.timeout.connect(self._poll_serial)


    @QtCore.Slot(str)
    def open_port(self, port_name):
        """Open the named serial `port_name` and start polling for data.

        This method is a Qt Slot and is expected to be invoked via a queued
        connection from the main thread.
        """

        # Ensure any existing port/worker is closed before opening a new one
        self.close_port()

        try:
            self.serial_port = serial.Serial(
                port_name,
                self.baudrate,
                timeout=0,
                write_timeout=2,
            )
        except serial.SerialException as exc:
            self.error_occurred.emit(f"Failed to open port {port_name}: {exc}")
            self.disconnected.emit()
            return

        self._reset_receive_state()
        self.poll_timer.start()
        self.port_opened.emit(port_name)


    @QtCore.Slot()
    def close_port(self):
        """Stop polling and close the serial port (if open).

        Safe to call multiple times.
        """

        self.poll_timer.stop()
        self._reset_receive_state()

        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
            except serial.SerialException:
                pass

        self.serial_port = None
        self.port_closed.emit()


    @QtCore.Slot(str)
    def send_text(self, text):
        """Send a newline-terminated text command over serial.

        Used for human-readable or control messages outside the image flow.
        """

        if not self._is_port_open():
            self.error_occurred.emit("No serial port is open")
            return

        try:
            self.serial_port.write((text + "\n").encode("utf-8"))
        except serial.SerialException as exc:
            self.error_occurred.emit(f"Failed to send text: {exc}")
            self.disconnected.emit()


    @QtCore.Slot(object, object)
    def process_image_file(self, file_or_image, mode):
        """Submit an image for processing.

        `file_or_image` may be:
        - `str`: a filesystem path (legacy behaviour)
        - `QtGui.QImage`: use directly
        - `bytes`/`bytearray`: raw 400-byte payload

        `mode` should usually be a `ProcessingMode` enum. For backward
        compatibility, a plain string command is also accepted.
        """

        if self._awaiting_image_reply:
            self.error_occurred.emit("Image processing request already in progress")
            return

        if not self._is_port_open():
            self.error_occurred.emit("No serial port is open")
            return

        payload = None

        # Accept a file path, a QImage, or raw bytes/bytearray
        if isinstance(file_or_image, str):
            payload = self._load_20x20_grayscale_payload(file_or_image)
        elif isinstance(file_or_image, QtGui.QImage):
            payload = self._payload_from_qimage(file_or_image)
        elif isinstance(file_or_image, (bytes, bytearray)):
            payload = bytes(file_or_image)
            if len(payload) != 400:
                self.error_occurred.emit("Unexpected grayscale payload size")
                return
        else:
            self.error_occurred.emit("Unsupported image input type")
            return

        if payload is None:
            # `_load_20x20_grayscale_payload` or `_payload_from_qimage` emitted an error
            return

        command = self._mode_to_serial_command(mode)
        if command is None:
            return

        try:
            # Prepare state so incoming bytes are handled as an image reply
            self._rx_buffer.clear()
            self._awaiting_image_reply = True
            self._awaiting_image_header = True
            self._expected_image_size = 400

            # Send command line then raw payload
            self.serial_port.write((command + "\n").encode("utf-8"))
            self.serial_port.write(payload)
            self.serial_port.flush()
        except serial.SerialException as exc:
            self._reset_receive_state()
            self.error_occurred.emit(f"Failed to submit image: {exc}")
            self.disconnected.emit()


    def _is_port_open(self):
        return self.serial_port is not None and self.serial_port.is_open


    def _reset_receive_state(self):
        """Clear receive buffer and reset reply-tracking flags."""
        self._rx_buffer.clear()
        self._awaiting_image_reply = False
        self._awaiting_image_header = False
        self._expected_image_size = 0


    def _mode_to_serial_command(self, mode):
        """Normalize a UI-level mode into the MCU command string.

        The enum is the preferred input. A raw string is accepted as a fallback
        so older callers continue to work during the transition.
        """

        if isinstance(mode, ProcessingMode):
            return mode.serial_command

        if isinstance(mode, str):
            try:
                return ProcessingMode.from_display_text(mode).serial_command
            except ValueError:
                return mode

        self.error_occurred.emit("Unsupported processing mode type")
        return None


    def _load_20x20_grayscale_payload(self, file_path):
        """Load an image file and convert to a 20x20 8-bit grayscale payload.

        Returns bytes of length 400 on success, otherwise emits `error_occurred`
        and returns `None`.
        """

        image = QtGui.QImage(file_path)
        if image.isNull():
            self.error_occurred.emit(f"Failed to load image: {file_path}")
            return None

        image = image.scaled(
            20,
            20,
            QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        image = image.convertToFormat(QtGui.QImage.Format.Format_Grayscale8)

        # Extract raw bytes from the QImage
        bits = image.bits()
        bits.setsize(image.sizeInBytes())
        payload = bytes(bits)

        if len(payload) != 400:
            self.error_occurred.emit("Unexpected grayscale payload size")
            return None

        return payload


    def _payload_from_qimage(self, image: QtGui.QImage):
        """Convert a `QImage` to a 20x20 grayscale payload.

        Preserves behaviour of file-loader but accepts an already-constructed
        `QImage` (useful for drawing widgets or in-memory sources).
        """

        if image.isNull():
            self.error_occurred.emit("Provided QImage is null")
            return None

        img = image.scaled(
            20,
            20,
            QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        img = img.convertToFormat(QtGui.QImage.Format.Format_Grayscale8)

        bits = img.bits()
        bits.setsize(img.sizeInBytes())
        payload = bytes(bits)

        if len(payload) != 400:
            self.error_occurred.emit("Unexpected grayscale payload size")
            return None

        return payload


    def _poll_serial(self):
        """Timer-driven poll that reads available bytes and processes them.

        Uses non-blocking reads (pyserial timeout=0) and accumulates data in
        `_rx_buffer` for reassembly.
        """

        if not self._is_port_open():
            return

        available = self.serial_port.in_waiting
        if available <= 0:
            return

        try:
            chunk = self.serial_port.read(available)
        except serial.SerialException as exc:
            self._reset_receive_state()
            self.error_occurred.emit(f"Serial read failed: {exc}")
            self.disconnected.emit()
            return

        if not chunk:
            return

        # Append and attempt to parse complete messages/frames
        self._rx_buffer.extend(chunk)
        self._drain_receive_buffer()


    def _drain_receive_buffer(self):
        # Attempt to parse either an image reply (header + raw payload) or
        # standalone newline-terminated text lines.
        while self._rx_buffer:
            # If we are expecting an image reply, first parse the header line
            if self._awaiting_image_reply:
                if self._awaiting_image_header:
                    newline_index = self._rx_buffer.find(b"\n")
                    if newline_index < 0:
                        # header not complete yet
                        return

                    header = bytes(self._rx_buffer[:newline_index]).strip()
                    del self._rx_buffer[: newline_index + 1]

                    # Expect the MCU to respond with 'OK|400' before raw bytes
                    if header != b"OK|400":
                        self._reset_receive_state()
                        self.error_occurred.emit(
                            f"Unexpected image reply header: {header.decode(errors='ignore')}"
                        )
                        return

                    # Header consumed; next we await the fixed-size payload
                    self._awaiting_image_header = False
                    continue

                # Wait until we have the full raw payload
                if len(self._rx_buffer) < self._expected_image_size:
                    return

                payload = bytes(self._rx_buffer[: self._expected_image_size])
                del self._rx_buffer[: self._expected_image_size]

                # Construct a QImage from the raw grayscale bytes
                image = QtGui.QImage(
                    payload,
                    20,
                    20,
                    20,
                    QtGui.QImage.Format.Format_Grayscale8,
                ).copy()

                # Reset state and emit the image for the UI to consume
                self._reset_receive_state()
                self.image_received.emit(image)
                continue

            # Otherwise, parse a text line (non-image protocol)
            newline_index = self._rx_buffer.find(b"\n")
            if newline_index < 0:
                return

            line = bytes(self._rx_buffer[:newline_index]).strip()
            del self._rx_buffer[: newline_index + 1]

            if line:
                self.data_received.emit(line.decode(errors="ignore"))


class SerialManager(QtCore.QObject):
    data_received = QtCore.Signal(str)
    image_received = QtCore.Signal(QtGui.QImage)
    error_occurred = QtCore.Signal(str)
    port_opened = QtCore.Signal(str)
    port_closed = QtCore.Signal()
    disconnected = QtCore.Signal()

    request_open_port = QtCore.Signal(str)
    request_close_port = QtCore.Signal()
    request_send_text = QtCore.Signal(str)
    # Accept an object (str file path, QtGui.QImage, or bytes/bytearray) plus the mode
    request_process_image = QtCore.Signal(object, str)

    def __init__(self):
        super().__init__()

        self.worker_thread = None
        self.worker = None


    @QtCore.Slot(str)
    def open_port(self, port):
        self.close_port()

        self.worker_thread = QtCore.QThread(self)
        self.worker = SerialWorker()
        self.worker.moveToThread(self.worker_thread)

        self.worker.data_received.connect(self.data_received.emit)
        self.worker.image_received.connect(self.image_received.emit)
        self.worker.error_occurred.connect(self.error_occurred.emit)
        self.worker.port_opened.connect(self.port_opened.emit)
        self.worker.port_closed.connect(self.port_closed.emit)
        self.worker.disconnected.connect(self._handle_worker_disconnect)
        self.worker.port_closed.connect(self.worker_thread.quit)

        self.request_open_port.connect(self.worker.open_port)
        self.request_close_port.connect(self.worker.close_port)
        self.request_send_text.connect(self.worker.send_text)
        self.request_process_image.connect(self.worker.process_image_file)

        self.worker_thread.finished.connect(self._cleanup_worker)
        self.worker_thread.start()
        self.request_open_port.emit(port)


    @QtCore.Slot()
    def close_port(self):
        if not self.worker_thread or not self.worker:
            return

        try:
            self.request_close_port.emit()
            self.worker_thread.wait()
        finally:
            self._cleanup_worker()


    @QtCore.Slot(str)
    def send(self, text):
        if not self.worker:
            self.error_occurred.emit("No serial port is open")
            return

        self.request_send_text.emit(text)


    @QtCore.Slot(object, str)
    def process_image_file(self, file_path_or_image, mode):
        if not self.worker:
            self.error_occurred.emit("No serial port is open")
            return

        self.request_process_image.emit(file_path_or_image, mode)


    @QtCore.Slot()
    def _handle_worker_disconnect(self):
        self.disconnected.emit()
        self.close_port()


    @QtCore.Slot()
    def _cleanup_worker(self):
        if self.worker:
            for signal in (
                self.request_open_port,
                self.request_close_port,
                self.request_send_text,
                self.request_process_image,
            ):
                try:
                    signal.disconnect()
                except (TypeError, RuntimeError):
                    pass

        if self.worker_thread:
            self.worker_thread.deleteLater()

        if self.worker:
            self.worker.deleteLater()

        self.worker_thread = None
        self.worker = None