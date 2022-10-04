import serial
import threading as tr
import time as t


class EmergencyBreaker(object):
    """
    Class to control the emergency breaker.
    
    The emergency breaker is a connected Arduino like microprocessor that is connected
    a set of relays, who are in turn connected to the power sources of all the hardware
    connected to the stacking setup.
    
    The breaker has two main functions:
        Hardware emergency breaker: 
        This is a big red button directly connected to the
        microcontroller. When the button is pushed all the relays will switch off and disconnect
        the powersources. The controller will then send a flag to the connected computer 
        indicating that the emergency button has been pressed.

        Software emergency breaker:
        The software emergency breaker is connected to the emergency_stop_event flag that
        is distributed to all connected controll classes by the central class (stacking setup)
        every class has the power to set this flag. Once the flag is an intterupt function will
        trigger that sends the connected microcontroller the emergency break signal, in turn the
        microcontroller will disconnect the power sources. The power sources will likely be disconnected
        before the software stops because the hardware classes only check the emergency flagg after (and 
        before) every action.
        """

    def __init__(self, com_port, baud_rate, timeout, emergency_stop_event):
        self._com_port = com_port
        self._baud_rate = baud_rate
        self._timeout = timeout
        self._emergency_stop_event
        self._power_state = self.get_power_state()

        # Pre encoded strings
        self._shutdown_string = 'shutdown'.encode()  # String to send to the microcontroller to trigger the emergency breaker.
        self._button_state_string = 'button_state'.encode()  # String to send to the microcontroller to get the status of the emergency button.
        self._switch_on_string = 'switch_on'.encode()  # String to send to the microcontroller to switch the relays on.
        self._switch_off_string = 'switch_off'.encode()  # String to send to the microcontroller to switch the relays off.
        self._power_state_string = 'power_state'.encode()  # String to send to the microcontroller to get the power state of the relays.

    def interrupt(self):
        """Function that will be triggered on reveiving the emergency flag."""
        self._emergency_stop_event.set()

    def trigger_breaker(self):
        """Trigger the emergency breaker."""
        self._serial.write(self._shutdown_string)
        self.interrupt()

    def is_pressed(self):
        """Get the status of the emergency button."""
        raise NotImplementedError()

    def get_power_state(self):
        """Get the power state of the emergency breaker."""
        self._serial.write(self._power_state_string)
        state = None
        etime = t.ticks_add(t.ticks_us(), self._timeout * 1e3)
        while t.ticks_diff(etime, t.ticks_us()) > 0:
            if self._serial.in_waiting > 0:
                state = self._serial.readline()

        if state is None:
            raise TimeoutError('Timeout while waiting for power state.')
        
        # Parse the state from the string.
        if state == 'on':
            return True
        elif state == 'off':
            return False

    def switch_relays(self, force_on=False, force_off=False):
        """Switch the relays on or off."""
        if self.is_pressed() or (force_on and force_off):
            return False
        if force_on:
            self._serial.write(self._switch_on_string)
        elif force_off:
            self._serial.write(self._switch_off_string)

        self._power_state = not self._power_state
        if self._power_state:
            self._serial.write(self._switch_on_string)
        else:
            self._serial.write(self._switch_off_string)

    def _handshake(self):
        """Handshake with the microcontroller."""
        raise NotImplementedError()


if __name__ == '__main__':
    # Test the emergency breaker class.
    import time
    import threading as tr
    import multiprocessing as mp

    # Create the emergency stop event.
    emergency_stop_event = mp.Event()

    # Create the emergency breaker.
    breaker = EmergencyBreaker('COM3', 9600, 1, emergency_stop_event)

    # Trigger the breaker.
    breaker.trigger_breaker()

    # Wait for the emergency stop event to be set.
    while not emergency_stop_event.is_set():
        time.sleep(0.1)

    print('Emergency stop event has been set.')