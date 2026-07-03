from enum import Enum


class ProcessingMode(Enum):
    """High-level processing choices shown in the UI.

    This enum is intentionally protocol-agnostic. Widgets work with the enum,
    while `SerialManager` maps it to whatever command string the MCU protocol
    currently expects.
    """

    BLUR_LIGHT = ("Blur - Light", "BLUR_LIGHT")
    BLUR_HEAVY = ("Blur - Heavy", "BLUR_HEAVY")
    SHARPEN = ("Sharpen", "SHARPEN")

    @property
    def display_text(self):
        return self.value[0]

    @property
    def serial_command(self):
        return self.value[1]

    @classmethod
    def from_display_text(cls, text):
        for mode in cls:
            if mode.display_text == text:
                return mode

        raise ValueError(f"Unknown processing mode: {text}")

    def __str__(self):
        return self.display_text