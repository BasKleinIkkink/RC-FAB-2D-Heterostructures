import unittest
from unittest.mock import MagicMock, patch, PropertyMock, Mock
import multiprocessing as mp
import configparser
from typing import List

#Following lines are for assigning parent directory dynamically.
import sys, os
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

# The code to be tested
from components.stacking_backend.stacking_setup import StackingSetupBackend
from components.stacking_backend.hardware.base import Base, NotSupportedError
from components.stacking_backend.configs.settings import Settings
from components.stacking_middleware.message import Message
from components.stacking_backend.configs.accepted_commands import ACCEPTED_COMMANDS, ACCEPTED_LINEAR_AXES, ACCEPTED_ROTATIONAL_AXES


def mock_pia13(id) -> MagicMock:
    """
    Create a mock class for the pia

    Parameters:
    -----------
    id: str
        The axis id of the pia.
    
    Returns:
    --------
    mock_part : MagicMock
        A mock pia object (MagicMock).
    """
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


def mock_prmtz8(id) -> MagicMock:
    """
    Create a mock class for the PRMTZ8.

    Parameters:
    -----------
    id: str
        The axis id of the PRMTZ8.

    Returns:
    --------
    mock_part : MagicMock
        A mock PRMTZ8 object (MagicMock).
    """
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
    mock_part.steps_per_um = 1
    mock_part.speed = 2
    mock_part.acceleration = 3
    type(mock_part).temperature = PropertyMock(side_effect=NotSupportedError)
    type(mock_part).target_temperature = PropertyMock(side_effect=NotSupportedError)

    return mock_part


def mock_sample_holder(id) -> MagicMock:
    """
    Create a mock class for the sample holder.

    Parameters:
    -----------
    id: str
        The axis id of the sample holder.

    Returns:
    --------
    mock_part : MagicMock
        A mock sample holder object (MagicMock).
    """
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


def mock_base_stepper(id):
    """
    Create a mock class for the base stepper.

    Parameters:
    -----------
    id: str
        The axis id of the base stepper.

    Returns:
    --------
    mock_part : MagicMock
        A mock base stepper object (MagicMock).
    """
    mock_part = MagicMock(spec=Base)
    mock_part.id = id
    mock_part.type = 'BASE STEPPER'

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


def _get_hardware_mocks() -> List[MagicMock]:
    """
    Create mock hardware for the backend to control.

    Returns:
    --------
    hardware : list
        A tuple of mock hardware objects (MagicMocks)
    """
    return [mock_pia13('X'),
            mock_pia13('Y'),
            mock_pia13('Z'),
            mock_prmtz8('L'),
            mock_sample_holder('K'),
            mock_base_stepper('H'),
            mock_base_stepper('J')]


