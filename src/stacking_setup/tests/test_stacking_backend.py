import unittest
from unittest.mock import MagicMock, patch, PropertyMock, Mock
import multiprocessing as mp
import configparser

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


def mock_pia13(id):
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


def mock_prmtz8(id):
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


def mock_sample_holder(id):
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


def _get_hardware_mocks():
    """
    Create mock hardware for the backend to control.

    Returns:
    --------
    hardware : dict
        A tuple of mock hardware objects (MagicMocks).

    """
    return [mock_pia13('X'),
            mock_pia13('Y'),
            mock_pia13('Z'),
            mock_prmtz8('L'),
            mock_sample_holder('K'),]


class TestControlBackend(unittest.TestCase):

    def setUp(self):
        self.to_main, self.to_proc = mp.Pipe()
        self.settings = configparser.ConfigParser()
        
    def tearDown(self):
        # Close the pipes
        self.to_main.close()
        self.to_proc.close()
        
    # Test initiate hardware
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_connect_hardware(self, _init_all_hardware_mock):
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())

        # Check if the right functions were called.
        _init_all_hardware_mock.assert_called_once()

        for i in stack._hardware:
            try:
                i.connect.assert_called_once()
            except AssertionError as e:
                raise AssertionError('{} was not connected : {}'.format(i.id, e))

    # Test disconnect hardware
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_disconnect_hardware(self, _init_all_hardware_mock):
        # Test the initiate hardware function.
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        stack._disconnect_all_hardware()

        for i in stack._hardware:
            try:
                i.disconnect.assert_called_once()
            except AssertionError as e:
                raise AssertionError('{} was not disconnected : {}'.format(i.id, e))

    # Test emergency stop
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_emergency_stop(self, _init_all_hardware_mock):
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        stack._emergency_stop()

        # Check if the emergency stop flag was set.
        self.assertTrue(stack._emergency_stop_event.is_set())

    # Test the echo function
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_echo(self, _init_all_hardware_mock):
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        
        def test_function(dummy1):
            return 0, dummy1

        def test_function2(dummy1=None):
            return 0, dummy1
        
        stack._echo(func=test_function, command_id='test', command={'X': 1})

        # Check if the right message was sent.
        msg = {'X': 1}
        exit_code = 0
        while stack._execution_q.empty():
            continue
        pipe_msg = stack._execution_q.get()
        self.assertIsInstance(pipe_msg, Message)
        self.assertEqual(pipe_msg.msg, msg)
        self.assertEqual(pipe_msg.exit_code, exit_code)
        self.assertEqual(pipe_msg.command_id, 'test')
        self.assertEqual(pipe_msg.command, msg)

        stack._echo(func=test_function2, command_id='test2')

        while not stack._execution_q.empty():
            continue
        pipe_msg = stack._execution_q.get()
        self.assertEqual(pipe_msg.msg, '')
        self.assertEqual(pipe_msg.exit_code, exit_code)
        self.assertEqual(pipe_msg.command_id, 'test2')
        self.assertEqual(pipe_msg.command, None)
    
    # Test execute one command
    @patch.object(StackingSetupBackend, 'G0', return_value=(0, None))
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_execute_one_command(self, _init_all_hardware_mock, G0_mock):
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
                                        M105_mock, G1_mock, G0_mock):
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

    # Test call M105
    @patch.object(StackingSetupBackend, 'M105', return_value=(0, 10))
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_call_M105(self, _init_all_hardware_mock, M105_mock):
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())

        # When calling with no arguments the function should return the current value
        command = {'M105': {}}
        stack._execute_command(command)
        while stack._execution_q.empty():
            continue
        M105_mock.assert_called_once()

        # Get the message from the pipe
        stack._check_command_output()
        pipe_msg = self.to_proc.recv()
        self.assertEqual(pipe_msg.msg, '10')
        self.assertEqual(pipe_msg.exit_code, 0)

    # Test call M112
    @patch.object(StackingSetupBackend, 'M112', return_value=(0, None))
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_call_M112(self, _init_all_hardware_mock, M112_mock):
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

    def setUp(self):
        self.to_main, self.to_proc = mp.Pipe()
        self.settings = configparser.ConfigParser()
        
    def tearDown(self):
        # Close the pipes
        self.to_main.close()
        self.to_proc.close()

    # Test G0
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G0(self, _init_all_hardware_mock):
        self.assertTrue('G0' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
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
    def test_G0_not_supported(self, _init_all_hardware_mock):
        self.assertTrue('G0' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        movement = {'L': 1}
        exit_code, msg = stack.G0(movement)

        # Check if the right functions were called.
        stack._hardware[3].move_by.assert_called()

        # Check if the return code is right
        self.assertEqual(exit_code, 1)
        self.assertNotEqual(msg, None)

    # Test G0 non existing part
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G0_non_existing_part(self, _init_all_hardware_mock):
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

    # Test G1
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G1(self, _init_all_hardware_mock):
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

    # Test G1 with a part that does not support it
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G1_not_supported(self, _init_all_hardware_mock):
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

    # Test G1 non existing part
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G1_non_existing_part(self, _init_all_hardware_mock):
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

    # Test G28
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G28(self, _init_all_hardware_mock):
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

    # Test G90
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_G90andG91(self, _init_all_hardware_mock):
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

    def setUp(self):
        self.to_main, self.to_proc = mp.Pipe()
        self.settings = configparser.ConfigParser()
        
    def tearDown(self):
        # Close the pipes
        self.to_main.close()
        self.to_proc.close()

    # Test M92
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M92(self, _init_all_hardware_mock):
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
        self.assertEqual(msg, {'X': 1, 'Y': 1, 'Z': 1, 'L': 1})


    # Test M105
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M105(self, _init_all_hardware_mock):
        self.assertTrue('M105' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        exit_code, msg = stack.M105()

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertNotEqual(msg, None)
        self.assertEqual(msg, {'K': {'current' : 0, 'target' : 10}})

    # Test M112
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M112(self, _init_all_hardware_mock):
        self.assertTrue('M112' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        exit_code, msg = stack.M112()

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertEqual(msg, None)

        self.assertTrue(stack._emergency_stop_event.is_set())

    # Test M113
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M113(self, _init_all_hardware_mock):
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

        # Start the timer again and wait for the message to be sent
        #exit_code, msg = stack.M113({'S': 0.01})  # 10ms
        #in_waiting = self.to_proc.poll(timeout=1)
        #self.assertTrue(in_waiting)
    
    # Test M114	
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M114(self, _init_all_hardware_mock):
        self.assertTrue('M114' in ACCEPTED_COMMANDS)
        stack = StackingSetupBackend(self.to_main)
        stack.setup_backend(Settings())
        exit_code, msg = stack.M114()

        # Check if the return code is right
        self.assertEqual(exit_code, 0)
        self.assertNotEqual(msg, None)
        self.assertEqual(msg, {'X': 0, 'Y': 0, 'Z': 0, 'L': 0})

    # Test M154
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M154(self, _init_all_hardware_mock):
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

    # Test M155
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    def test_M155(self, _init_all_hardware_mock):
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

    # Test initiating the class
    def test_init(self):
        settings = Settings()
        
        self.assertTrue(isinstance(settings._config, type(configparser.ConfigParser())))

    # Test asking the attributes
    def test_getattr(self):
        settings = Settings()
        accepted_commands = settings.accepted_commands
        accepted_linear_axes = settings.accepted_linear_axes
        accepted_rotational_axes = settings.accepted_rotational_axes

        self.assertEqual(accepted_commands, ACCEPTED_COMMANDS)
        self.assertEqual(accepted_linear_axes, ACCEPTED_LINEAR_AXES)
        self.assertEqual(accepted_rotational_axes, ACCEPTED_ROTATIONAL_AXES)

    # Test setting an attribute
    def test_setattr(self):
        settings = Settings()
        with self.assertRaises(AttributeError):
            settings.accepted_commands = 'test'

    # Ask for existing key
    def test_get_existing_key(self):
        settings = Settings()
        self.assertEqual(settings.get('PIA13.DEFAULT', 'steps_per_um'), 50)

    # Ask for non-existing key
    def test_get_non_existing_key(self):
        settings = Settings()
        with self.assertRaises(KeyError):
            self.assertEqual(settings.get('PIA.Z', 'test'), None)

    # Ask for existing key with default
    def test_get_existing_key_with_default(self):
        settings = Settings()
        self.assertEqual(settings.get('SAMPLEHOLDER', 'max_vel'), 25e3)

    # Change a value
    def test_set_existing_key(self):
        settings = Settings()
        settings.set('PIA13.Z', key='start_movement_mode', value='ABS')
        self.assertEqual(settings.get('PIA13.Z', 'start_movement_mode'), 'ABS')

    # Change a value in a section that does not exist
    def test_set_non_existing_key(self):
        settings = Settings()
        with self.assertRaises(KeyError):
            settings.set('PIA13.TEST', key='L', value=10)

    # Change a value in the default section
    def test_set_existing_key_in_default(self):
        settings = Settings()
        with self.assertRaises(KeyError):
            settings.set('PIA13.DEFAULT', key='L', value=10)

    # Test the save function
    def test_save(self):
        settings = Settings()
        settings.set('PIA13.Z', key='l', value=1)
        self.assertEqual(settings.get('PIA13.Z', 'l'), 1)
        settings.save('test.ini')

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
