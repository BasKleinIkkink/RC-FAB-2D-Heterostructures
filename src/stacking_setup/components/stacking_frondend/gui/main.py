import sys
import time
import threading
import queue
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QFrame,
    QMenuBar,
    QVBoxLayout,
    QHBoxLayout,
    QDockWidget,
    QApplication,
)
from .widgets.system_messages_widget import SystemMessageWidget
from .widgets.control_widget import BaseControlWidget, MaskControlWidget
from .widgets.focus_widget import FocusWidget
from .widgets.temperature_widget import TemperatureWidget
from .configs.settings import Settings
import multiprocessing as mp


VERBOSE_OUTPUT = True


class MainWindow(QMainWindow):
    window_size = (1280, 720)

    def __init__(self, connector):
        """Initialize the main window."""
        super().__init__()
        # Connect to the backend
        self._connector = connector
        self._connector.__init_lock__()
        self._q = queue.Queue()
        self._shutdown_event = mp.Event()
        self._settings = Settings()

        # Resize to the screen resolution
        self.setWindowTitle("Main Window")

        # Set the menu and toolbar
        self.set_menubar()
        self.set_toolbar()

        # Load and set the widgets
        self.load_widgets()  # Load the docks
        self.connect_actions()

        self._connect_backend()

    def _connect_backend(self):
        # Handshake with the frondend
        time.sleep(0.5)
        self._connector.handshake()
        self._start_event_handeler()
        self._q.put("M154 S{}".format(self._settings.pos_auto_update_interval))
        self._q.put("M155 S{}".format(self._settings.temp_auto_update_interval))

    def closeEvent(self, event):
        """Close the main window."""
        self._stop_event_handeler()
        # self._q.join()
        self._connector.send_sentinel()
        self.close()

    def set_toolbar(self):
        """Add the toolbar and the options to it."""
        # Add the toolbar
        self.toolBar = QToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.toolBar)
        self.toolBar.addAction("Home all", self._home_all)
        self.toolBar.addAction("Stop", self._trigger_stop)
        self.toolBar.addSeparator()
        self.toolBar.addAction("E-stop", self._trigger_estop)

    def _home_all(self):
        """Home all the axes."""
        self._q.put("G28")

    def _trigger_estop(self):
        """Trigger the emergency stop."""
        if VERBOSE_OUTPUT:
            print("Triggered estop!")
        self._q.put("M112")

        # If the flag is set disable all the widget buttons
        self.baseControlWidget.estop()
        self.maskControlWidget.estop()
        self.microscopeWidget.estop()
        self.temperatureWidget.estop()

    def _reset_estop(self):
        if VERBOSE_OUTPUT:
            print("Reset the estop")
        self._q.put("M999")
        self._shutdown_event.M999()

        # If the flag is set disable all the widget buttons
        self.baseControlWidget.estop(True)
        self.maskControlWidget.estop(True)
        self.microscopeWidget.estop(True)
        self.temperatureWidget.estop(True)

    def _trigger_stop(self):
        if VERBOSE_OUTPUT:
            print("Triggered the stop")
        self._q.put("M813")

    def _lock_unlock_machine(self):
        # Get the button state
        state = not self._optionsMenu.actions()[0].isChecked()

        if VERBOSE_OUTPUT:
            print("Set machine lock to {}".format(state))

        # If the flag is set disable all the widget buttons
        self.baseControlWidget.estop(state)
        self.maskControlWidget.estop(state)
        self.microscopeWidget.estop(state)
        self.temperatureWidget.estop(state)

    def set_menubar(self):
        """Add the menu bar and the options to it."""
        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)
        self._viewMenu = menuBar.addMenu("&View")
        self._optionsMenu = menuBar.addMenu("&Options")
        self._optionsMenu.addAction("Lock/Unlock system", self._lock_unlock_machine)
        self._optionsMenu.actions()[-1].setCheckable(True)
        self._optionsMenu.actions()[-1].setChecked(False)
        self._optionsMenu.addAction("Reset e-stop", self._reset_estop)

    def load_widgets(self):
        """Load the dock widgets from the _included_widgets list."""
        # Create the central frame and layout
        self.centralFrame = QFrame(self)
        self.centralHorizontalLayout = QHBoxLayout(self.centralFrame)
        self.setCentralWidget(self.centralFrame)

        # Load the main control widgets
        self.baseControlWidget = BaseControlWidget(self._settings, self._q, self)
        self.baseControlWidget.connect_actions(self._viewMenu, self.toolBar)
        self.maskControlWidget = MaskControlWidget(self._settings, self._q, self)
        self.maskControlWidget.connect_actions(self._viewMenu, self.toolBar)
        # self.maskControlWidget.connect_actions(self._viewMenu, self.toolBar)
        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(self.maskControlWidget)
        verticalLayout.addWidget(self.baseControlWidget)
        verticalLayout.setAlignment(Qt.AlignTop)
        self.centralHorizontalLayout.addLayout(verticalLayout)

        # Load the focus and temperature widgets
        self.microscopeWidget = FocusWidget(self._settings, self._q, self)
        self.microscopeWidget.connect_actions(self._viewMenu, self.toolBar)
        self.temperatureWidget = TemperatureWidget(self._settings, self._q, self)
        self.temperatureWidget.connect_actions(self._viewMenu, self.toolBar)
        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(self.microscopeWidget)
        verticalLayout.addWidget(self.temperatureWidget)
        verticalLayout.setAlignment(Qt.AlignTop)
        self.centralHorizontalLayout.addLayout(verticalLayout)

        # Load the message dock
        self.systemMessagesWidget = SystemMessageWidget(self._settings, self)
        self.centralHorizontalLayout.addWidget(self.systemMessagesWidget)
        self.centralHorizontalLayout.setAlignment(Qt.AlignTop)

    def connect_actions(self):
        """Connect the actions to the widgets."""
        # Add hide options in te vieuw menu for all the widgets
        self._viewMenu.addAction(
            "Base control", lambda: self._toggle_visibility(self.baseControlWidget)
        )
        self._viewMenu.addAction(
            "Mask control", lambda: self._toggle_visibility(self.maskControlWidget)
        )
        self._viewMenu.addAction(
            "Focus", lambda: self._toggle_visibility(self.microscopeWidget)
        )
        self._viewMenu.addAction(
            "Temperature", lambda: self._toggle_visibility(self.temperatureWidget)
        )
        self._viewMenu.addAction(
            "System messages",
            lambda: self._toggle_visibility(self.systemMessagesWidget),
        )
        self.systemMessagesWidget.setVisible(False)

        # Make the menu actions checkable
        for action in self._viewMenu.actions():
            action.setCheckable(True)
            action.setChecked(True)

        # Except for the messaging widget
        self._viewMenu.actions()[-1].setChecked(False)

    def _toggle_visibility(self, widget):
        """Toggle the visibility of the widget."""
        if widget.isVisible():
            widget.hide()
        else:
            widget.show()

    # Communication with the backend
    def _start_event_handeler(self):
        """Start the event handeler."""
        if VERBOSE_OUTPUT:
            print("Starting the event handeler")
        # Strart the handler
        self._connector.send("G91")  # Set relative positioning
        self.event_handle_thread = threading.Thread(
            target=self._event_handeler, args=(self._q, self._shutdown_event)
        )
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

    def _update_gui(self, messages: list):
        """Get the content from the message and pass it to the correct widget."""
        for i in messages:
            self.systemMessagesWidget.add_message(i)
            if i.command_id == "M112":
                # Emergency stop was triggered
                self.toolBar.actions()[1].setChecked(True)

            elif i.command_id == "M154":
                # Set all the positions to the correct values
                try:
                    positions = dict(i.msg)
                except ValueError:
                    continue
                self.maskControlWidget.update_positions(positions)
                self.baseControlWidget.update_positions(positions)
                self.microscopeWidget.update_positions(positions)
            elif i.command_id == "M155":
                # Set the temperature to the correct value
                try:
                    temp = dict(i.msg)
                except ValueError:
                    continue
                self.temperatureWidget.update_temperature(temp=temp)


def main(connector=None):
    """ "Start the GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow(connector)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
