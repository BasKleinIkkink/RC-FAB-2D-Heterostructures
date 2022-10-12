from .stacking_setup import StackingSetup
from .gcode_parser import GCodeParser

import threading as tr


if __name__ == '__main__':
    # Setup
    ss = StackingSetup()
    ss.setup()

    # Parse GCode
    gp = GCodeParser(ss)
    gp.parse()

    # Start threads
    q = tr.Queue()
    tr.Thread(target=ss.start).start()
    tr.Thread(target=gp.start).start()

    # Wait for threads to finish
    ss.join()
    gp.join()

    # Cleanup
    ss.cleanup()