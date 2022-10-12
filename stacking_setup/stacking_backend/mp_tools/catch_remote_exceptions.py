import sys
import traceback
import functools


def catch_remote_exceptions(wrapped_function):
    """
    Catch and propagate the remote exeptions.
    https://stackoverflow.com/questions/6126007/python-getting-a-traceback
    """

    @functools.wraps(wrapped_function)
    def new_function(*args, **kwargs):
        try:
            return wrapped_function(*args, **kwargs)

        except:
            raise Exception(
                "".join(traceback.format_exception(*sys.exc_info())))

    return new_function


if __name__ == '__main__':
    from time import sleep
    import multiprocessing

    # Usage example
    class ProcessLocker(object):
        @catch_remote_exceptions
        def __init__(self):
            super().__init__()

        @catch_remote_exceptions
        def create_process_locks(self, total_processes):
            self.process_locks = []
            # ...

    @catch_remote_exceptions
    def funct_0():
        sleep(1)
        funct_1()
        return

    @catch_remote_exceptions
    def funct_1():
        i = 5 + 'a'

    funct_0()
    process = multiprocessing.Process(target=funct_0)
    process.start()