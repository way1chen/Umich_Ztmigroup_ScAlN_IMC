#!/usr/bin/env python3

from pathlib import Path
import re
import sys


TEMPLATE = '''from PySide6 import QtWidgets, QtCore
from gui.widgets.preview_util import preview_widget


class {class_name}(QtWidgets.QWidget):

    error_occurred = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        #Define Child Widgets

        #Define Layout

        #Define Signal-Slot Connections


def preview():
    preview_widget({class_name})


if __name__ == "__main__":
    preview()
'''


def camel_to_snake(name: str) -> str:
    """
    Convert:
        SelectTool -> select_tool
        TCPPortWidget -> tcp_port_widget
    """

    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def main():
    if len(sys.argv) != 2:
        print("Usage: new_widget <ClassName>")
        sys.exit(1)

    class_name = sys.argv[1]

    filename = camel_to_snake(class_name) + ".py"

    path = Path("gui/widgets/" + filename)

    if path.exists():
        print(f"Error: {filename} already exists")
        sys.exit(1)

    content = TEMPLATE.format(class_name=class_name)

    path.write_text(content)

    print(f"Created {filename}")


if __name__ == "__main__":
    main()