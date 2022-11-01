"""This file contains the infinite loop that runs the program."""
#from ...stacking_middleware.serial_connection import SerialConnection
from configparser import ConfigParser
import os
from threading import Thread, Lock, Event
from time import sleep


def check_for_response(con, lock, event):
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

    Returns:
    --------
    None.

    """
    response = None
    
    while not event.is_set():
        lock.acquire()
        if con.is_connected:
            response = con.receive()
        lock.release()

        if response is not None:
            if isinstance(response, list):
                for msg in response:
                    for key, value in msg.summary().items():
                        print(key, value)
            else:
                print(response)

        sleep(0.1)  # Sleep 100ms to prevent the thread from hogging the CPU


def main(connector):
    """
    Start the TUI and the backend.

    Returns:
    --------
    None

    """
    # Print the welcome dialog
    os.system('cls')
    print("Welcome to the Stacking TUI!")
    print("Type exit() to exit the program and type help() for a list of possible commands.")

    # Create the response thread as a deamon so it will close when the program closes
    shutdown_event = Event()
    res_thread = Thread(target=check_for_response, args=(connector, Lock(), shutdown_event,), daemon=True)
    res_thread.start()

    # Start the main loop
    while True:
        response = input(">>> ")
        if response.lower() == "help()":
            print("\nhelp() - Print this help dialog")
            print("exit() - Exit the program")
            print("G0 - Make a linaer move")
            print("G1 - Make a rotational move")
            print("G28 - Home all axes")
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
