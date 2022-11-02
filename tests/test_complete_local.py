import multiprocessing as mp
from unittest.mock import patch
from test_stacking_backend import _get_hardware_mocks

#Following lines are for assigning parent directory dynamically.
import sys, os
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

from stacking_setup.stacking_frondend.tui.main import main as ui_main
from stacking_setup.stacking_middleware.pipeline_connection import PipelineConnection as Connector
from stacking_setup.stacking_backend.stacking_setup import StackingSetupBackend


if __name__ == '__main__':
    # Create the middleware connection
    parent_pipe, child_pipe = mp.Pipe()
    parent_conn = Connector(parent_pipe, 'PARENT')
    child_conn = Connector(child_pipe, 'CHILD')

    # Start the backend
    @patch.object(StackingSetupBackend, '_init_all_hardware', return_value=_get_hardware_mocks())
    @patch.object(StackingSetupBackend, '_init_emergency_breaker', return_value=None)
    def get_backend(emergency_moc, hardware_moc):
        # Method used to patch the backend for testing
        return StackingSetupBackend(child_conn)

    setup = get_backend()
    setup.start_backend()

    # Start the frondend  (blocks until exit)
    ui_main(parent_conn)

    # Clean up the mess
    setup.stop_backend()
    parent_conn.close()
    child_conn.close()

