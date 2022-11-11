import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from dock_widgets.control_dock import BaseControlDockWidget, MaskControlDockWidget
from dock_widgets.temperature_dock import TemperatureDockWidget


class MainWindow(QMainWindow):
    _included_widgets = [BaseControlDockWidget, MaskControlDockWidget,
                         TemperatureDockWidget]

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        # Resize to the screen resolution
        self.resize(1280, 720)
        self.setWindowTitle("Main Window")
        font = QFont()
        font.setBold(True)
        self.set_menubar()
        self.set_toolbar()

        # Set the central widget


        # Load the docks
        self.load_docks()

    def set_toolbar(self):
        """Add the toolbar and the options to it."""
        # Add the toolbar
        self.toolBar = QToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.toolBar)
        self.toolBar.addAction("Open")

    def set_menubar(self):
        """Add the menu bar and the options to it."""
        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)
        self._viewMenu = menuBar.addMenu("&View")

    def load_docks(self):
        """Load the dock widgets from the _included_widgets list."""
        # Load the base control dock
        self.baseControlDock = BaseControlDockWidget(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.baseControlDock)
        self._viewMenu.addAction(self.baseControlDock.toggleViewAction())

        # Load the mask control dock
        self.maskControlDock = MaskControlDockWidget(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.maskControlDock)
        self._viewMenu.addAction(self.maskControlDock.toggleViewAction())

        # Load the temperature dock
        self.temperatureDock = TemperatureDockWidget(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.temperatureDock)
        self._viewMenu.addAction(self.temperatureDock.toggleViewAction())
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())