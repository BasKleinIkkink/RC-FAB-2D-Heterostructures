import multiprocessing as mp
from .base_connector import BaseConnector
import errno
from time import sleep
from queue import Empty, Full


SENTINEL = 'SENTINEL'  # Sentinel command to close the pipe
EOM_CHAR = 'EOM'  # String indicating the end of a message over a pipe


class PipeCom():

    @staticmethod
    def close_pipe(conn):
        """
        Close the pipe connection.
        
        Parameters
        ----------
        conn : multiprocessing.connection.Connection
            The connection to close.

        Returns
        -------
        None.

        """
        conn.close()

    @classmethod
    def read_pipe(cls, child_conn, feedback=False):
        """
        Read the data from the pipe.
        
        Parameters
        ----------
        child_conn : multiprocessing.connection.Connection
            The connection to read from.
        n : int, optional
            The number of messages to read. The default is 0, read all messages.
        feedback : bool, optional
            If True, the received data will be sent back to the parent process.
            The default is False.

        Returns
        -------
        result : list
            The received data. I a sentinel command was received, it will be the
            last element in the list.

        """
        result = []
        try:
            # Check if there is a message ready
            if child_conn.poll(): 
                for msg in iter(child_conn.recv, EOM_CHAR):
                    result.append(msg)
            else:
                pass
        except IOError as e:
            # Catch the error if the other side closes unexpected
            if e.errno == errno.EPIPE:
                cls.close_pipe(child_conn)
                return result
            else:
                # Raise the error, cause is unknown
                raise IOError(e)

        if feedback:
            # Echo the reived conformation to parent
            cls.write_pipe(child_conn, result)

        # Check if the closing request was given
        if SENTINEL in result:
            cls.close_pipe(child_conn)
            # Put the SENTINEL command at the end
            result.append(result.pop(result.index(SENTINEL)))
        return result

    @staticmethod
    def write_pipe(conn, data):
        """
        Write the data to the pipe.
        
        Parameters
        ----------
        conn : multiprocessing.connection.Connection
            The connection to write to.
        data : list
            The data to write to the pipe.
        
        Returns
        -------
        None.

        """
        conn.send(data)
        conn.send(EOM_CHAR)

    @staticmethod
    def pipe_is_open(conn):
        """
        Check if the pipe is open.
        
        Parameters
        ----------
        conn : multiprocessing.connection.Connection
            The connection to check.

        Returns
        -------
        bool
            True if the pipe is open, False otherwise.

        """
        # Essentialy checks if a message is waiting.
        state = conn.poll()
        if state:
            # Message is waiting so the pipe has to be open
            return True
        else:
            # No message waiting, check if the pipe is closed
            try:
                # Try to read a message, if the pipe is open returns EMPTY error
                conn.recv()
            except EOFError:
                # Pipe is closed
                return False
            except Empty:
                # Pipe is open
                return True
            finally:
                raise IOError('Unknown error while checking pipe state')


class PipelineConnection(BaseConnector):
    """
    Connection method using a multiprocessing pipe.
    
    This connection method is most suited for when the frond and backend are running
    on the same machine. It is not suited for communication over a network.
    """
    _connection_method = "PIPELINE"

    def __init__(self, connection, role):
        self._connection = connection
        self._role = role
        
        # A pipeline is local so no handshake is needed

    @property
    def is_connected(self):
        return PipeCom.pipe_is_open(self._connection)

    def _load_settings(self):
        # No specific settings are needed for this communication method
        pass

    def connect(self):
        # The pipe is connected on init and cannot reconnect
        pass

    def disconnect(self):
        PipeCom.close_pipe(self._connection)

    

    def send(self, data):
        PipeCom.write_pipe(self._connection, data)

    def message_waiting(self):
        return self._connection.poll()

    def receive(self):
        # Check if a message is waiting
        if not self._connection.poll():
            return None
        return PipeCom.read_pipe(self._connection)

    def handshake(self):
        self.send('Hello there.')

        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            res = self.receive()
            if len(res) == 0:
                attempts += 1
                sleep(0.1)
            elif res[0] == 'Hello there general Kenobi.':
                self._handshake_complete = True
                return True

        self._handshake_complete = False
        return False

    