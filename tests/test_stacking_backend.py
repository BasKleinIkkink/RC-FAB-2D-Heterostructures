from re import X
import sys, os
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import multiprocessing as mp

#Following lines are for assigning parent directory dynamically.
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

# The code to be tested
from stacking_setup.stacking_backend.hardware.exceptions import NotSupportedError
from stacking_setup.stacking_backend.stacking_setup import StackingSetupBackend
from stacking_setup.stacking_backend.configs.accepted_commands import ACCEPTED_COMMANDS, ACCEPTED_AXES, ACCEPTED_LINEAR_AXES, ACCEPTED_ROTATIONAL_AXES
from stacking_setup.stacking_backend.hardware.base import Base


def mock_pia13(id):
    mock_part = MagicMock(spec=Base)
    mock_part.id = id
    mock_part.type = 'PIA13'

    # Add the functions that should not error
    mock_part.is_connected = MagicMock(return_value=True)
    mock_part.move_by = MagicMock(return_value=None)
    mock_part.move_to = MagicMock(return_value=None)
    mock_part.rotate_by = MagicMock(return_value=NotSupportedError)
    mock_part.rotate_to = MagicMock(return_value=NotSupportedError)
    
    # Set some attributes
    mock_part.position = PropertyMock(return_value=0)
    mock_part.steps_per_um = PropertyMock(return_value=1)
    mock_part.speed = PropertyMock(return_value=2)
    mock_part.acceleration = PropertyMock(return_value=3)
    mock_part.temperature = PropertyMock(return_value=NotSupportedError)
    mock_part.target_temperature = PropertyMock(return_value=NotSupportedError)

    return mock_part

def mock_prmtz8(id):
    mock_part = MagicMock(spec=Base)
    mock_part.id = id
    mock_part.type = 'PRMTZ8'

    # Add the functions that should not error
    mock_part.is_connected = MagicMock(return_value=True)
    mock_part.rotate_by = MagicMock(return_value=None)
    mock_part.rotate_to = MagicMock(return_value=None)
    mock_part.move_by = MagicMock(return_value=NotSupportedError)
    mock_part.move_to = MagicMock(return_value=NotSupportedError)
    
    # Set some attributes
    mock_part.position = PropertyMock(return_value=0)
    mock_part.steps_per_deg = PropertyMock(return_value=1)
    mock_part.speed = PropertyMock(return_value=2)
    mock_part.acceleration = PropertyMock(return_value=3)
    mock_part.temperature = PropertyMock(return_value=NotSupportedError)
    mock_part.target_temperature = PropertyMock(return_value=NotSupportedError)

    return mock_part

def mock_sample_holder(id):
    mock_part = MagicMock(spec=Base)
    mock_part.id = id
    mock_part.type = 'SAMPLE HOLDER'

    # Add the functions that should not error
    mock_part.is_connected = MagicMock(return_value=True)
    mock_part.move_by = MagicMock(return_value=NotSupportedError)

    
    # Set some attributes
    mock_part.temperature = PropertyMock(return_value=0)
    mock_part.target_temperature = PropertyMock(return_value=1)
    
    return mock_part


