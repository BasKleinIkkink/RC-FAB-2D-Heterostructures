import traceback
import functools
import sys


def catch_remote_exceptions(wrapped_function : callable) -> callable:
    """
    Catch and propagate the remote exeptions.

    The function is a wrapper around the function to catch the remote exceptions.
    This is usefull for the multiprocessing module, because the exceptions can't be pickled.

    https://stackoverflow.com/questions/6126007/python-getting-a-traceback

    Parameters
    ----------
    wrapped_function : function
        The function to wrap.

    Raises
    ------
    Exception
        The remote exception that should be send to the main process.

    Returns
    -------
    function
        The wrapped function.
    """

    @functools.wraps(wrapped_function)
    def new_function(*args, **kwargs):
        try:
            return wrapped_function(*args, **kwargs)

        except:
            raise Exception(
                "".join(traceback.format_exception(*sys.exc_info())))

    return new_function