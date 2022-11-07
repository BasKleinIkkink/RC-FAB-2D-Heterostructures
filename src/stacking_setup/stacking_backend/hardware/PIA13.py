from typing import Union
from typeguard import typechecked

try:
    from .base import Base, NotCalibratedError
    from .KIM101 import KIM101
except ImportError:
    from base import Base, NotCalibratedError
    from KIM101 import KIM101


class PIA13(Base):
    """Class to control a PIA13 Thorlabs piezo actuator."""
    

    def __init__(self, id : str, channel : int, actuator_id : str, hardware_controller : KIM101) -> None:
        """
        Initialize the PIA13.
        
        Parameters
        ----------
        id: str
            The id of the hardware.
        channel: int
            The channel of the hardware.
        actuator_id: int
            The id of the actuator.
        hardware_controller: KIM101
            The hardware controller to use.
        """
        self._id = id
        self._type = 'PIA13'
        self._channel = channel
        self._hardware_controller = hardware_controller
        self._steps_calibrated = False  # Steps per nm were calibrated
        self._steps_per_nm = 0  # Steps per nm

    # ATTRIBUTES
    @property
    def device_info(self) -> None:
        """Get the device info."""
        return {'id': self._id,
                'type': self._type,
                'channel': self._channel,
                'controller': self._hardware_controller
                }

    @property
    def steps_per_um(self) -> None:
        """Get the steps per um."""
        # Return the steps per um
        return self._steps_per_um

    @steps_per_um.setter
    def steps_per_um(self, steps_per_mm : Union[float, int]) -> None:
        """
        Set the steps per um.
        
        Parameters
        ----------
        steps_per_mm: float or int
            The steps per um.
        """
        if not self._steps_calibrated:
            raise NotCalibratedError('Steps per nm were not calibrated/set.')

        # Set the jog settings on the hardware controller.
        return self._hardware_controller.set_steps_per_nm(self._channel, 
                                                        steps_per_mm)

    @property
    def position(self) -> None:
        """Get the position of the hardware."""
        return self._hardware_controller.get_position(self._channel)

    @property
    def speed(self) -> None:
        """Get the speed of the hardware."""
        drive = self._hardware_controller.get_drive_parameters(self._channel)
        return drive[3]

    @speed.setter
    def speed(self, speed : Union[float, int]) -> None:
        """
        Set the speed of the hardware.
        
        Parameters:
        -----------
        speed: float or int
            The speed to set the hardware to.
        """
        if speed >= self._max_speed:
            self._hardware_controller.setup_drive(self._channel, velocity=speed)
        else:
            self._hardware_controller.setup_drive(self._channel, velocity=self._max_speed)

    @property
    def acceleration(self) -> float:
        """
        Get the acceleration of the hardware.
        
        Returns
        -------
        acceleration: float
            The acceleration of the hardware.
        """
        drive = self._hardware_controller.get_drive_parameters(self._channel)
        return drive[4]

    @acceleration.setter
    def acceleration(self, acceleration : Union[float, int]) -> None:
        """
        Set the acceleration of the hardware.
        
        Parameters
        ----------
        acceleration: float or int
            The acceleration to set the hardware to. 
        """
        if acceleration >= self._max_acceleration:
            self._hardware_controller.setup_drive(self._channel, acceleration=acceleration)
        else:
            self._hardware_controller.setup_drive(self._channel, acceleration=self._max_acceleration)

    # CONNECTION FUNCTIONS
    def connect(self) -> None:
        """Connect the hardware."""
        if not self._hardware_controller.is_connected():
            self._hardware_controller.connect()
        else:
            pass

    def disconnect(self) -> None:
        """Disconnect the hardware."""
        if self._hardware_controller.is_connected():
            self._hardware_controller.disconnect()
        else:
            pass

    # STATUS FUNCTIONS
    def is_connected(self) -> None:
        """Check if the hardware is connected."""
        return self._hardware_controller.is_connected()

    def get_status(self) -> None:
        """Get the statusreport of the hardware."""
        return self._hardware_controller.get_status(self._channel)

    def is_moving(self) -> None:
        """Check if the hardware is moving."""
        return self._hardware_controller.is_moving(self._channel)

    def get_status(self) -> None:
        return {'id': self._id,
                'is_moving': self.is_moving(),
                'position': self.position,
                'speed': self.speed,
                'acceleration': self.acceleration,
                'steps_per_mm': self.steps_per_mm,
                'max_speed': self._max_speed,
                'max_acceleration': self._max_acceleration,
                }

    # MOVEMENT FUNCTIONS
    def start_jog(self, direction : str) -> None:
        """
        Start a jog.

        Parameters
        ----------
        direction: str
            The direction to jog in (+ or -).
        """
        self._hardware_controller.start_jog(self._channel, direction)

    def stop_jog(self) -> None:
        """Stop the jog."""
        self._hardware_controller.stop_jog(self._channel)
        
    def move_by(self, distance : Union[float, int]) -> None:
        """
        Move the hardware by a certain distance.

        Parameters
        ----------
        distance: float or int
            The distance to move the hardware.
        """
        self._hardware_controller.move_by(self._channel, distance)

    def move_to(self, position : Union[float, int]) -> None:
        """
        Move the hardware to a certain position.

        Parameters
        ----------
        position: float or int
            The position to move the hardware to.
        """
        if not self._steps_calibrated:
            raise NotCalibratedError('Steps per nm were not calibrated/set.')

        self._hardware_controller.move_to(self._channel, position)

    def stop(self):
        """Stop the hardware."""
        self._hardware_controller.stop(self._channel)


if __name__ == '__main__':
    controller = KIM101()
    piezo = PIA13('X', 1, 1, controller)
    piezo.connect()
    piezo.move_by(500)