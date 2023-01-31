import os
from threading import Thread, Lock, Event
from time import sleep


def check_for_response(con, lock: Lock, event: Event) -> ...:
    """
    Check for a response from the pipe connection.

    This function is used in a thread to print responses from the pipe connection
    without having to wait for a loop to finish.

    Parameters:
    -----------
    con : Child class of BaseConnector
        The connection to check for a response from.
    lock : threading.Lock
        The lock to use to prevent multiple threads from using the pipe at the same time.
    event : threading.Event
        The event to check if the thread should be closed.

    Returns:
    --------
    None.

    """
    response = None

    while not event.is_set():
        sleep(0.1)  # Sleep 100ms to prevent the thread from hogging the CPU

        if con.is_connected and con.message_waiting():
            lock.acquire()
            response = con.receive()
            lock.release()
        else:
            continue

        if response is not None:
            if isinstance(response, list):
                for msg in response:
                    print(msg.__dict__)
            else:
                print(response)

            print("\n >>>")


def main(connector) -> ...:
    """
    Start the TUI and the backend.

    Parameters:
    -----------
    connector : Child class of BaseConnector
        The connector to use to communicate with the backend.

    Returns:
    --------
    None

    """
    # Print the welcome dialog
    os.system("cls")
    print("Welcome to the Stacking TUI!")
    print(
        "Type exit() to exit the program and type help() for a list of possible commands."
    )

    print("\n Performing handshake with backend...")
    connector.handshake()

    # Create the response thread as a deamon so it will close when the program closes
    shutdown_event = Event()
    res_thread = Thread(
        target=check_for_response,
        args=(
            connector,
            Lock(),
            shutdown_event,
        ),
        daemon=True,
    )
    res_thread.start()

    # Start the main loop
    while True:
        response = input(">>> ")
        if response.lower() == "help()":
            print("\nhelp() - Print this help dialog")
            print("exit() - Exit the program")
            print("G0 - Make a linear move")
            print("G1 - Make a rotational move")
            print("G28 - Home all axes")
            print("G90 - Set absolute positioning")
            print("G91 - Set relative positioning")
            print("M0 - Stop all motion")
        elif response.lower() == "exit()":
            # Send the sentinel command to the backend to close the program
            connector.send_sentinel()
            connector.disconnect()
            break
        else:
            # Send the command to the rpi and wait for the response
            connector.send(response)

    # Close the response thread and connector
    shutdown_event.set()
    res_thread.join()
    connector.disconnect()

    print("\n\nThank you for using the Stacking TUI! See you next time.")
