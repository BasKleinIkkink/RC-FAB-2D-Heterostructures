# -*- coding: utf-8 -*-
"""
Copied and edited from:
https://stackoverflow.com/questions/55110733/python-multiprocessing-pipe-communication-between-processes
This code can be used to cummunicate over a multiprocessing pipeline
"""
from multiprocessing import Process, Pipe
from datetime import datetime

SENTINEL = 'SENTINEL'
EOM_CHAR = 'EOM'


def read_pipe(child_conn, feedback=False):
    """Read the data from the pipe."""
    result = []
    try:
        # Check if there is a message ready
        if child_conn.poll():
            for msg in iter(child_conn.recv, EOM_CHAR):
                result.append(msg)
        else:
            pass
    except OSError:
        # Catch the error if the other side closes unexpected
        close_pipe(child_conn)
        return result

    if feedback:
        # Send the reived conformation to parent
        write_pipe(child_conn, result)

    # Check if the closing request was given
    if SENTINEL in result:
        close_pipe(child_conn)
        # Put the SENTINEL command at the end
        result.append(result.pop(result.index(SENTINEL)))
        # print('RECEIVED SENTINEL COMMAND.')

    return result


def close_pipe(conn):
    """Close the pipe connection."""
    conn.close()


def write_pipe(conn, data):
    """Write the data to the pipe."""
    conn.send(data)
    conn.send(EOM_CHAR)


if __name__ == '__main__':
    # Example usage
    parent_conn, child_conn = Pipe()  # default is duplex!
    update_data_process = Process(target=read_pipe, args=(child_conn,
                                                          True,))
    update_data_process.daemon = True
    update_data_process.start()

    data = [i for i in range(5)]
    data.append(SENTINEL)
    write_pipe(parent_conn, data)

    for msg in iter(parent_conn.recv, EOM_CHAR):
        print(f'{datetime.now()} parent received {msg}')

    print(f'{datetime.now()} parent received SENTINEL')
    parent_conn.close()
    update_data_process.join()