import unittest
from unittest.mock import MagicMock, patch
import multiprocessing as mp
import configparser
#Following lines are for assigning parent directory dynamically.
import sys, os
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)
from src.stacking_setup.stacking_middleware.pipeline_connection import PipelineConnection


class TestPipeLineConnection(unittest.TestCase):


    def setUp(self):
        self.to_proc, self.from_proc = mp.Pipe()
        self.settings = configparser.ConfigParser()

    def tearDown(self):
        self.to_proc.close()
        self.from_proc.close()

    # Open the pipe
    @patch.object(PipelineConnection, 'handshake', return_value=True)
    def test_open_pipe(self, connector_mock):
        parent_pipe = PipelineConnection(self.to_proc, 'FRONDEND', self.settings)
        child_pipe = PipelineConnection(self.from_proc, 'BACKEND', self.settings)

    # Send and reiceive a message
    @patch.object(PipelineConnection, 'handshake', return_value=True)
    def test_send_and_receive_a_message(self, connector_mock):
        parent_pipe = PipelineConnection(self.to_proc, 'FRONDEND', self.settings)
        child_pipe = PipelineConnection(self.from_proc, 'BACKEND', self.settings)

        parent_pipe.send('Hello World')
        self.assertEqual(child_pipe.receive(), ['Hello World'])

    # Test the message waiting function
    @patch.object(PipelineConnection, 'handshake', return_value=True)
    def test_message_waiting(self, connector_mock):
        parent_pipe = PipelineConnection(self.to_proc, 'FRONDEND', self.settings)
        child_pipe = PipelineConnection(self.from_proc, 'BACKEND', self.settings)

        parent_pipe.send('Hello World')
        self.assertTrue(child_pipe.message_waiting())
        self.assertFalse(parent_pipe.message_waiting())
        _ = child_pipe.receive()

        child_pipe.send('Hello World')
        self.assertTrue(parent_pipe.message_waiting())
        self.assertFalse(child_pipe.message_waiting())

    # Check if the pipe is open
    @patch.object(PipelineConnection, 'handshake', return_value=True)
    def test_is_connected(self, connector_mock):
        parent_pipe = PipelineConnection(self.to_proc, 'FRONDEND', self.settings)
        child_pipe = PipelineConnection(self.from_proc, 'BACKEND', self.settings)

        self.assertTrue(parent_pipe.is_connected)
        self.assertTrue(child_pipe.is_connected)

        # Close the pipe on one side
        parent_pipe.disconnect()

        self.assertFalse(parent_pipe.is_connected)
        self.assertFalse(child_pipe.is_connected)

        # Close on both sides
        child_pipe.disconnect()

        self.assertFalse(parent_pipe.is_connected)
        self.assertFalse(child_pipe.is_connected)

if __name__ == '__main__':
    unittest.main()