class TestControlBackend(unittest.TestCase):
    """
    This test class test the main functions of the backend.

    Individual functions (such as M and G commands) are not tested
    here. This class tests the connection, execution and communication
    functions.

    .. attention::
        The only command tested in this class is M112, this because this is
        the emergency stop command.

    .. note::
        This class makes extensive use of mocking. This is done to
        prevent the backend from connecting to the hardware and to
        prevent the backend from executing the commands. This also
        means all tests can be run without connecting to the hardware.
    """

    def setUp(self) -> ...:
        """
        Set up the backend for testing.
        
        .. note::
            Because patching is used to prevent the backend from connecting
            to the hardware the backend is not started in the setUp.
        """
        self.to_main, self.to_proc = mp.Pipe()
        
    def tearDown(self) -> ...:
        """Clean up after the test."""
        # Close the pipes
        self.to_main.close()
        self.to_proc.close()
        
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_connect_hardware(self, _init_all_hardware_mock) -> ...:
        """
        Test if all the hardware is called when connecting.

        .. attention::
            When a part is disabled in config it will not be called
            and this method will fail. As disabling parts is only meant
            for debugging all parts should be active during normal operation.
        """
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()

        for i in stack._hardware:
            try:
                i.connect.assert_called_once()
            except AssertionError as e:
                raise AssertionError('{} was not connected : {}'.format(i.id, e))

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_disconnect_hardware(self, _init_all_hardware_mock) -> ...:
        """
        Test if all the hardware is called when disconnecting.

        .. attention::
            When a part is disabled in config it will not be called
            and this method will fail. As disabling parts is only meant
            for debugging all parts should be active during normal operation.
        """
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        stack._disconnect_all_hardware()

        for i in stack._hardware:
            try:
                i.disconnect.assert_called_once()
            except AssertionError as e:
                raise AssertionError('{} was not disconnected : {}'.format(i.id, e))

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_emergency_stop(self, _init_all_hardware_mock) -> ...:
        """
        Test if the emergency stop flag is set when the emergency stop
        command is called.
        """
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        stack._emergency_stop()

        # Check if the emergency stop flag was set.
        self.assertTrue(stack._emergency_stop_event.is_set())

    # @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    # def test_echo(self, _init_all_hardware_mock) -> ...:
    #     """
    #     Test if the echo function sends the right message.

    #     The echo function is used to create the execution threads and 
    #     relay the output message back to the frontend.
    #     """
    #     stack = StackingSetupBackend(self.to_main)
    #     stack.setup_backend(Settings())

    #     def test_function(dummy1):
    #         return 0, dummy1

    #     def test_function2(dummy1=None):
    #         return 0, dummy1
        
    #     stack._echo(func=test_function, command_id='test', command={'X': 1})

    #     # Check if the right message was sent.
    #     msg = {'X': 1}
    #     exit_code = 0
    #     while stack._execution_q.empty():
    #         continue
    #     pipe_msg = stack._execution_q.get()
    #     self.assertIsInstance(pipe_msg, Message)
    #     self.assertEqual(pipe_msg.msg, msg)
    #     self.assertEqual(pipe_msg.exit_code, exit_code)
    #     self.assertEqual(pipe_msg.command_id, 'test')
    #     self.assertEqual(pipe_msg.command, msg)

    #     stack._echo(func=test_function2, command_id='test2')

    #     while not stack._execution_q.empty():
    #         continue
    #     pipe_msg = stack._execution_q.get()
    #     self.assertEqual(pipe_msg.msg, '')
    #     self.assertEqual(pipe_msg.exit_code, exit_code)
    #     self.assertEqual(pipe_msg.command_id, 'test2')
    #     self.assertEqual(pipe_msg.command, None)
    
    @patch.object(StackingSetupBackend, 'G0', return_value=(0, None))
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_execute_one_command(self, _init_all_hardware_mock, G0_mock) -> ...:
        """Test if the execute command function calls the right function."""
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())

        # Test a command that is not implemented
        stack._execute_command({'M1000': {}})
        while not stack._execution_q.empty():
            continue
        pipe_msg = self.to_proc.recv()
        self.assertNotEqual(pipe_msg.msg, '')
        self.assertEqual(pipe_msg.exit_code, 1)

        # Test a command that is implemented
        stack._execute_command({'G0': {'X': 5}})
        while not stack._execution_q.empty():
            continue
        pipe_msg = self.to_proc.recv()
        self.assertEqual(pipe_msg.msg, '')
        self.assertEqual(pipe_msg.exit_code, 0)

    # Test execute multiple commands
    @patch.object(StackingSetupBackend, 'G0', return_value=(0, None))
    @patch.object(StackingSetupBackend, 'G1', return_value=(0, None))
    @patch.object(StackingSetupBackend, 'M105', return_value=(0, None))
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_execute_multiple_commands(self, _init_all_hardware_mock,
                                        M105_mock, G1_mock, G0_mock) -> ...:
        """
        Test if the execute command function calls the right function.
        
        The backend supports multiple commands in one message.
        """
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())

        # Test a command that is not implemented
        stack._execute_command({'M1000': {}, 'G1': {'X': 5, 'Y': 5, 'I': 5, 'J': 5}})
        while not stack._execution_q.empty():
            continue
        pipe_msg = self.to_proc.recv()
        self.assertIsInstance(pipe_msg.msg, str)
        self.assertEqual(pipe_msg.exit_code, 1)

        # Empty the pipe
        self.to_proc.recv()

        # Test a command that is implemented
        stack._execute_command({'G0': {'X': 5}, 'M105': {}})
        while not stack._execution_q.empty():
            continue
        pipe_msg = self.to_proc.recv()
        self.assertEqual(pipe_msg.msg, '')
        self.assertEqual(pipe_msg.exit_code, 0)

    # Test call M112
    @patch.object(StackingSetupBackend, 'M112', return_value=(0, None))
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_call_M112(self, _init_all_hardware_mock, M112_mock) -> ...:
        """Test the emergency stop command."""
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())

        # When calling with no arguments the function should return the current value
        command = {'M112': {}}
        stack._execute_command(command)
        M112_mock.assert_called_once()

        # Get the message from the pipe
        stack._check_command_output()
        pipe_msg = self.to_proc.recv()
        self.assertEqual(pipe_msg.msg, '')
        self.assertEqual(pipe_msg.exit_code, 0)


