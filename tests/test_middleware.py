import unittest
from unittest.mock import MagicMock, patch
import multiprocessing as mp
#Following lines are for assigning parent directory dynamically.
import sys, os
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)
from stacking_setup.stacking_middleware.pipeline_connection import PipelineConnection


class TestPipeLineConnection(unittest.TestCase):


    def setUp(self):
        self.to_proc, self.from_proc = mp.Pipe()

    def tearDown(self):
        self.to_proc.close()
        self.from_proc.close()

    # Open the pipe
    def test_open_pipe(self):
        parent_pipe = PipelineConnection(self.to_proc, 'parent')
        child_pipe = PipelineConnection(self.from_proc, 'child')

        self.assertTrue(parent_pipe.is_connected)
        self.assertTrue(child_pipe.is_connected)

    # Send and reiceive a message
    def test_send_and_receive_a_message(self):
        parent_pipe = PipelineConnection(self.to_proc, 'parent')
        child_pipe = PipelineConnection(self.from_proc, 'child')

        parent_pipe.send('Hello World')
        self.assertEqual(child_pipe.receive(), ['Hello World'])

    # Test the message waiting function
    def test_message_waiting(self):
        parent_pipe = PipelineConnection(self.to_proc, 'parent')
        child_pipe = PipelineConnection(self.from_proc, 'child')

        parent_pipe.send('Hello World')
        self.assertTrue(child_pipe.message_waiting())
        self.assertFalse(parent_pipe.message_waiting())

"""
    # Check if the pipe is open
    def test_is_connected(self):
        parent_pipe = PipelineConnection(self.to_proc, 'parent')
        child_pipe = PipelineConnection(self.from_proc, 'child')

        self.assertTrue(parent_pipe.is_connected)
        self.assertTrue(child_pipe.is_connected)

        # Close the pipe
        parent_pipe.disconnect()
        child_pipe.disconnect()

        self.assertFalse(parent_pipe.is_connected)
        self.assertFalse(child_pipe.is_connected)
"""