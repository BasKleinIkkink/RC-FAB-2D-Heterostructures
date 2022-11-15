import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

try:
    from .dock_widgets.control_dock import BaseControlDockWidget, MaskControlDockWidget
    from .dock_widgets.temperature_dock import TemperatureDockWidget
    from basicsortfiltermodel import Message, SystemMessageWidget
except ImportError:
    from dock_widgets.control_dock import BaseControlDockWidget, MaskControlDockWidget
    from dock_widgets.temperature_dock import TemperatureDockWidget
    from basicsortfiltermodel import Message, SystemMessageWidget
    from dock_widgets.focus_dock import FocusDockWidget
    from settings import Settings


class MainWindow(QMainWindow):
    _included_widgets = [BaseControlDockWidget, MaskControlDockWidget,
                         TemperatureDockWidget, FocusDockWidget]

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
        self.set_central_widget()  # Set the central widget
        self.load_docks()  # Load the docks

    def set_central_widget(self):
        # Place the system messages widget on the right side of the main window
        self.systemMessagesWidget = SystemMessageWidget(self)
        self.message_frame = QFrame(self)
        self.message_frame.setFixedSize(500, 840)
        layout = QVBoxLayout(self.message_frame)
        layout.addWidget(self.systemMessagesWidget)
        self.setCentralWidget(self.message_frame)

    def closeEvent(self, event):
        """Close the main window."""
        self.close()

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

        # Add the action to hide the message groupbox
        self._viewMenu.addAction("System Messages")
        self._viewMenu.triggered.connect(self.hide_messages)

    def hide_messages(self, action):
        """Hide the messages groupbox."""
        # Check if the box is visible
        if self.systemMessagesWidget.isVisible():
            self.systemMessagesWidget.hide()
        else:
            self.systemMessagesWidget.show()
    

    def load_docks(self):
        """Load the dock widgets from the _included_widgets list."""
        # Load the base control dock
        self.baseControlDock = BaseControlDockWidget(Settings(), self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.baseControlDock)
        self._viewMenu.addAction(self.baseControlDock.toggleViewAction())

        # Load the mask control dock
        self.maskControlDock = MaskControlDockWidget(Settings(), self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.maskControlDock)
        self._viewMenu.addAction(self.maskControlDock.toggleViewAction())

        # Load the focus dock
        self.focusDock = FocusDockWidget(Settings(), self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.focusDock)
        self._viewMenu.addAction(self.focusDock.toggleViewAction())

        # Load the temperature dock
        self.temperatureDock = TemperatureDockWidget(Settings(), self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.temperatureDock)
        self._viewMenu.addAction(self.temperatureDock.toggleViewAction())

def main():
    """"Start the GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()