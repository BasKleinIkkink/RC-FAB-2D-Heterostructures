import sys
import time
import threading
import queue
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (QMainWindow, QToolBar, QFrame, QMenuBar,
                            QVBoxLayout, QHBoxLayout, QDockWidget,
                            QApplication)
from .widgets.system_messages_widget import SystemMessageWidget
from .widgets.control_widget import BaseControlWidget, MaskControlWidget
from .widgets.focus_widget import FocusWidget
from .widgets.temperature_widget import TemperatureWidget
from .settings import Settings
from ...stacking_middleware.message import Message


class MainWindow(QMainWindow):
    window_size = (1280, 720)

    def __init__(self, connector):
        """Initialize the main window."""
        super().__init__()
        # Connect to the backend
        self._connector = connector
        self._q = queue.Queue()
        self._shutdown_event = threading.Event()
        # self._start_event_handeler()

        # Resize to the screen resolution
        self.resize(self.window_size[0], self.window_size[1])
        self.setWindowTitle("Main Window")

        # Set the menu and toolbar
        self.set_menubar()
        self.set_toolbar()

        # Load and set the widgets
        self.load_widgets()  # Load the docks
        self.connect_actions()

    def closeEvent(self, event):
        """Close the main window."""
        self._stop_event_handeler()
        self._connector.send_sentinel()
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
        self.baseControlWidget = BaseControlWidget(Settings(), self._q, self)
        self.baseControlWidget.connect_actions(self._viewMenu, self.toolBar)
        self.maskControlWidget = MaskControlWidget(Settings(), self._q, self)
        self.maskControlWidget.connect_actions(self._viewMenu, self.toolBar)
        #self.maskControlWidget.connect_actions(self._viewMenu, self.toolBar)
        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(self.maskControlWidget)
        verticalLayout.addWidget(self.baseControlWidget)
        verticalLayout.setAlignment(Qt.AlignTop)
        self.centralHorizontalLayout.addLayout(verticalLayout)

        # Load the focus and temperature widgets
        self.microscopeWidget = FocusWidget(Settings(), self._q, self)
        self.microscopeWidget.connect_actions(self._viewMenu, self.toolBar)
        self.temperatureWidget = TemperatureWidget(Settings(), self._q, self)
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
    def _start_event_handeler(self):
        """Start the event handeler."""
        # Handshake with the frondend
        time.sleep(1)
        self._connector.handshake()

        # Strart the handler
        self._connector.send('G91')  # Set absolute positioning
        self.event_handle_thread = threading.Thread(target=self._event_handeler, args=(self._q, self._shutdown_event))
        self.event_handle_thread.setDaemon(True)
        self.event_handle_thread.start()

    def _stop_event_handeler(self):
        """Stop the event handeler."""
        self._shutdown_event.set()

    def _event_handeler(self, q, shutdown_event):
        """Thread that responds to messages from the backend."""
        while not shutdown_event.is_set():
            # Check if the connector has a message waiting
            if self._connector.message_waiting():
                msg = self._connector.receive()
                self._update_gui(msg)
                
            else:
                # Check if the gui send a message and pass it too the backend
                if not q.empty():
                    msg = q.get()
                    self._connector.send(msg)
            
            time.sleep(0.01)  # Yield the processor

    def _update_gui(self, messages : list):
        """Get the content from the message and pass it to the correct widget."""
        for i in messages:
            self.systemMessagesWidget.add_message(i)
            if i.command_id == 'G28':
                # Set all the axis with a homing function to 0
                pass
            print(i.__dict__)


def main(connector=None):
    """"Start the GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow(connector)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()