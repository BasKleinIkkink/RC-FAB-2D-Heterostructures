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

    # Open the pipe
    def test_open_pipe(self):
        parent_pipe = PipelineConnection(self.to_proc, 'parent')
        child_pipe = PipelineConnection(self.from_proc, 'child')

        self.assertTrue(parent_pipe.is_connected)
        self.assertTrue(child_pipe.is_connected)

    # Send a message

    # Send a message with echo

    # Wait for a message

    # Receive a message

    # Check if the pipe is open