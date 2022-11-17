import threading
from src.stacking_setup.stacking_middleware.pipeline_connection import PipelineConnection as Connection
from multiprocessing import Pipe
import time


def handhake_backend(conn):
    conn.handshake()
    print('Backend {}'.format(conn._handshake_complete))


if __name__ == "__main__":
    pcon, ccon = Pipe()
    backend_thread = threading.Thread(target=handhake_backend, args=(Connection(ccon, 'BACKEND'),))
    backend_thread.setDaemon(True)

    time.sleep(1)
    front_conn = Connection(pcon, "FRONDEND")
    backend_thread.start()
    front_conn.handshake()
    print('Frondend {}'.format(front_conn._handshake_complete))