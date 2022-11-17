import sys
import time
import threading
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (QMainWindow, QToolBar, QFrame, QMenuBar,
                            QVBoxLayout, QHBoxLayout, QDockWidget,
                            QApplication)
from .basicsortfiltermodel import SystemMessageWidget
from .control_widget import BaseControlWidget, MaskControlWidget
from .focus_widget import FocusWidget
from .temperature_widget import TemperatureWidget
from .settings import Settings


class MainWindow(QMainWindow):
    window_size = (1280, 720)

    def __init__(self, connector):
        """Initialize the main window."""
        super().__init__()
        # Resize to the screen resolution
        self.resize(self.window_size[0], self.window_size[1])
        self.setWindowTitle("Main Window")

        # Set the menu and toolbar
        self.set_menubar()
        self.set_toolbar()

        # Load and set the widgets
        self.load_widgets()  # Load the docks
        self.connect_actions()

        # Connect to the backend
        self._connector = connector
        self.shutdown_event = threading.Event()

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
    
    def load_widgets(self):
        """Load the dock widgets from the _included_widgets list."""
        # Create the central frame and layout
        self.centralFrame = QFrame(self)
        self.centralHorizontalLayout = QHBoxLayout(self.centralFrame)
        self.setCentralWidget(self.centralFrame)

        # Load the main control widgets
        self.baseControlWidget = BaseControlWidget(Settings(), self)
        self.baseControlWidget.connect_actions(self._viewMenu, self.toolBar)
        self.maskControlWidget = MaskControlWidget(Settings(), self)
        self.maskControlWidget.connect_actions(self._viewMenu, self.toolBar)
        #self.maskControlWidget.connect_actions(self._viewMenu, self.toolBar)
        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(self.maskControlWidget)
        verticalLayout.addWidget(self.baseControlWidget)
        verticalLayout.setAlignment(Qt.AlignTop)
        self.centralHorizontalLayout.addLayout(verticalLayout)

        # Load the focus and temperature widgets
        self.microscopeWidget = FocusWidget(Settings(), self)
        self.microscopeWidget.connect_actions(self._viewMenu, self.toolBar)
        self.temperatureWidget = TemperatureWidget(Settings(), self)
        self.temperatureWidget.connect_actions(self._viewMenu, self.toolBar)
        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(self.microscopeWidget)
        verticalLayout.addWidget(self.temperatureWidget)
        verticalLayout.setAlignment(Qt.AlignTop)
        self.centralHorizontalLayout.addLayout(verticalLayout)
        
        # Load the message dock
        self.systemMessagesWidget = SystemMessageWidget(Settings(), self)
        self.centralHorizontalLayout.addWidget(self.systemMessagesWidget)
        self.centralHorizontalLayout.setAlignment(Qt.AlignTop)

    def connect_actions(self):
        """Connect the actions to the widgets."""
        # Add hide options in te vieuw menu for all the widgets
        self._viewMenu.addAction("Base control", 
                lambda : self._toggle_visibility(self.baseControlWidget))
        self._viewMenu.addAction("Mask control", 
                lambda : self._toggle_visibility(self.maskControlWidget))
        self._viewMenu.addAction("Focus", 
                lambda : self._toggle_visibility(self.microscopeWidget))
        self._viewMenu.addAction("Temperature", 
                lambda : self._toggle_visibility(self.temperatureWidget))
        self._viewMenu.addAction("System messages", 
                lambda : self._toggle_visibility(self.systemMessagesWidget))

        # Make the menu actions checkable
        for action in self._viewMenu.actions():
            action.setCheckable(True)
            action.setChecked(True)

    def _toggle_visibility(self, widget):
        """Toggle the visibility of the widget."""
        if widget.isVisible():
            widget.hide()
        else:
            widget.show()

    # Communication with the backend
    def start_event_handeler(self):
        """Start the event handeler."""
        self.event_handle_thread = threading.Thread(target=self._event_handeler)
        self.event_handle_thread.setDaemon(True)
        self.event_handle_thread.start()

    def stop_event_handeler(self):
        """Stop the event handeler."""
        self.shutdown_event.set()

    def _event_handeler(self):
        """Thread that responds to messages from the backend."""
        while not self.shutdown_event.is_set():
            # Check if the connector has a message waiting
            if self.connector.in_waiting():
                msg = self.connector.receive()

                # Emit the right signal
                
            else:
                pass
            
            time.sleep(0.01)  # Yield the processor


def main(connector=None):
    """"Start the GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow(connector)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()