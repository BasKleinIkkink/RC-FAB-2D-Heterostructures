import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from dock_widgets.control_dock import BaseControlDockWidget, MaskControlDockWidget


class MainWindow(QMainWindow):
    _included_widgets = [BaseControlDockWidget, MaskControlDockWidget]

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        # Resize to the screen resolution
        self.resize(1920, 1080)
        self.setWindowTitle("Main Window")
        font = QFont()
        font.setBold(True)

        # Load the docks
        self.load_docks()

    def load_docks(self):
        """Load the dock widgets from the _included_widgets list."""
        # Load the docks
        for widget in self._included_widgets:
            self.addDockWidget(Qt.RightDockWidgetArea, widget(self))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())