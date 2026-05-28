"""Helpers for reading MNIST IDX files into Qt images.

The files in ``gui/archive`` use the standard MNIST IDX binary format:

* images: magic 2051 (0x00000803), followed by count, rows, cols, then raw
  unsigned-byte grayscale pixels
* labels: magic 2049 (0x00000801), followed by count, then one unsigned-byte
  label per image

This module parses that format and converts image records into ``QImage``
objects using ``Format_Grayscale8``. Loaded images are downscaled to 20x20 so
they match the image-processing protocol used elsewhere in the app.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PySide6 import QtCore, QtGui


MNIST_IMAGE_MAGIC = 2051
MNIST_LABEL_MAGIC = 2049
MNIST_IMAGE_HEADER_BYTES = 16
MNIST_LABEL_HEADER_BYTES = 8
MNIST_TARGET_SIZE = 20


@dataclass(frozen=True)
class MnistSample:
    """One MNIST sample with its decoded image and optional label."""

    image: QtGui.QImage
    label: int | None = None
    index: int | None = None


def _resolve_idx_path(path: str | Path) -> Path:
    """Resolve a path that may point at either a file or an extracted directory."""
    resolved = Path(path)

    # The archive contains both direct IDX files and folders that contain a
    # single extracted copy of the same file, so support both layouts.
    if resolved.is_file():
        return resolved

    if resolved.is_dir():
        direct_child = resolved / resolved.name
        if direct_child.is_file():
            return direct_child

        children = [child for child in resolved.iterdir() if child.is_file()]
        if len(children) == 1:
            return children[0]

    raise FileNotFoundError(f"Could not locate MNIST IDX file at {resolved}")


def _read_u32_be(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def _parse_image_header(data: bytes) -> tuple[int, int, int]:
    # IDX headers are big-endian. The image file stores:
    #   magic, image_count, row_count, column_count
    if len(data) < MNIST_IMAGE_HEADER_BYTES:
        raise ValueError("MNIST image file is too small to contain a valid header")

    magic = _read_u32_be(data, 0)
    if magic != MNIST_IMAGE_MAGIC:
        raise ValueError(f"Expected MNIST image magic {MNIST_IMAGE_MAGIC}, got {magic}")

    count = _read_u32_be(data, 4)
    rows = _read_u32_be(data, 8)
    cols = _read_u32_be(data, 12)
    return count, rows, cols


def _parse_label_header(data: bytes) -> int:
    # IDX label files store:
    #   magic, label_count
    if len(data) < MNIST_LABEL_HEADER_BYTES:
        raise ValueError("MNIST label file is too small to contain a valid header")

    magic = _read_u32_be(data, 0)
    if magic != MNIST_LABEL_MAGIC:
        raise ValueError(f"Expected MNIST label magic {MNIST_LABEL_MAGIC}, got {magic}")

    return _read_u32_be(data, 4)


def _image_from_pixels(pixels: bytes, rows: int, cols: int) -> QtGui.QImage:
    # The pixel payload is already grayscale, so we can wrap it directly in a
    # QImage and then copy it to detach from the original byte buffer.
    if len(pixels) != rows * cols:
        raise ValueError(
            f"Expected {rows * cols} pixels for a {rows}x{cols} image, got {len(pixels)}"
        )

    image = QtGui.QImage(pixels, cols, rows, cols, QtGui.QImage.Format.Format_Grayscale8)
    return image.copy()


def _downscale_image(image: QtGui.QImage, size: int = MNIST_TARGET_SIZE) -> QtGui.QImage:
    """Resize an image to a square grayscale thumbnail used by the protocol."""
    if image.isNull():
        raise ValueError("Cannot downscale a null MNIST image")

    # Most MNIST images are 28x28, but the app uses 20x20 for the image
    # processing protocol, so preserve that shape here.
    if image.width() == size and image.height() == size:
        return image.copy()

    return image.scaled(
        size,
        size,
        QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
        QtCore.Qt.TransformationMode.SmoothTransformation,
    )


def load_mnist_images(
    path: str | Path,
    limit: int | None = None,
    start: int = 0,
    target_size: int = MNIST_TARGET_SIZE,
) -> list[QtGui.QImage]:
    """Load MNIST images from an IDX file into resized ``QImage`` objects.

    Args:
        path: Path to the image IDX file or extracted directory.
        limit: Maximum number of images to load.
        start: Zero-based image index to start from.
        target_size: Final square size for each returned image.
    """
    idx_path = _resolve_idx_path(path)
    data = idx_path.read_bytes()
    count, rows, cols = _parse_image_header(data)

    image_size = rows * cols
    payload = data[MNIST_IMAGE_HEADER_BYTES:]
    expected_size = count * image_size
    if len(payload) < expected_size:
        raise ValueError(
            f"MNIST image payload is truncated: expected {expected_size} bytes, got {len(payload)}"
        )

    start_index = max(start, 0)
    end_index = count if limit is None else min(count, start_index + max(limit, 0))

    images: list[QtGui.QImage] = []
    for index in range(start_index, end_index):
        # Each image is stored as a contiguous rows*cols byte block.
        offset = index * image_size
        pixels = payload[offset: offset + image_size]
        image = _image_from_pixels(pixels, rows, cols)
        images.append(_downscale_image(image, target_size))

    return images


def load_mnist_labels(path: str | Path, limit: int | None = None, start: int = 0) -> list[int]:
    """Load MNIST labels from an IDX file into a list of integers."""
    idx_path = _resolve_idx_path(path)
    data = idx_path.read_bytes()
    count = _parse_label_header(data)

    payload = data[MNIST_LABEL_HEADER_BYTES:]
    if len(payload) < count:
        raise ValueError(
            f"MNIST label payload is truncated: expected {count} bytes, got {len(payload)}"
        )

    start_index = max(start, 0)
    end_index = count if limit is None else min(count, start_index + max(limit, 0))
    return list(payload[start_index:end_index])


def load_mnist_samples(
    image_path: str | Path,
    label_path: str | Path | None = None,
    limit: int | None = None,
    start: int = 0,
    target_size: int = MNIST_TARGET_SIZE,
) -> list[MnistSample]:
    """Load paired MNIST image/label samples from IDX files.

    If no label file is provided, the returned samples still contain images but
    their ``label`` field is set to ``None``.
    """
    images = load_mnist_images(image_path, limit=limit, start=start, target_size=target_size)

    labels: Sequence[int | None]
    if label_path is None:
        # Keep the image list usable even when the caller only has images.
        labels = [None] * len(images)
    else:
        labels = load_mnist_labels(label_path, limit=len(images), start=start)

    samples: list[MnistSample] = []
    for offset, image in enumerate(images):
        # Pair the image with its label when available and keep the original
        # dataset index so callers can trace the sample back to the archive.
        label = labels[offset] if offset < len(labels) else None
        samples.append(MnistSample(image=image, label=label, index=start + offset))

    return samples


def load_mnist_image(path: str | Path, index: int = 0) -> QtGui.QImage:
    """Load a single MNIST image by index."""
    images = load_mnist_images(path, limit=index + 1, start=index)
    if not images:
        raise IndexError(f"No MNIST image found at index {index}")
    return images[0]
