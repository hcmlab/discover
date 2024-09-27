""" Utility modules for NOVA-Server Threads

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    13.09.2023
"""

import ctypes
import threading

status_lock = threading.Lock()
ml_lock = threading.Lock()
jc_lock = threading.Lock()
job_counter = 0

THREADS = {}


def ml_thread_wrapper(func):
    """
    Executing the function in a mutex protected thread for asynchronous execution of long-running ml tasks.
    The thread waits with execution unit the status_lock is released. To do any initialization before the thread starts acquire the status lock before creating the thread.
    :param func:
    :return: The thread
    """

    def wrapper(*args, **kwargs):
        global job_counter

        def lock(*args, **kwargs):
            try:
                # Only one ml thread can be active at the same time
                ml_lock.acquire()
                func(*args, **kwargs)
            finally:
                ml_lock.release()

        jc_lock.acquire()
        job_id = str(job_counter)
        job_counter += 1
        jc_lock.release()

        t = BackendThread(target=lock, name=job_id, args=args, kwargs=kwargs)
        return t

    return wrapper


def status_thread_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            status_lock.acquire()
            return func(*args, **kwargs)
        finally:
            status_lock.release()

    return wrapper


class BackendThread(threading.Thread):
    def __init__(self, target, name, args, kwargs):
        threading.Thread.__init__(
            self, target=target, name=name, args=args, kwargs=kwargs
        )

    def get_id(self):
        if hasattr(self, "_thread_id"):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            thread_id, ctypes.py_object(SystemExit)
        )
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
