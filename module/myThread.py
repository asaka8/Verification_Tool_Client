import time
import threading
import ctypes

class MyThread(threading.Thread):
    def __init__(self, target=None, name=None, args=(), kwargs=None, daemon=True):
        super(MyThread, self).__init__(target=target, args=args, name=None, kwargs=kwargs, daemon=daemon)
        self._name = str(name)

    def stop(self):
        if not self.is_alive():
            return
        exc = ctypes.py_object(SystemExit)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self.ident), exc)
        if res == 0:
            raise ValueError("invalid thread id")
        elif res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, None)
            raise SystemError("Thread is stopped")