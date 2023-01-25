from typing import Union
import time
import threading as tr


class RepeatedTimer:
    """
    Class to repeat a task every x seconds.
    
    The class is a wrapper around a threading.Timer object and resets
    it every time the function is called.
    """

    def __init__(self, interval : Union[int, float], function : callable, 
            *args, **kwargs) -> ...:
        """
        Initiate the timer.
        
        Parameters
        ----------
        interval : float, int
            The interval in seconds.
        function : callable
            The function to repeat.

            .. note::
                Because the timer is reset and a new thread is started
                every time the function is called, the user should make
                sure that the function is thread safe and exits cleanly.

        args
            The arguments for the function.
        kwargs
            The keyword arguments for the function.
        """
        self._timer = None
        self._interval = interval
        self._function = function
        self._args = args
        self._kwargs = kwargs
        self._is_running = False
        self._next_call = time.time()
        self.start()

    @property
    def interval(self) -> Union[int, float]:
        """
        Get the interval.
        
        Returns
        -------
        float, int
            The interval in seconds.
        """
        return self._interval

    @property
    def is_running(self) -> bool:
        """
        Get the running status.
        
        Returns
        -------
        bool
            True if the timer is running, False otherwise.
        """
        return self._is_running

    @property
    def next_call(self) -> Union[int, float]:
        """
        Get the next call.
        
        Returns
        -------
        float, int
            The next call in seconds.
        """
        return self._next_call

    def _run(self) -> ...:
        """Run the function."""
        self._is_running = False
        self.start()
        self._function(*self._args, **self._kwargs)

    def start(self) -> ...:
        """Wait for the next run."""
        if not self.is_running:
            self._next_call += self._interval
            if self._timer is not None:
                del self._timer
            self._timer = tr.Timer(self.next_call - time.time(), self._run)
            self._timer.setDaemon(True)
            self._timer.start()
            self._is_running = True

    def stop(self) -> ...:
        """Stop the timer."""
        self._timer.cancel()
        self._timer.join()
        self._is_running = False