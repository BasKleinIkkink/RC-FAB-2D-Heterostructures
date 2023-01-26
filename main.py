# Import the backend
from src.stacking_setup.components.stacking_backend.stacking_setup import StackingSetupBackend

# Import the connection method
from multiprocessing import Pipe  # Only needed for the pipe connection
from src.stacking_setup.components.stacking_middleware.pipeline_connection import PipelineConnection as Connection

# Import the ui
# from src.stacking_setup.components.stacking_frondend.gui.main import main as ui_main
from src.stacking_setup.components.stacking_frondend.tui.main import main as ui_main


if __name__ == '__main__':
    # Create the chosen middleware method and start the backend
    par_con, ch_con = Pipe()
    backend = StackingSetupBackend(Connection(par_con, "BACKEND"))
    backend.start_backend()

    # Run the ui main function
    ui_main(Connection(ch_con, "FRONTEND"))