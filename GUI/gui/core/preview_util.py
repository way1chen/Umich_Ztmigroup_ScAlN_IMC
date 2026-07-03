"""
Shared utility for previewing widgets in full-screen mode.

This module provides a reusable preview function for displaying any widget
in a full-screen window, avoiding code duplication across widget modules.
"""

import sys
from PySide6 import QtWidgets, QtCore, QtGui


def preview_widget(widget_class, *args, **kwargs):
    """
    Display a widget class in a full-screen preview window.

    Args:
        widget_class: The widget class to instantiate and display.
        *args: Positional arguments to pass to the widget constructor.
        **kwargs: Keyword arguments to pass to the widget constructor.
    """
    app = QtWidgets.QApplication.instance()
    owns_app = app is None

    if owns_app:
        app = QtWidgets.QApplication(sys.argv)

    widget = widget_class(*args, **kwargs)
    
    # Get the available screen geometry
    screen = app.primaryScreen()
    geometry = screen.availableGeometry()
    
    # Set widget to screen size and show
    widget.setGeometry(geometry)
    widget.show()

    if owns_app:
        sys.exit(app.exec())
