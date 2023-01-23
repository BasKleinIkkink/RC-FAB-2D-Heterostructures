from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Slot
from threading import Event


class PushButton(QPushButton):

    def __init__(self, icon=None, parent=None) -> None:
        super().__init__(icon, parent)

        # Connect the push and release actions
        self.pressed.connect(self._on_push)
        self.released.connect(self._on_release)

        # Create the event
        self._pushed = Event()
        self._released = Event()
        self._released.set()

    @property
    def is_pushed(self) -> bool:
        return self._pushed.is_set()

    @property
    def is_released(self) -> bool:
        return self._released.is_set()

    @Slot()
    def _on_push(self) -> None:
        self._pushed.set()
        self._released.clear()
        print("Pushed")

    @Slot()
    def _on_release(self) -> None:
        self._pushed.clear()
        self._released.set()
        print("Released")

    