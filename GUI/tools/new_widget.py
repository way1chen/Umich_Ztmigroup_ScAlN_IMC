#!/usr/bin/env python3

from pathlib import Path
import re
import sys


TEMPLATE = '''from PySide6 import QtWidgets, QtCore
import sys


class {class_name}(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


def preview():
    app = QtWidgets.QApplication.instance()

    owns_app = app is None

    if owns_app:
        app = QtWidgets.QApplication(sys.argv)

    widget = {class_name}()
    widget.resize(400, 400)
    widget.show()

    if owns_app:
        sys.exit(app.exec())


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

    path = Path("widgets/" + filename)

    if path.exists():
        print(f"Error: {filename} already exists")
        sys.exit(1)

    content = TEMPLATE.format(class_name=class_name)

    path.write_text(content)

    print(f"Created {filename}")


if __name__ == "__main__":
    main()