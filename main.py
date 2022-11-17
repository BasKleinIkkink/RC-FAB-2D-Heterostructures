from src.stacking_setup.stacking_backend.stacking_setup import StackingSetupBackend
from src.stacking_setup.stacking_middleware.pipeline_connection import PipelineConnection as Connection
from src.stacking_setup.stacking_frondend.gui.main import main as ui_main
from multiprocessing import Pipe


if __name__ == '__main__':
    # Create the chosen middleware method
    par_con, ch_con = Pipe()
    #backend = StackingSetupBackend(Connection(par_con, "BACKEND"))
    #backend.start_backend()

    # Run the tui main function
    ui_main(Connection(ch_con, "FRONDEND"))