class TestMovementCommands(unittest.TestCase):
    """
    Test the movement commands.
    
    Movement commands are commands starting with G.
    """

    def setUp(self) -> ...:
        """Create the backend for testing."""
        self.to_main, self.to_proc = mp.Pipe()
        
    def tearDown(self) -> ...:
        """Clean up after testing."""
        # Close the pipes
        self.to_main.close()
        self.to_proc.close()

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G0(self, _init_all_hardware_mock) -> ...:
        """Test the G0 command."""
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        self.assertTrue('G0' in ACCEPTED_COMMANDS)
        movement = {'X': 1, 'Y': 2, 'Z': 3}
        exit_code, msg = stack.G0(movement)

        # Check if the right functions were called.
        stack._hardware[0].move_by.assert_called_once_with(1)
        stack._hardware[1].move_by.assert_called_once_with(2)
        stack._hardware[2].move_by.assert_called_once_with(3)

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G0_not_supported(self, _init_all_hardware_mock) -> ...:
        """Test the G0 command for a non supported part."""
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        self.assertTrue('G0' in ACCEPTED_COMMANDS)
        movement = {'L': 1}
        exit_code, msg = stack.G0(movement)

        # Check if the right functions were called.
        stack._hardware[3].move_by.assert_called()

        # Check if the return code is right
        self.assertEqual(exit_code, 1)
        self.assertNotEqual(msg, None)

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G0_non_existing_part(self, _init_all_hardware_mock) -> ...:
        """Test the G0 command for a non existing part."""
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        self.assertTrue('G0' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        movement = {'X': 5,'A': 1}
        exit_code, msg = stack.G0(movement)

        # Check if the right functions were called.
        stack._hardware[0].move_by.assert_called_once_with(5)
        for axis in stack._hardware[1:]:
            axis.move_by.assert_not_called()

        # Check if the return code is right
        self.assertEqual(exit_code, 1)
        self.assertNotEqual(msg, None)

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G1(self, _init_all_hardware_mock) -> ...:
        """Test the G1 command."""
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        self.assertTrue('G1' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        movement = {'L': 5}
        exit_code, msg = stack.G1(movement)

        # Check if the right functions were called.
        stack._hardware[3].rotate_by.assert_called_once_with(5)

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G1_not_supported(self, _init_all_hardware_mock) -> ...:
        """Test the G1 command for a non supported part."""
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        self.assertTrue('G1' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        movement = {'X': 5}
        exit_code, msg = stack.G1(movement)

        # Check if the right functions were called.
        stack._hardware[0].rotate_by.assert_called_with(5)

        # Check if the return code is right
        self.assertEqual(exit_code, 1)
        self.assertNotEqual(msg, None)

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G1_non_existing_part(self, _init_all_hardware_mock) -> ...:
        """Test the G1 command for a non existing part."""
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        self.assertTrue('G1' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
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

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G28(self, _init_all_hardware_mock) -> ...:
        """Test the G28 command."""
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        self.assertTrue('G28' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        exit_code, msg = stack.G28()

        # Check if the right functions were called.
        stack._hardware[0].home.assert_called_once()
        stack._hardware[1].home.assert_called_once()
        stack._hardware[2].home.assert_called_once()
        stack._hardware[3].home.assert_called_once()

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G90andG91(self, _init_all_hardware_mock) -> ...:
        """Test the G90 and G91 commands."""
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        self.assertTrue('G90' in ACCEPTED_COMMANDS)
        self.assertTrue('G91' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())

        # Change the mode a few times
        _, _ = stack.G90()
        self.assertEqual(stack._positioning, 'ABS')
        _, _ = stack.G91()
        self.assertEqual(stack._positioning, 'REL')
        exit_code, msg = stack.G90()
        self.assertEqual(stack._positioning, 'ABS')

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertNotEqual(msg, None)


class TestMachineCommands(unittest.TestCase):
    """
    Test the machine commands.
    
    Machine commands are commands starting with M.
    """

    def setUp(self) -> ...:
        """Set up the stacking backend."""
        self.to_main, self.to_proc = mp.Pipe()
        self.settings = configparser.ConfigParser()
        
    def tearDown(self) -> ...:
        """Clean up after the tests."""
        # Close the pipes
        self.to_main.close()
        self.to_proc.close()

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M92(self, _init_all_hardware_mock) -> ...:
        """Test the M92 command."""
        self.assertTrue('M92' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())

        factors = {'Y': 5}
        exit_code, msg = stack.M92(factors)

        # Check if the right functions were called.
        self.assertEqual(stack._hardware[1].steps_per_um, 5)

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

        # Get the current factors
        stack._hardware[1].steps_per_um = 1
        exit_code, msg = stack.M92({})
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, {'X': 1, 'Y': 1, 'Z': 1, 'L': 1, 'H': 1, 'J': 1})

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M105(self, _init_all_hardware_mock) -> ...:
        """Test the M105 command."""
        self.assertTrue('M105' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        exit_code, msg = stack.M105()

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertNotEqual(msg, None)
        self.assertEqual(msg, {'K': {
            'current' : 0,
            'target' : 10,
        }})

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M112(self, _init_all_hardware_mock) -> ...:
        """Test the M112 command."""
        self.assertTrue('M112' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        exit_code, msg = stack.M112()

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

        self.assertTrue(stack._emergency_stop_event.is_set())

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M113(self, _init_all_hardware_mock) -> ...:
        """Test the M113 command."""
        self.assertTrue('M113' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())

        # Ask for the inteval without one being set
        exit_code, msg = stack.M113({})
        self.assertEqual(exit_code, 1)
        self.assertNotEqual(msg, None)

        # Set a timer and ask the inteval
        exit_code, msg = stack.M113({'S': 1})
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)
        exit_code, msg = stack.M113({})
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, '1')
    
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M114(self, _init_all_hardware_mock) -> ...:
        """Test the M114 command."""
        self.assertTrue('M114' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        exit_code, msg = stack.M114()

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertNotEqual(msg, None)
        self.assertEqual(msg, {'X': 0, 'Y': 0, 'Z': 0, 'L': 0, 'H': 0, 'J': 0})

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M154(self, _init_all_hardware_mock) -> ...:
        """Test the M154 command."""
        self.assertTrue('M154' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())

        # Ask for the inteval without one being set
        exit_code, msg = stack.M154({})
        self.assertEqual(exit_code, 1)
        self.assertNotEqual(msg, None)

        # Set a timer and ask the inteval
        exit_code, msg = stack.M154({'S': 1})
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)
        exit_code, msg = stack.M154({})
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, 1)

    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M155(self, _init_all_hardware_mock) -> ...:
        """Test the M155 command."""
        self.assertTrue('M155' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())

        # Ask for the inteval without one being set
        exit_code, msg = stack.M155({})
        self.assertEqual(exit_code, 1)
        self.assertNotEqual(msg, None)

        # Set a timer and ask the inteval
        exit_code, msg = stack.M155({'S': 1})
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)
        exit_code, msg = stack.M155({})
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, 1)


class TestSettings(unittest.TestCase):
    """Test the Settings class."""

    def setUp(self) -> ...:
        """Set up the test."""
        self.settings = Settings()

    def test_getattr(self) -> ...:
        """Test getting the attributes."""
        accepted_commands = self.settings.accepted_commands
        accepted_linear_axes = self.settings.accepted_linear_axes
        accepted_rotational_axes = self.settings.accepted_rotational_axes

        self.assertEqual(accepted_commands, ACCEPTED_COMMANDS)
        self.assertEqual(accepted_linear_axes, ACCEPTED_LINEAR_AXES)
        self.assertEqual(accepted_rotational_axes, ACCEPTED_ROTATIONAL_AXES)

    def test_setattr(self) -> ...:
        """Test setting the attributes."""
        with self.assertRaises(AttributeError):
            self.settings.accepted_commands = 'test'

    def test_get_existing_key(self) -> ...:
        """Test getting an existing key."""
        self.assertEqual(self.settings.get('PIA13.DEFAULT', 'steps_per_um'), 50)

    def test_get_non_existing_key(self) -> ...:
        """Test getting a non-existing key."""
        with self.assertRaises(KeyError):
            self.assertEqual(self.settings.get('PIA.Z', 'test'), None)

    def test_get_existing_key_with_default(self) -> ...:
        """Test getting an existing key with a default value."""
        self.assertEqual(self.settings.get('SAMPLEHOLDER', 'max_vel'), 25e3)

    def test_set_existing_key(self) -> ...:
        """Test setting an existing key."""
        self.settings.set('PIA13.Z', key='start_movement_mode', value='ABS')
        self.assertEqual(self.settings.get('PIA13.Z', 'start_movement_mode'), 'ABS')

    def test_set_non_existing_key(self) -> ...:
        """Test setting a non-existing key."""
        with self.assertRaises(KeyError):
            self.settings.set('PIA13.TEST', key='L', value=10)

    def test_set_existing_key_in_default(self) -> ...:
        """Test setting an existing key in the default section."""
        with self.assertRaises(KeyError):
            self.settings.set('PIA13.DEFAULT', key='L', value=10)

    def test_save(self) -> ...:
        """Test saving the settings."""
        self.settings.set('PIA13.Z', key='l', value=1)
        self.assertEqual(self.settings.get('PIA13.Z', 'l'), 1)
        self.settings.save('test.ini')

        # Check if the file exists
        self.assertTrue(os.path.isfile('.\\src\\stacking_setup\\components\\stacking_backend\\configs\\test.ini'))
        new_settings = Settings('test.ini')

        # Delete the file
        os.remove('.\\src\\stacking_setup\\components\\stacking_backend\\configs\\test.ini')

        # Check if the value is correct
        self.assertEqual(new_settings.get('PIA13.Z', 'l'), 1)


if __name__ == '__main__':
    # Run all the tests in this file
    unittest.main()
