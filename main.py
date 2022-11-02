from stacking_setup.stacking_backend.stacking_setup import StackingSetupBackend
from stacking_setup.stacking_middleware.pipeline_connection import PipelineConnection as Connection
from stacking_setup.stacking_frondend.tui.main import main as ui_main
from multiprocessing import Pipe


if __name__ == '__main__':
    # Connect the back and frondend with the chosen middleware method
    par_con, ch_con = Pipe()
    backend = StackingSetupBackend(Connection(par_con, "BACKEND"))

    # Start the backend
    backend.start_backend()

    # Run the tui main function
    ui_main(Connection(ch_con, "FRONDEND"))