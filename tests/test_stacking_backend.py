from re import X
import sys, os
import unittest
from unittest.mock import MagicMock, patch, PropertyMock, Mock
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
    mock_part.is_connected.return_value = Mock(side_effect=True)
    mock_part.move_by.return_value = Mock(side_effect=None)
    mock_part.move_to.return_value = Mock(side_effect=None)
    mock_part.rotate_by.side_effect = Mock(side_effect=NotSupportedError)
    mock_part.rotate_to.side_effect = Mock(side_effect=NotSupportedError)
    
    # Set some attributes
    mock_part.position = 0
    mock_part.steps_per_um = 1
    mock_part.speed = 2
    mock_part.acceleration = 3
    type(mock_part).temperature = PropertyMock(side_effect=NotSupportedError)
    type(mock_part).target_temperature = PropertyMock(side_effect=NotSupportedError)

    return mock_part

def mock_prmtz8(id):
    mock_part = MagicMock(spec=Base)
    mock_part.id = id
    mock_part.type = 'PRMTZ8'

    # Add the functions that should not error
    mock_part.is_connected.return_value = Mock(side_effect=True)
    mock_part.rotate_by.return_value = Mock(side_effect=None)
    mock_part.rotate_to.return_value = Mock(side_effect=None)
    mock_part.move_by.side_effect = Mock(side_effect=NotSupportedError)
    mock_part.move_to.side_effect = Mock(side_effect=NotSupportedError)
    
    # Set some attributes
    mock_part.position = 0
    mock_part.steps_per_deg = 1
    mock_part.speed = 2
    mock_part.acceleration = 3
    type(mock_part).temperature = PropertyMock(side_effect=NotSupportedError)
    type(mock_part).target_temperature = PropertyMock(side_effect=NotSupportedError)

    return mock_part

def mock_sample_holder(id):
    mock_part = MagicMock(spec=Base)
    mock_part.id = id
    mock_part.type = 'SAMPLE HOLDER'

    # Add the functions that should not error
    mock_part.is_connected = Mock(return_value=True)
    mock_part.move_by = Mock(side_effect=NotSupportedError)
    mock_part.move_to = Mock(side_effect=NotSupportedError)
    mock_part.rotate_by = Mock(side_effect=NotSupportedError)
    mock_part.rotate_to = Mock(side_effect=NotSupportedError)
    
    # Set some attributes
    mock_part.temperature = 0
    mock_part.target_temperature = 10
    type(mock_part).position = PropertyMock(side_effect=NotSupportedError)
    type(mock_part).steps_per_um = PropertyMock(side_effect=NotSupportedError)
    
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

    def setUp(self):
        self.to_main, self.to_proc = mp.Pipe()
        
    def tearDown(self):
        # Close the pipes
        self.to_main.close()
        self.to_proc.close()
        
    # Test initiate hardware
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_connect_hardware(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        stack = StackingSetupBackend(self.to_main)
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
        stack = StackingSetupBackend(self.to_main)
        stack._disconnect_all_hardware()

        for i in stack._hardware:
            try:
                i.disconnect.assert_called_once()
            except AssertionError as e:
                raise AssertionError('{} was not disconnected : {}'.format(i.id, e))

    # Test emergency stop
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_emergency_stop(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        stack = StackingSetupBackend(self.to_main)
        stack._emergency_stop()

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
        stack = StackingSetupBackend(self.to_main)
        movement = {'X': 1, 'Y': 2, 'Z': 3}
        exit_code, msg = stack.G0(movement)

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
        stack = StackingSetupBackend(self.to_main)
        movement = {'L': 1}
        exit_code, msg = stack.G0(movement)

        # Check if the right functions were called.
        stack._hardware[3].move_by.assert_called()

        # Check if the return code is right
        self.assertEqual(exit_code, 1)
        self.assertNotEqual(msg, None)

    # Test G0 non existing part
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_G0_non_existing_part(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        stack = StackingSetupBackend(self.to_main)
        movement = {'X': 5,'A': 1}
        exit_code, msg = stack.G0(movement)

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
        stack = StackingSetupBackend(self.to_main)
        movement = {'L': 5}
        exit_code, msg = stack.G1(movement)

        # Check if the right functions were called.
        stack._hardware[3].rotate_by.assert_called_once_with(5)

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

    # Test G1 with a part that does not support it
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_G1_not_supported(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        stack = StackingSetupBackend(self.to_main)
        movement = {'X': 5}
        exit_code, msg = stack.G1(movement)

        # Check if the right functions were called.
        stack._hardware[0].rotate_by.assert_called_with(5)

        # Check if the return code is right
        self.assertEqual(exit_code, 1)
        self.assertNotEqual(msg, None)

    # Test G1 non existing part
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_G1_non_existing_part(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        stack = StackingSetupBackend(self.to_main)
        movement = {'L': 5,'A': 1}
        exit_code, msg = stack.G1(movement)

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
        stack = StackingSetupBackend(self.to_main)
        exit_code, msg = stack.G28()

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
        stack = StackingSetupBackend(self.to_main)

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
        stack = StackingSetupBackend(self.to_main)
        factors = {'Y': 5}
        exit_code, msg = stack.M92(factors)

        # Check if the right functions were called.
        self.assertEqual(stack._hardware[1].steps_per_um, 5)

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

    # Test M105
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_M105(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        stack = StackingSetupBackend(self.to_main)
        exit_code, msg = stack.M105()

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertNotEqual(msg, None)
        self.assertEqual(msg, {'K': {'current' : 0, 'target' : 10}})

    # Test M112
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_M112(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        stack = StackingSetupBackend(self.to_main)
        exit_code, msg = stack.M112()

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

        self.assertTrue(stack._emergency_breaker.is_set())

    # Test M113
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_M113(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        stack = StackingSetupBackend(self.to_main)
        exit_code, msg = stack.M113(1)

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

        try:
            # Check if the interval is set right
            self.assertEqual(stack._keep_host_alive_timer.interval, 1)
            # Check if the keep alive timer is set
            stack._keep_alive_timer.cancel() 

        except AttributeError:
            self.fail("The keep alive timer was not set.")

        # Start the timer again and wait for the message to be sent
        exit_code, msg = stack.M113(0.01)  # 10ms
        in_waiting = self.to_proc.poll(timeout=0.5)
        self.assertTrue(in_waiting)
    
    # Test M114	
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=MagicMock())
    def test_M114(self, _init_emergency_breaker_mock, _init_all_hardware_mock):
        stack = StackingSetupBackend(self.to_main)
        exit_code, msg = stack.M114()

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertNotEqual(msg, None)
        self.assertEqual(msg, {'X': 0, 'Y': 0, 'Z': 0, 'L': 0})

    # Test M999


if __name__ == '__main__':
    # Run all the tests in this file
    unittest.main()
