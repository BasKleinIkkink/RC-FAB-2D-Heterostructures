from base import Base
import serial
from exceptions import HardwareNotConnectedError, NotSupportedError
from typing import Union
from typeguard import typechecked


class TangoDesktop(Base):
    """
    Class for TangoDesktop hardware.

    IMPORTANT: This class is

    Communication interface:
    ------------------------
    All TANGO controllers communicate via a serial COM port interface, independent
    of the controller type (RS232C, USB, PCI, PCI-E). The default setting is
    57600,8,2,N.

    Instruction syntax:
    -------------------
    The instructions and parameters are sent as cleartext ASCII strings with a
    terminating carriage return [CR], which is 0x0d hex. Characters may be upper-,
    lower- or camel-case. The parameters are separated by a space character.
    This provides easy access to all functions by using a simple terminal program
    such as HyperTerminal. A typical instruction syntax is as follows: 

    [!,?][instruction][SP][optional axis] [parameter1][SP][parameter2] [etc…] [CR]

    A read instruction may return more than one parameter. In many cases the number
    of returned parameters depends on the amount of available axes:

    [axis X] [if available: axis Y] [if available: axis Z] [if available: axis A]

    """
    _id = None
    _type = "TANGO DESKTOP"
    _controller = None
    _baud_rate = 9600
    _timeout = 0.2
    _serial_nr = '220313104'
    _ser = None
    _port = 'COM6'

    def __init__(self) -> None:
        """Initialize the tango desktop."""	
        # Check if the tango desktop is connected
        if self._controller is None:
            # Controller is not initiated, check if the port can be captured
            try:
                ser = serial.Serial(self._port, self._baud_rate, timeout=self._timeout)
                ser.write('?readsn \r'.encode())
                resp = ser.readline().decode().strip()

                # Check the serial nr
                if resp != self._serial_nr:
                    ser.close()
                    raise HardwareNotConnectedError("The tango desktop that is connected does not match the saved serial nr {}.".format(self._serial_nr))
                else:
                    ser.close()

            except [serial.SerialException, ConnectionRefusedError] as e:
                raise HardwareNotConnectedError("Could not connect to port: {}: e {}".format(self._port, e))

    # ATTRIBUTES
    @property
    @typechecked
    def steps_per_um(self) -> float:
        """Get the steps per um."""
        steps_per_rev = float(self._send_and_receive('?motorsteps z', expect_response=True, expect_confirmation=False))
        spindle_pitch = float(self._send_and_receive('?pitch z', expect_response=True, expect_confirmation=False))
        return round(steps_per_rev / spindle_pitch, 3)

    @property
    @typechecked
    def position(self) -> float:
        """Get the current position."""
        return float(self._send_and_receive('?pos z', expect_response=True, expect_confirmation=False))

    @property
    @typechecked
    def speed(self) -> float:
        """Get the current speed."""
        spindle_pitch = float(self._send_and_receive('?pitch z', expect_response=True, expect_confirmation=False))
        rev_per_s = float(self._send_and_receive('?vel z', expect_response=True, expect_confirmation=False))
        return round(rev_per_s / spindle_pitch, 3)

    @speed.setter
    @typechecked
    def speed(self, speed : Union[float, int]) -> None:
        """Set the speed of the tango desktop."""
        # Calculate the needed revolutions per second
        spindle_pitch = float(self._send_and_receive('?pitch z', expect_response=True, expect_confirmation=False))
        rev_per_s = round(speed / spindle_pitch, 3)
        self._send_and_receive('!vel z {}'.format(rev_per_s), expect_confirmation=False, expect_response=False)

    @property
    @typechecked
    def acceleration(self) -> float:
        """Get the acceleration of the tango desktop."""
        acc = float(self._send_and_receive('?accel z', expect_response=True, expect_confirmation=False))
        acc *= 10e6
        return acc

    @acceleration.setter
    @typechecked
    def acceleration(self, acceleration : Union[float, int]) -> None:
        """Set the acceleration of the tango desktop."""
        # The acceleration is given in mm/s^2
        # The tango desktop needs the acceleration in um/s^2
        acc = round(acceleration / 10e-6, 3)
        self._send_and_receive('!accel z {}'.format(acc), expect_confirmation=False, expect_response=False)

    # CONNECTION FUNCTIONS
    @typechecked
    def _send_and_receive(self, command : str, expect_confirmation : bool=True, expect_response : bool=False) -> Union[None, str]:
        """
        Send a command to the tango desktop and receive the response.
        
        Parameters:
        -----------
        command: str
            The command to send to the tango desktop.
        expect_confirmation: bool
            If the command should expect a confirmation.
        expect_response: bool
            If the command should expect a response.

        Raises:
        -------
        HardwareNotConnectedError: 
            If the tango desktop is not connected.
        ValueError:
            If the command caused an error

        Returns:
        --------
        response: str or None
            The response of the tango desktop.
        """
        if self._ser is None:
            raise HardwareNotConnectedError("The tango desktop is not connected.")

        # Check if the command has a carriage return
        if command[-2:] != '\r':
            command += ' \r'
        self._ser.write(command.encode())  # Send the command
        
        while True:
            # Check if a confirmation is expected
            if expect_confirmation and not expect_response:
                resp = self._ser.readline().decode().strip()  # Read the command confirmation
                if resp == '@': continue
                if resp == 'OK...': break
                else: raise ValueError("The command {} was not accepted by the tango desktop and gave response: {}.".format(command, resp))
            elif expect_response:
                data_resp = self._ser.readline().decode().strip()
                if data_resp == '@': continue
                else: break
            

        if not expect_confirmation:
            # Ask the tango if there are any errors
            self._ser.write('?err \r'.encode())

            while True:
                resp = self._ser.readline().decode().strip()
                if resp == '@': continue
                elif resp != '0':
                    raise ValueError("The command {} gave an error: {}.".format(command, resp))
                else: break
        
            if expect_response: return data_resp  
            else: return None

    @typechecked
    def connect(self) -> None:
        """Connect to the tango desktop."""
        if self._ser is None:
            # Connect the tango desktop
            self._ser = serial.Serial(self._port, self._baud_rate, timeout=self._timeout)

            # Check if the right dim and ext modes are set
            resp = self._send_and_receive('?dim', expect_response=True, expect_confirmation=False)
            if resp != '1 1 1':
                # Set the dimentions to um
                self._send_and_receive('!dim 1 1 1', expect_confirmation=False, expect_response=False)

            resp = self._send_and_receive('?extmode', expect_response=True, expect_confirmation=False)
            if resp != '1':
                self._send_and_receive('!extmode 1', expect_response=False, expect_confirmation=False)

    @typechecked
    def disconnect(self) -> None:
        """Disconnect from the tango desktop."""
        if self._ser is None:
            pass
        else:
            # Make sure nothing is moving
            while self.is_moving():
                pass

            self._ser.close()  # Disconnect the tango desktop

    # STATUS FUNCTIONS
    @typechecked
    def is_connected(self) -> bool:
        """Check if the tango desktop is connected."""
        return True if self._ser is not None else False

    @typechecked
    def is_moving(self) -> bool:
        """
        Check the status of the axis.
        
        Possible return states:
        -----------------------
        @: Axis is not moving and ready
        M: Axis is moving
        J: Axis is ready and can also be manually controlled (joystick)
        S: A limit switch is reached and prevents further movement
        A: Oke response after a cal instruction
        D: Oke response after a rm instruction
        E: Error response, move aborted or not executed
        T: Timeout occured
        -: Axis is not enabled or available in the hardware

        Raises:
        -------
        ValueError: 
            If the axis responds with E, T or -.

        Returns:
        --------
        bool:
            True if the axis is moving, False if not.

        """
        resp = self._send_and_receive('sa z', expect_response=True, expect_confirmation=False)
        if resp in ['E', '-', 'T']: raise ValueError("The axis responded with: {}".format(resp))
        elif resp == 'M': return True
        elif resp in ['@', 'J']: return False
        else: raise KeyError('Unknown response: {}'.format(resp))

    # MOVEMENT FUNCTIONS
    @typechecked
    def start_jog(self, direction : Union[str, int]) -> None:
        """Start a continuous jog in the given direction."""
        # Check if the direction is allowed
        if not isinstance(direction, str):
            direction = str(direction)
        if direction not in ['+', '-']:
            raise ValueError("The direction {} is not allowed.".format(direction))

        rev_per_s = self._send_and_receive('?vel', expect_response=True, expect_confirmation=False).split(' ')[2]
        rev_per_s = float(rev_per_s)
        self._send_and_receive('!speed {}{}'.format(direction, rev_per_s), expect_response=False, expect_confirmation=False)

    def stop_jog(self) -> None:
        self._send_and_receive('!speed 0', expect_response=False, expect_confirmation=False)

    @typechecked
    def move_to(self, position : Union[float, int]) -> None:
        """Move the tango desktop to the given position."""
        self._send_and_receive('!moa z {}'.format(position), expect_response=False, expect_confirmation=False)

    @typechecked
    def move_by(self, distance : Union[float, int]) -> None:
        """Move the tango desktop by the given distance."""
        self._send_and_receive('!mor z {}'.format(distance), expect_response=False, expect_confirmation=False)

    def stop(self) -> None:
        """Stop the tango desktop."""
        self._send_and_receive('!stop', expect_response=False, expect_confirmation=False)


if __name__ == '__main__':
    tango = TangoDesktop()
    tango.connect()
    print('Position: {}'.format(tango.position))
    print('Speed: {}'.format(tango.speed))
    print('Acceleration: {}'.format(tango.acceleration))
    tango.move_by(10000)  # Move 10mm up
    print('Is moving: {}'.format(tango.is_moving()))
    tango.move_to(0)
    while tango.is_moving():
        pass
    print('Is moving: {}'.format(tango.is_moving()))
    tango.disconnect()