import sys
import time
import traceback

from os.path import basename
from inspect import getframeinfo, signature
from functools import wraps, partial
from typing import Tuple, List
from PIL import Image
from PyQt5.QtGui import QColor, QPixmap, QPainter, QPen
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QWidget, QWidgetAction

__all__ = ['debugLocal', 'lasyproperty', 'enter_hook', 'calltag',
           'ncalls', 'ntime', 'catch_errors', 'qmixin']

def calltag(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('call %s', func.__name__)
        res = func(*args, **kwargs)
        return res
    return wrapper

def qmixin(cls):

    def setStrWidth(self, widget, st: str):
        width = widget.fontMetrics().width(st)
        widget.setFixedWidth(width)

    def addColor(self, pix: QPixmap, color=QColor(50, 50, 50, 50)) -> QPixmap:  # 给图片添加遮罩
        rect = QRect(0, 0, pix.width(), pix.height())
        new_pixmap = QPixmap(pix)
        painter = QPainter()
        painter.begin(new_pixmap)
        pen = QPen()
        pen.setBrush(QColor(color))
        painter.setPen(pen)
        painter.fillRect(rect, QColor(color))
        painter.end()
        return new_pixmap

    def validImage(self, file_path) -> bool:
        valid = True
        try:
            Image.open(file_path).verify()
        except:
            valid = False
        return valid

    cls.setStrWidth = setStrWidth

    cls.addColor = addColor
    
    cls.validImage = validImage

    return cls


def ncalls(func):
    ncalls = 0

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal ncalls
        ncalls += 1
        return func(*args, **kwargs)

    def clear():
        nonlocal ncalls
        ncalls = 0

    wrapper.ncalls = lambda: ncalls
    wrapper.clear = lambda: clear()
    return wrapper


def ntime(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        s1 = time.time()
        res = func(*args, **kwargs)
        print(func.__name__, 'spend: %s' % time.time() - s1)
        return res
    return wrapper


def catch_errors(func=None, *, exceptions: Tuple[Exception] = None):
    if func is None:
        return partial(catch_errors, exceptions=exceptions)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except exceptions if exceptions else Exception:
            traceback.print_exc()
            return None
    return wrapper


def debugLocal(func=None, *, excepts: List[str]=None, base:bool=False):
    if func is None:
        return partial(debugLocal, excepts=excepts, base=base)

    @wraps(func)
    def wrapper(*args, **kwargs):
        def tracer(frame, event, arg):
            if event == 'return':
                sig = signature(func)
                args = sig.parameters.copy().keys()
                func_name = frame.f_code.co_name
                call = getframeinfo(frame.f_back.f_back)
                if call is not None:
                    context = call[3][0].strip()
                    file_name = basename(call[0]) if base else call[0]
                    file_no = call[1]
                    print('`%s` at %s file_no:%s' %
                          (context, file_name, file_no))
                print(f'Debug `{func_name}`locals start')
                local = frame.f_locals.copy()

                for key in reversed(list(local.keys())):
                    if excepts:
                        if not key in excepts:
                            print(
                                key + f': {type(local[key])} =', local[key])
                    else:
                        print(key + f': {type(local[key])} =', local[key])
                print(f'Debug `{func_name}` locals over')

        sys.setprofile(tracer)
        try:
            res = func(*args, **kwargs)
        finally:
            sys.setprofile(None)
        return res

    return wrapper


class lasyproperty(object):
    def __init__(self, func):
        # self.func = wraps(self)(func)
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self.func(instance)
        instance.__dict__[self.func.__name__] = value
        return value


class ValidImageMixin:

    def validImage(self, file_path: str) -> bool:
        valid = True
        try:
            Image.open(file_path).verify()
        except:
            valid = False
        return valid

from types import MethodType

def enter_hook(widget: QWidget=None, widgets: List[QWidget]=None):

    def enterEvent(self, event):
        super(self.__class__, self).enterEvent(event)
        self.setCursor(Qt.ArrowCursor)

    if widgets is None:
        widget.enterEvent = MethodType(enterEvent, widget)
    else:
        for wid in widgets:
            wid.enterEvent = MethodType(enterEvent, wid)
