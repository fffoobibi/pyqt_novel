import time
from queue import Queue
from PyQt5.QtCore import QThread, pyqtSignal
from typing import Callable, Any

__all__ = ['getBackThread']


class BackThread(QThread):  # 耗时任务线程

    done_sig = pyqtSignal(str, object)

    _instance = None

    def __new__(cls, **kwargs):
        if cls._instance is None:
            instance = super().__new__(cls)
            instance.task_q = Queue()
            instance.result_q = Queue()
            cls._instance = instance
        return cls._instance

    def __init__(self, **kwargs):
        super().__init__()
        self.debug = kwargs.pop('debug', False)

    def add_task(self, func, args=(), kwargs={}, callback: Callable = None, errback: Callable = None) -> None:
        self.task_q.put((func, args, kwargs, callback, errback))

    def getResult(self, func, args=(), kwargs={}) -> Any:
        self.add_task(func, args, kwargs)
        res = self.result_q.get()
        return res

    def run(self) -> None:
        while True:
            get_value = self.task_q.get()
            if get_value == 'stop':
                break
            else:
                func, args, kwargs, callback, errback = get_value
                res = None
                try:
                    s = time.time()
                    res = func(*args, **kwargs)
                    ends = time.time() - s
                    if self.debug:
                        print(f'{func.__name__} cost: {ends}')
                    if callback:
                        callback(res)
                except Exception as e:
                    if errback:
                        errback(e)
                self.result_q.put(res)
                self.done_sig.emit(func.__name__, res)

    def stop(self) -> None:
        self.task_q.put('stop')


def getBackThread(**kwargs) -> BackThread:
    t = BackThread(**kwargs)
    return t