class TestControlBackend(unittest.TestCase):

    @staticmethod
    def _get_hardware_mocks():
        """
        Create a mock hardware for the backend to control.

        Returns:
            A tuple of mock hardware objects (MagicMocks).

        """
        return [mock_pia13('X'),
                mock_pia13('Y'),
                mock_pia13('Z'),
                mock_prmtz8('L'),
                mock_sample_holder('K'),]

    # Test initiate hardware
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_connect_hardware(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        # Test the initiate hardware function.
        to_main, _ = mp.Pipe()
        stack = StackingSetupBackend(to_main)
        stack._connect_all_hardware()

        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()
        _init_emergency_breaker_mock.assert_called_once()

        for i in stack._hardware:
            try:
                i.connect.assert_called_once()
            except AssertionError as e:
                raise AssertionError('{} was not connected : {}'.format(i.id, e))

    # Test disconnect hardware
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_disconnect_hardware(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        # Test the initiate hardware function.
        to_main, _ = mp.Pipe()
        stack = StackingSetupBackend(to_main)
        stack._disconnect_all_hardware()

        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()
        _init_emergency_breaker_mock.assert_called_once()

        for i in stack._hardware:
            try:
                i.disconnect.assert_called_once()
            except AssertionError as e:
                raise AssertionError('{} was not disconnected : {}'.format(i.id, e))

    # Test emergency stop
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_emergency_stop(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        to_main, _ = mp.Pipe()
        stack = StackingSetupBackend(to_main)
        stack._emergency_stop()

        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()
        _init_emergency_breaker_mock.assert_called_once()

        # Check if the emergency stop flag was set.
        self.assertTrue(stack._emergency_stop_event.is_set())

    # Test the control loop
    #@patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    #@patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    #def test_control_loop(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
    #    # Test the initiate hardware function.
    #    to_main, from_process = mp.Pipe()
    #    stack = StackingSetupBackend(to_main)
    #    stack._control_loop()

    #    # Check if the right functions were called.
    #    _init_all_hardware_mock.assert_called_once()
    #    _init_emergency_breaker_mock.assert_called_once()

        # Start the process
    #    stack.start_backend_process()
    
    # Test execute one command

    # Test execute multiple commands

    # Test execute lots of commands

    # Test G0
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_G0(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        to_main, _ = mp.Pipe()
        stack = StackingSetupBackend(to_main)
        movement = {'X': 1, 'Y': 2, 'Z': 3}
        exit_code, msg = stack.G0(movement)

        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()
        _init_emergency_breaker_mock.assert_called_once()

        # Check if the right functions were called.
        stack._hardware[0].move_by.assert_called_once_with(1)
        stack._hardware[1].move_by.assert_called_once_with(2)
        stack._hardware[2].move_by.assert_called_once_with(3)

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

    # Test G0 with a part that does not support it
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_G0_not_supported(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        to_main, _ = mp.Pipe()
        stack = StackingSetupBackend(to_main)
        movement = {'L': 1}
        exit_code, msg = stack.G0(movement)

        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()
        _init_emergency_breaker_mock.assert_called_once()

        # Check if the right functions were called.
        stack._hardware[3].move_by.assert_called()

        # Check if the return code is right
        self.assertEqual(exit_code, 1)
        self.assertNotEqual(msg, None)

    # Test G0 non existing part
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_G0_non_existing_part(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        to_main, _ = mp.Pipe()
        stack = StackingSetupBackend(to_main)
        movement = {'X': 5,'A': 1}
        exit_code, msg = stack.G0(movement)

        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()
        _init_emergency_breaker_mock.assert_called_once()

        # Check if the right functions were called.
        stack._hardware[0].move_by.assert_called_once_with(5)
        for axis in stack._hardware[1:]:
            axis.move_by.assert_not_called()

        # Check if the return code is right
        self.assertEqual(exit_code, 1)
        self.assertNotEqual(msg, None)

    # Test G1
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_G1(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        to_main, _ = mp.Pipe()
        stack = StackingSetupBackend(to_main)
        movement = {'L': 5}
        exit_code, msg = stack.G1(movement)

        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()
        _init_emergency_breaker_mock.assert_called_once()

        # Check if the right functions were called.
        stack._hardware[3].rotate_by.assert_called_once_with(5)

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

    # Test G1 with a part that does not support it
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_G1_not_supported(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        to_main, _ = mp.Pipe()
        stack = StackingSetupBackend(to_main)
        movement = {'X': 5}
        exit_code, msg = stack.G1(movement)

        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()
        _init_emergency_breaker_mock.assert_called_once()

        # Check if the right functions were called.
        stack._hardware[0].rotate_by.assert_called_with(5)

        # Check if the return code is right
        self.assertEqual(exit_code, 1)
        self.assertNotEqual(msg, None)

    # Test G1 non existing part
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_G1_non_existing_part(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        to_main, _ = mp.Pipe()
        stack = StackingSetupBackend(to_main)
        movement = {'L': 5,'A': 1}
        exit_code, msg = stack.G1(movement)

        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()
        _init_emergency_breaker_mock.assert_called_once()

        # Check if the right functions were called.
        stack._hardware[3].rotate_by.assert_called_once_with(5)
        for axis in stack._hardware[1:]:
            if axis.id == 'L':
                continue
            axis.rotate_by.assert_not_called()

        # Check if the return code is right
        self.assertEqual(exit_code, 1)
        self.assertNotEqual(msg, None)

    # Test G28
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_G28(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        to_main, _ = mp.Pipe()
        stack = StackingSetupBackend(to_main)
        exit_code, msg = stack.G28()

        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()
        _init_emergency_breaker_mock.assert_called_once()

        # Check if the right functions were called.
        stack._hardware[0].home.assert_called_once()
        stack._hardware[1].home.assert_called_once()
        stack._hardware[2].home.assert_called_once()
        stack._hardware[3].home.assert_called_once()

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

    # Test G90
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_G90andG91(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        to_main, _ = mp.Pipe()
        stack = StackingSetupBackend(to_main)

        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()
        _init_emergency_breaker_mock.assert_called_once()

        # Change the mode a few times
        _, _ = stack.G90()
        self.assertEqual(stack._positioning, 'ABS')
        _, _ = stack.G91()
        self.assertEqual(stack._positioning, 'REL')
        exit_code, msg = stack.G90()
        self.assertEqual(stack._positioning, 'ABS')

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

    # Test M92
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_M92(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        to_main, _ = mp.Pipe()
        stack = StackingSetupBackend(to_main)
        movement = {'X': 5}
        exit_code, msg = stack.M92(movement)

        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()
        _init_emergency_breaker_mock.assert_called_once()

        # Check if the right functions were called.
        stack._hardware[3].set_steps_per_unit.assert_called_once_with(5)

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

    # Test M105

    # Test M112

    # Test M113

    # Test M999


if __name__ == '__main__':
    # Run all the tests in this file
    unittest.main()
