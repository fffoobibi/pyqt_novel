import math
import time
import httpx
import pprint
import subprocess
import logging
import traceback
import jinja2
import asyncio

from enum import IntEnum
from textwrap import fill
from random import sample
from copy import deepcopy
from abc import abstractmethod
from collections.abc import MutableSequence
from functools import partial, partialmethod
from collections import deque
from queue import Queue
from typing import Any, Callable, List, Optional, Sequence, Tuple, Union, Iterable

from PIL import Image
from scrapy.http import HtmlResponse
from jinja2 import FileSystemLoader, Environment

from PyQt5.QtWidgets import (
    QColorDialog, QStyle, QTextBrowser, QWidget, QApplication, QPushButton, QLabel,
    QMenu, QListWidget, QListWidgetItem, QFrame, QGraphicsOpacityEffect,
    QListView, QAbstractItemView, QLineEdit, QVBoxLayout, QCheckBox, QToolTip,
    QComboBox, QHBoxLayout, QPlainTextEdit, QShortcut, QCompleter, QAction,
    QMessageBox, QStackedWidget, QWidgetAction)

from PyQt5.QtCore import (QFile, QObject, QSemaphore, QTextStream, QThread, Qt,
                          QFileInfo, QDir, pyqtSignal, QMimeData, QSize,
                          QPropertyAnimation, QUrl, QPoint, QRect, QEvent,
                          QRectF, QRegExp, QRegularExpression,
                          QRegularExpressionMatchIterator, QTimer,
                          QSortFilterProxyModel, pyqtSlot, qRound)

from PyQt5.QtGui import (QIntValidator, QPixmap, QIcon, QMouseEvent, QCursor,
                         QDragEnterEvent, QDragMoveEvent, QDropEvent, QDrag,
                         QDesktopServices, QPen, QColor, QPainter,
                         QFontMetrics, QMovie, QPalette, QBitmap, QPainterPath,
                         QFont, QSyntaxHighlighter, QTextCharFormat,
                         QTextDocument, QStandardItem, QStandardItemModel,
                         QIcon, QTextCursor, QWheelEvent)

from PyQt5.QtSvg import QSvgRenderer

from .magic import lasyproperty
from .common_srcs import CommonPixmaps, StyleSheets, COLORS
from .titlebar import TitleBar

from crawl_novel import (InfoObj, InfTools, LatestRead, ChapterDownloader,
                         DownStatus, Markup, get_spider_byname)


class BaseFilterListView(QListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_model = QStandardItemModel(self)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setSpacing(0)
        self.setDragEnabled(False)
        self.setEnabled(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # ????????????
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)  # ??????
        self.setUniformItemSizes(True)  # ???????????????????????????
        self.setViewMode(QListView.ListMode)  # ????????????
        self.setMovement(QListView.Static)
        self.setResizeMode(QListView.Adjust)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.data_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setDynamicSortFilter(False)  # ??????????????????
        self.proxy_model.setFilterKeyColumn(0)
        self.proxy_model.setFilterRole(Qt.UserRole)  # ??????????????????
        self.setModel(self.proxy_model)
        self.__filter_status = 0  # 0 ?????????, 1?????????, 2????????????

    def insertItem(self,
                   index: int,
                   filter_value: str,
                   widget: QWidget,
                   meta: dict = None) -> None:
        item = QStandardItem()
        item.setSizeHint(QSize(60, widget.height()))
        item.setData(filter_value, Qt.UserRole)
        self.data_model.insertRow(index, item)
        true_index = self.data_model.indexFromItem(item)
        widget.model_index = true_index.row()
        item.setData(true_index, Qt.UserRole + 1)
        for e_index, key in enumerate(meta.keys(), 2):
            item.setData(meta[key], Qt.UserRole + e_index)
        proxy_index = self.proxy_model.mapFromSource(true_index)
        self.setIndexWidget(proxy_index, widget)
        for item_index in range(self.filterCount()):
            item_widget = self.itemWidget(item_index)
            item_widget.model_index = item_index

    appendTop = partialmethod(insertItem, 0)

    def appendItem(self,
                   filter_value: str,
                   widget: QWidget,
                   meta: dict = None) -> None:
        item = QStandardItem()
        item.setSizeHint(QSize(60, widget.height()))
        item.setData(filter_value, Qt.UserRole)
        self.data_model.appendRow(item)
        true_index = self.data_model.indexFromItem(item)
        widget.model_index = true_index.row()
        item.setData(true_index, Qt.UserRole + 1)
        for index, key in enumerate(meta.keys(), 2):
            item.setData(meta[key], Qt.UserRole + index)
        proxy_index = self.proxy_model.mapFromSource(true_index)
        self.setIndexWidget(proxy_index, widget)

    def itemWidget(self, proxy_index: int) -> QWidget:
        proxy_index = self.proxy_model.index(proxy_index, 0)
        widget = self.indexWidget(proxy_index)
        return widget

    def removeItem(self, true_index: int) -> None:
        self.data_model.removeRow(true_index)

    def clear(self) -> None:
        self.data_model.clear()

    def count(self) -> int:
        return self.data_model.rowCount()

    def filterCount(self) -> int:
        return self.proxy_model.rowCount()

    def filter(self, filter_value: str) -> None:
        if self.__filter_status in [0, 2]:
            self.__filter_status = 1
            pattern = filter_value
            if pattern:
                self.proxy_model.setFilterRegularExpression(pattern)
            else:
                self.proxy_model.setFilterRegularExpression(".*")

            for row in range(self.proxy_model.rowCount()):  # ????????????
                QApplication.processEvents()
                proxy_index = self.proxy_model.index(row, 0)
                true_index = self.proxy_model.mapToSource(proxy_index)
                item = self.data_model.item(true_index.row(), 0)
                create_widget = self._restoreItemWidget(item)
                create_widget.model_index = true_index.row()
                self.setIndexWidget(proxy_index, create_widget)
            self.__filter_status = 2

    def _restoreItemWidget(self, item: QStandardItem) -> QWidget:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"


class DownRecordFilterListView(BaseFilterListView):

    remove_sig = pyqtSignal(str)

    def removeItem(self, index: int) -> None:
        self.data_model.removeRow(index)
        self.remove_sig.emit("????????????")

    def _restoreItemWidget(self, item: QListWidgetItem) -> "_DownRecordWidget":
        inf = item.data(Qt.UserRole + 2)
        down_widget = _DownRecordWidget(inf, self)
        down_widget.model_index = item.data(Qt.UserRole + 1)
        return down_widget


class _DownRecordWidget(QWidget):
    def __init__(self, inf, listview: DownRecordFilterListView):
        super().__init__()
        self.list_view = listview
        self.model_index: int = None
        file_name = inf.novel_name + \
            f"[{inf.novel_site}]." + inf.novel_file_type
        file_path = QDir(inf.novel_save_path).absoluteFilePath(file_name)
        if inf.novel_chapter_urls:
            file_name = file_name + f" [{inf.novel_size}]"
        file_exists = QFileInfo(file_path).exists()
        if file_exists:
            info_txt = (inf.novel_file_size + "--" + inf.novel_site + "--" +
                        inf.novel_end_time)
        else:
            info_txt = "???????????????????????????" + "--" + inf.novel_site + "--" + inf.novel_end_time

        if inf.novel_file_type.lower() == "txt":
            icon = QPixmap(":/ico/txt_1205634_easyicon.net.svg")
        elif inf.novel_file_type.lower() in ["rar", "zip", "7z"]:
            icon = QPixmap(":/ico/zip_1205637_easyicon.net.svg")
        else:
            icon = QPixmap(":/ico/file_1205611_easyicon.net.svg")
        lay = QHBoxLayout(self)
        icon_label = QLabel()
        icon_label.setPixmap(icon)
        icon_button = QPushButton()
        icon_button.setIcon(
            QIcon(":/ico/folder-o.svg"
                  ) if file_exists else QIcon(":/ico/trash-o.svg"))
        icon_button.setStyleSheet("border:none")
        icon_button.setCursor(Qt.PointingHandCursor)
        icon_button.clicked.connect(lambda: self.openOrdelete(file_path))

        v_frame = QFrame()
        v_lay = QVBoxLayout()
        file_label = QLabel()
        info_label = QLabel()
        file_label.setText(file_name)
        info_label.setText(info_txt)
        v_lay.addWidget(file_label)
        v_lay.addWidget(info_label)
        v_frame.setLayout(v_lay)

        lay.addWidget(icon_label)
        lay.addWidget(v_frame)
        lay.addWidget(icon_button)
        lay.setStretch(0, 1)
        lay.setStretch(1, 100)
        lay.setStretch(2, 1)
        fm = file_label.fontMetrics()
        self.setFixedHeight(fm.height() * 6)
        self.inf = inf
        self.info_label = info_label
        self.icon_button = icon_button
        self.dft = self.styleSheet()
        self.file_label = file_label

    def updateMessage(self) -> None:
        inf = self.inf
        file_name = inf.novel_name + \
            f"[{inf.novel_site}]." + inf.novel_file_type
        file_path = QDir(inf.novel_save_path).absoluteFilePath(file_name)
        file_exists = QFileInfo(file_path).exists()
        if file_exists:
            info_txt = (inf.novel_file_size + "--" + inf.novel_site + "--" +
                        inf.novel_end_time)
            icon = QIcon(":/ico/folder-o.svg")
        else:
            info_txt = "???????????????????????????" + "--" + inf.novel_site + "--" + inf.novel_end_time
            icon = QIcon(":/ico/trash-o.svg")
        self.info_label.setText(info_txt)
        self.icon_button.setIcon(icon)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.updateMessage()

    def openOrdelete(self, file_path) -> None:
        if QFileInfo(file_path).exists():
            cmd = "explorer.exe /select,%s" % QDir.toNativeSeparators(
                file_path)
            try:
                subprocess.Popen(cmd)
            except:
                ...
        else:
            self.inf.remove()  # ??????
            self.list_view.removeItem(self.model_index)
            for proxy_index in range(self.list_view.filterCount()):
                widget = self.list_view.itemWidget(proxy_index)
                widget.model_index = proxy_index


class SearchRecordFilterView(BaseFilterListView):

    remove_sig = pyqtSignal(str)

    def _restoreItemWidget(self, item: QListWidgetItem) -> QWidget:
        logmsg = item.data(Qt.UserRole)
        index = item.data(Qt.UserRole + 1)
        logs = item.data(Qt.UserRole + 2)
        time = item.data(Qt.UserRole + 3)
        widget = _SearchRecordWidget(logmsg, self, logs)
        widget.model_index = index
        widget.datetime = time
        return widget

    def removeItem(self, true_index: int) -> None:
        self.data_model.removeRow(true_index)
        self.remove_sig.emit("????????????")


class _SearchRecordWidget(QWidget):
    def __init__(self, logmsg: str, listview: SearchRecordFilterView,
                 search_log: "_SearchLog"):
        super().__init__()
        self.model_index: int = None
        self.logmsg = logmsg
        self.listview = listview
        self.search_log = search_log
        icon_button = QPushButton()
        icon_button.setIcon(QIcon(":/ico/trash-o.svg"))
        icon_button.setStyleSheet("border:none")
        icon_button.setCursor(Qt.PointingHandCursor)
        icon_button.clicked.connect(self.remove)
        lay = QHBoxLayout(self)
        lay.addWidget(QLabel(logmsg), 100)
        lay.addWidget(icon_button, 0)
        self.setFixedHeight(55)

    def remove(self) -> None:
        true_index = self.model_index
        self.listview.removeItem(true_index)
        for proxy_index in range(self.listview.filterCount()):
            widget = self.listview.itemWidget(proxy_index)
            widget.model_index = proxy_index
        self.search_log.removeLogByMsg(self.datetime, self.logmsg)


class DragListWidgetEx(QListWidget):
    drag_item = None
    target_item = None
    drag_enabled = False
    drop_enabled = False
    spacing = 0
    switch_sig = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setResizeMode(QListView.Adjust)
        self.setMovement(QListView.Free)
        self.setSpacing(self.spacing)
        self._start_press = None

    def _radiusPixmap(self, radius: int, pixmap: QPixmap) -> None:  # ??????????????????
        bit = QBitmap(pixmap.size())
        bit.fill()  # ????????????
        painter = QPainter()
        painter.begin(bit)
        painter.setRenderHint(QPainter.Antialiasing, 0)  # ?????????
        painter.setRenderHint(QPainter.SmoothPixmapTransform, 0)  # ????????????
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.black)
        painter.drawRoundedRect(bit.rect(), radius, radius)
        painter.end()
        pixmap.setMask(bit)

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.drag_item = self.itemAt(event.pos())
            self._start_press = event.pos()
        elif event.buttons() & Qt.MidButton:
            self.switch_sig.emit()

    def mouseMoveEvent(self, event: QMouseEvent):  # ??????????????????
        if event.buttons() & Qt.LeftButton:
            if self.drag_enabled:
                if (event.pos() - self._start_press
                    ).manhattanLength() < QApplication.startDragDistance():
                    return
                if self.drag_item:
                    drag = QDrag(self)
                    data = QMimeData()
                    widget = self.itemWidget(self.drag_item)
                    data.setImageData(widget.getPreviewPixmap().toImage())
                    if widget:
                        pixmap = widget.grab()
                        self._radiusPixmap(20, pixmap)
                        drag.setPixmap(pixmap)
                    drag.setMimeData(data)
                    item_widget = self.itemWidget(self.drag_item).geometry()
                    drag.setHotSpot(
                        QPoint(event.x(),
                               event.y() - item_widget.y()))
                    action = drag.exec_(Qt.CopyAction | Qt.MoveAction
                                        | Qt.IgnoreAction)
                    if action == Qt.MoveAction:
                        self.dropActionMove(event)
                    elif action == Qt.CopyAction:
                        self.dropActionCopy(event)
                    elif action == Qt.IgnoreAction:
                        self.dropIgnore(event, data)

    def dropIgnore(self, event: QMouseEvent, data: QMimeData):  # ????????????
        pass

    def dropActionMove(self, event: QMouseEvent):  # ???????????????
        pass

    def dropActionCopy(self, event: QMouseEvent):  # ????????????
        pass

    def dragEnterEvent(self, event: QDragEnterEvent):
        event.accept()

    def dragMoveEvent(self, event: QDragMoveEvent):
        event.setDropAction(Qt.MoveAction)
        event.accept()

    def dropEvent(self, event: QDropEvent):
        if self.drop_enabled:
            self.dropPolicy(event)
            event.accept()
        else:
            event.ignore()

    def dropPolicy(self, event: QDropEvent) -> None:
        event.setDropAction(Qt.MoveAction)

    def addItemWidget(self, itemsize: QSize,
                      widget: QWidget) -> None:  # ??????item
        item = QListWidgetItem()
        item.setSizeHint(itemsize)
        self.addItem(item)
        self.setItemWidget(item, widget)

    def getItemWidget(self, index: int) -> QWidget:
        item = self.item(index)
        return self.itemWidget(item)

    def insertItemWidget(self, index: int, itemsize: QSize,
                         widget: QWidget) -> None:  # ??????item
        item = QListWidgetItem()
        item.setSizeHint(itemsize)
        self.insertItem(index, item)
        self.setItemWidget(item, widget)

    def takeItemWidget(self, index: int) -> None:  # ??????item
        item = self.item(index)
        self.removeItemWidget(item)
        self.takeItem(index)

    def swapItemWidget(self, first: int, second: int) -> None:  # ??????item
        f_widget = self.getItemWidget(first)
        s_widget = self.getItemWidget(second)
        self.insertItemWidget(first + 1, s_widget.size(), s_widget)
        self.insertItemWidget(second + 2, f_widget.size(), f_widget)
        self.takeItem(first)
        self.takeItem(second)

    def itemWidgets(self) -> List[QWidget]:
        res = []
        for count in range(self.count()):
            widget = self.getItemWidget(count)
            if widget:
                res.append(widget)
            else:
                res.append(None)
        return res


class TaskInfoLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.totel_content = None
        self.setContextMenuPolicy(Qt.NoContextMenu)

    def setText(self, a0: str, *, strwidth: int = None) -> None:
        if strwidth:
            value = self.fontMetrics().elidedText(a0, Qt.ElideMiddle, strwidth)
        else:
            value = self.fontMetrics().elidedText(a0, Qt.ElideMiddle,
                                                  self.width())
        self.total_content = a0
        super().setText(value)
        if self.objectName() == "label_14":
            self.setCursor(Qt.PointingHandCursor)
        elif self.objectName() == "label_15":
            self.setStyleSheet("text-decoration:underline")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setText(self.total_content)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            if self.objectName() == "label_14":
                QDesktopServices.openUrl(QUrl.fromLocalFile(
                    self.total_content))


class _SubscribeLinkThread(QThread):
    def __init__(self, loop):
        super().__init__()
        self._loop = loop

    def run(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()


class _SubscribeLinkObj(QObject):

    dft_headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }

    update_info_signal = pyqtSignal(InfoObj)

    fail_info_signal = pyqtSignal(InfoObj)

    fresh_down_signal = pyqtSignal()

    _first_init = False

    def __new__(cls, loop=None):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, loop=None):
        if self._first_init == False:
            super().__init__()
            self.asyc_loop = asyncio.new_event_loop(
            ) if loop is None else loop  # ????????????
            self.asyc_seam = asyncio.Semaphore(30,
                                               loop=self.asyc_loop)  # ???????????????
            self.link_thread = _SubscribeLinkThread(self.asyc_loop)
            self.link_thread.start()
            self.states = 0  # ????????????
            _SubscribeLinkObj._first_init = True

    def updateSubscribeLinks(self, subscribe_infos: Sequence[InfoObj]) -> bool:
        if self.states in [0, 2]:
            if not self.link_thread.isRunning():
                self.link_thread.start()
            asyncio.run_coroutine_threadsafe(
                self._updateChapterInfos(subscribe_infos), self.asyc_loop)
            return True
        return False

    async def _parse_request(self, headers: dict, info: InfoObj,
                             client: httpx.AsyncClient) -> Tuple[InfoObj]:
        try:
            async with self.asyc_seam:
                regiter_spider = get_spider_byname(info.novel_site)
                cookies = regiter_spider.subscribe_cookies()
                info.novel_fresh_state = 1
                resp = await client.get(info.novel_subs_url,
                                        headers=headers,
                                        cookies=cookies)
                resp.raise_for_status()
                encoding = resp.encoding if resp.encoding else "utf8"
                html_response = HtmlResponse(info.novel_subs_url,
                                             body=resp.text,
                                             encoding=encoding)
                updated_info = regiter_spider.subscribe_updateinfo(
                    html_response)
                return (
                    regiter_spider.process_subscribe_updateinfo(
                        info, updated_info),
                    info,
                )
        except Exception as e:
            info.novel_fresh_state = 3
            e.info = info
            raise e

    async def _updateChapterInfos(self, subscribe_infos: Sequence[InfoObj]):
        async with httpx.AsyncClient() as client:
            tasks = []
            for info in subscribe_infos:
                info.novel_fresh_state = 0
                sub_headers = info.novel_subs_headers
                headers = sub_headers if sub_headers else self.dft_headers
                task = asyncio.create_task(
                    self._parse_request(headers, info, client))
                tasks.append(task)
            if tasks:
                self.states = 1  # ?????????
                for future in asyncio.as_completed(tasks):
                    try:
                        update_info, old_info = await future
                        self.update_info_signal.emit(update_info)
                    except Exception as e:
                        info = e.info
                        self.fail_info_signal.emit(info)
                else:
                    self.states = 2  # ?????????
                    self.fresh_down_signal.emit()
        # self.asyc_loop.stop()


def get_subscribeLinkobj() -> _SubscribeLinkObj:
    return _SubscribeLinkObj()


class IconWidget(QWidget):

    IMG_DFT_SIZE = 180, 240

    SHOW_TIP = True  # ??????tooltip

    BKG_COLOR = COLORS.icon_hover_color  # ????????????

    MARGINS = 10, 10, 10, 10

    MAX_RETRY_COUNTS = 3  # ??????????????????

    RANDOM_COLORS = [
        "#CEFFCE",
        "#97CBFF",
        "#7D7DFF",
        "#D6D6AD",
        "#5CADAD",
        "#FF95CA",
        "#B15BFF",
        "#F1E1FF",
        "#5F9EA0",
        "#9ACD32",
    ]

    scaled: float = 0.6

    introutced_signal = pyqtSignal(InfoObj)

    down_signal = pyqtSignal(InfoObj)

    clicked_signal = pyqtSignal(InfoObj)

    subscribe_signal = pyqtSignal(InfoObj, bool)

    @classmethod
    def getNovelSize(cls) -> QSize:
        return QSize(cls.IMG_DFT_SIZE[0] * cls.scaled,
                     cls.IMG_DFT_SIZE[1] * cls.scaled)

    def getNovelName(self) -> str:
        if self.inf:
            return self.inf.novel_name
        return ""

    def crawlNovelImage(self) -> bool:
        if self.inf:
            if self.inf.novel_img_save_flag == False:
                self.img_q.put(self.inf)
                return True
        return False

    @property
    def info(self) -> InfoObj:
        return self.inf

    @info.setter
    def info(self, inf) -> None:
        self.inf = inf

    @lasyproperty
    def novel_widget(self) -> "NovelWidget":
        return self.inf.novel_app

    def __repr__(self) -> str:
        if self.inf.novel_subs_state:
            return f"SubscribeWidget<{self.inf.novel_name}>"
        return f"IconWidget<{self.inf.novel_name}>"

    def __init__(
        self,
        inf: InfoObj,
        listwidget: "IconsListWidget",
        img_q: Queue,
        subscribe: bool = False,
    ):
        super().__init__()
        self.init(inf, listwidget, img_q, subscribe)

    def init(self, inf, listwidget, img_q, subscribe) -> None:
        QToolTip.setFont(QFont("????????????", 10))
        self.setFocusPolicy(Qt.StrongFocus)  # ??????????????????
        self.retry_counts = 0  # ??????????????????
        self.subscribe = subscribe
        self.list_widget = listwidget
        self.img_q = img_q
        self.inf = inf
        self.put = False
        self._enter = False

        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        m1, m2, m3, m4 = self.MARGINS
        lay.setContentsMargins(m1, m2, m3, m4)
        self.checkbox = QCheckBox(self)
        self.checkbox.hide()

        self.img_label = ShadowLabel(shadow=self.BKG_COLOR)
        self.img_label.setScaledContents(True)
        w, h = self.IMG_DFT_SIZE
        self.img_label.setFixedSize(w * self.scaled, h * self.scaled)
        self.file_label = ProgressLabel()
        self.file_label.setFont(QFont("????????????", 9))
        fontmetrics = self.file_label.fontMetrics()
        self.file_label.setWordWrap(True)
        self.file_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        # self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setFixedHeight(fontmetrics.height() * 2)
        self.file_label.setFixedWidth(w * self.scaled)
        lay.addWidget(self.img_label)
        lay.addWidget(self.file_label)

        self.setFixedWidth(w * self.scaled + self.MARGINS[0] + self.MARGINS[2])
        self.setFixedHeight(h * self.scaled + self.file_label.height() +
                            self.MARGINS[1] + self.MARGINS[3])
        self.setCursor(Qt.PointingHandCursor)
        self.addInfo(inf)
        self.installEventFilter(self)

    def resizeNovelImage(self, scaled: float) -> QSize:
        w, h = self.IMG_DFT_SIZE
        IconWidget.scaled = scaled
        self.setFixedWidth(w * self.scaled + self.MARGINS[0] + self.MARGINS[2])
        self.setFixedHeight(h * self.scaled + self.file_label.height() +
                            self.MARGINS[1] + self.MARGINS[3])
        self.img_label.setFixedSize(w * self.scaled, h * self.scaled)
        self.file_label.setFixedWidth(w * self.scaled)
        return QSize(self.width(), self.height())

    def novelImageExists(self) -> bool:  # ??????????????????
        return self._imgExists()

    def addInfo(self, inf: InfoObj) -> None:
        self.inf = inf
        self.inf.novel_meta.setdefault("novel_colors", self.novel_colors)
        self.inf.novel_meta.setdefault("submit_widget", self.subscribe)
        tool_tip = (self.inf.novel_name + "\n" +
                    self.inf.novel_introutced).replace("<br>", "\n")
        self.tool_tip = fill(tool_tip.strip(),
                             40,
                             max_lines=16,
                             placeholder="...")
        self.setToolTip(self.tool_tip)
        self.file_path = QDir(inf.novel_img_save_path).absoluteFilePath(
            inf.novel_img_name)
        if self.novelImageExists():
            scaled_pixmap = QPixmap(self.file_path).scaled(
                self.img_label.size(), transformMode=Qt.SmoothTransformation)
            self.img_label._addRect(scaled_pixmap)
            self.inf.novel_img_save_flag = True
            self.put = True
        else:
            scaled_pixmap = self.drawNovelImage(inf.novel_name)
        self.img_label.setPixmap(scaled_pixmap)
        fontmetrics = self.file_label.fontMetrics()
        elide_file_name = fontmetrics.elidedText(inf.novel_name, Qt.ElideRight,
                                                 self.file_label.width() * 2)
        name = InfTools.addColor("red",
                                 inf.novel_app.search_content,
                                 name=elide_file_name)
        self.file_label.setText(name)

        if inf.novel_download:
            self._downOkFlag()

    @pyqtSlot(str)
    def setNovelImage(self, file_path: str) -> None:
        try:
            if self._validImage(file_path) == False:
                file_info = QFileInfo(file_path)
                pixmap = self.drawNovelImage(file_info.baseName())
                self.img_label.setPixmap(pixmap)
            else:
                self.img_label.setPixmap(QPixmap(file_path))
        except:
            ...
        self.update()

    def haslatestChapterState(self, state: bool) -> None:
        if self.subscribe:
            self.file_label.haslatestChapterState(state)

    def isBrokenLink(self, state: bool) -> None:
        if self.subscribe:
            self.file_label.isBrokenLink(state)

    def enterEvent(self, event):
        super().enterEvent(event)
        self._enter = True
        self.img_label.createShadow()
        if self.SHOW_TIP:
            if not self.toolTip():
                self.setToolTip(self.tool_tip)
            QToolTip.showText(event.globalPos(), self.tool_tip, self)
        else:
            self.setToolTip("")
        self.update()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._enter = False
        self.img_label.clearShadow()
        self.update()

    def _textAutoWrap(self,
                      content: str,
                      limit: int,
                      fm: QFontMetrics,
                      rows: int = None) -> str:
        if fm.width(content) >= limit:
            final = []
            res = []
            row_count = 1
            for alpha in content:
                res.append(alpha.strip())
                if fm.width("".join(res)) >= limit:
                    row_count += 1
                    if rows:
                        if row_count > rows:
                            break
                    final.append("".join(res[:-1]))
                    temp = res[-1]
                    res.clear()
                    res.append(temp.strip())
            newst = "\n".join(final) + "\n" + "".join(res)
            if rows:
                newst = fm.elidedText(newst, Qt.ElideRight, limit * rows)
        else:
            newst = content
        return newst

    @lasyproperty
    def novel_colors(self) -> List[str]:
        return sample(self.RANDOM_COLORS, 2)

    def drawNovelImage(self, name: str) -> QPixmap:  # ???????????????
        colors = self.inf.novel_meta.get("novel_colors", self.novel_colors)
        colors = [QColor(color_str) for color_str in colors]
        pixmap = QPixmap(180, 240)
        pixmap.fill(Qt.white)
        painter = QPainter()
        painter.begin(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        font = QFont("??????", 15)
        font.setBold(True)
        painter.setFont(font)
        name = self._textAutoWrap(name, 140, painter.fontMetrics(), rows=3)
        painter.fillRect(QRect(20, 0, 160, 120), colors[0])
        painter.drawText(20, 122, 160, 138, Qt.AlignLeft, name)
        font = QFont("????????????", 28)
        font.setBold(True)
        pen = QPen()
        pen.setColor(colors[1])
        painter.setPen(pen)
        painter.setFont(font)
        painter.drawText(20, 0, 140, 120, Qt.AlignCenter, "Read")
        painter.setPen(Qt.lightGray)
        painter.drawRect(pixmap.rect().adjusted(1, 1, -1, -1))
        if self.inf._is_file:
            painter.setBrush(Qt.lightGray)
        else:
            painter.setBrush(QColor("#B8DAEF"))
        site_points = [
            QPoint(180 / 4 * 2.5, 240),
            QPoint(180, 240 / 8 * 6),
            QPoint(180, 240),
        ]
        painter.drawPolygon(*site_points)
        painter.setPen(Qt.black)
        painter.setFont(QFont("??????", 13))
        painter.drawText(
            180 / 4 * 2,
            240 / 8 * 7,
            180 / 4 * 2,
            240 / 8,
            Qt.AlignRight,
            self.inf.novel_site[0] + " ",
        )
        painter.end()
        return pixmap

    def addSubscribeState(self) -> None:
        self.img_label.addSubscribeState()
        self.img_label.update()

    def removeSubscribeState(self) -> None:
        self.img_label.setSubscribeState(False)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._enter:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setBrush(self.BKG_COLOR)
            painter.setPen(Qt.transparent)
            path = QPainterPath()
            path.addRoundedRect(QRectF(self.rect()), 5, 5)
            painter.drawPath(path)

    def _imgExists(self) -> bool:
        file_info = QFileInfo(
            QDir(self.inf.novel_img_save_path).absoluteFilePath(
                self.inf.novel_img_name))
        return file_info.exists() and self._validImage(
            file_info.absoluteFilePath())

    def _validImage(self, file_path: str) -> bool:
        valid = True
        try:
            Image.open(file_path).verify()
        except:
            valid = False
        return valid

    def eventFilter(self, objwatched, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:  # ???????????????????????????????????????
                self._menuPolicy(event)
            elif event.button() == Qt.LeftButton:  # ????????????
                self.clicked_signal.emit(self.inf)
                self._t1 = time.time()
                if self.checkbox.isHidden() == False:
                    if self.checkbox.isChecked() == True:
                        self.checkbox.setChecked(False)
                    elif self.checkbox.isChecked() == False:
                        self.checkbox.setChecked(True)

        elif event.type() == QEvent.MouseButtonRelease:  # ?????????????????????????????????
            if event.button() == Qt.LeftButton:
                self._t2 = time.time()
                try:
                    if self._t2 - self._t1 >= 1:
                        self._longPressPolicy(event)
                except:
                    traceback.print_exc()
            return True
        elif event.type() == QEvent.MouseButtonDblClick:  # ????????????
            if self.inf:
                self.introutced_signal.emit(self.inf)
            return True
        elif event.type() == QEvent.KeyPress:  # ????????????
            if event.key() == Qt.Key_Escape:
                for widget in self.list_widget.itemWidgets():
                    widget.checkbox.setChecked(False)
                    widget.checkbox.hide()
            return True

        return QWidget.eventFilter(self, objwatched, event)

    def _menuPolicy(self, event) -> None:
        menu = QMenu(self)
        fm = menu.fontMetrics()
        width = fm.width("???" * 10)
        menu.setFixedWidth(width)
        menu.setStyleSheet(StyleSheets.menu_style)
        a1 = menu.addAction(QIcon(":/ico/book_128px_1138983_easyicon.net.ico"),
                            "????????????")
        a1.setCheckable(True)
        if self.inf.novel_download:
            a3 = menu.addAction(
                QIcon(":/ico/reload_128px_1139035_easyicon.net.ico"), "????????????")
        else:
            a3 = menu.addAction(
                QIcon(":/ico/download_128px_1139003_easyicon.net.ico"), "????????????")
        a3.setCheckable(True)
        menu.addSeparator()
        a4 = menu.addAction(
            QIcon(":/ico/check_128px_1138992_easyicon.net.ico"), "????????????")
        a4.setCheckable(True)
        a5 = menu.addAction(
            QIcon(":/ico/close_128px_1138994_easyicon.net.ico"), "????????????")
        a5.setCheckable(True)
        menu.addSeparator()
        a10 = menu.addAction("??????????????????")
        if self.inf.novel_subs_url and (self.inf._is_file == False):
            menu.addSeparator()
            sub_menu = QMenu("??????")
            sub_menu.setStyleSheet(StyleSheets.menu_style)
            a6 = sub_menu.addAction("????????????")
            a7 = sub_menu.addAction("????????????")
            a6.setCheckable(True)
            a7.setCheckable(True)
            menu.addMenu(sub_menu)
        act = menu.exec_(QCursor.pos())
        if act == a1:
            if self.inf:
                self.introutced_signal.emit(self.inf)
        elif act == a3:
            if self.inf:
                self.down_signal.emit(self.inf)
        elif act == a4:
            self.select()
        elif act == a5:
            self.cancelSelect()
        elif act == a10:
            self.info.novel_app.main_gui.showUI(
                scaled_w=0.65,
                scaled_h=0.5,
                hide=True,
                with_title=False,
                add_shadow=True,
            )
        else:
            if self.inf.novel_subs_url and (self.inf._is_file == False):
                if act == a6:
                    a6.setChecked(True)
                    self.removeSubscribeState()
                    self.subscribe_signal.emit(self.inf, True)
                elif act == a7:
                    a7.setChecked(True)
                    self.removeSubscribeState()
                    self.subscribe_signal.emit(self.inf, False)

    def _longPressPolicy(self, event) -> None:
        for widget in self.list_widget.itemWidgets():
            widget.checkbox.show()
            widget.checkbox.raise_()
        self.checkbox.setChecked(True)

    @pyqtSlot(int)
    def _selectBy(self, checked: int) -> None:
        if checked == Qt.Checked:
            self.select()
        elif checked == Qt.Unchecked:
            self.cancelSelect()

    def select(self) -> None:
        self.checkbox.setChecked(True)
        self.checkbox.show()
        self.checkbox.raise_()

    def cancelSelect(self) -> None:
        self.checkbox.setChecked(False)
        self.checkbox.hide()

    @pyqtSlot()
    def cancelDownload(self) -> None:
        self.inf.novel_down_cancel = True
        self.inf.novel_flag = False
        self._downCancelFlag()

    def downLoad(self) -> None:
        self.file_label.waveStart()

    @pyqtSlot()
    def _downOkFlag(self) -> None:
        self.file_label.stateDone(COLORS.down_ok)

    @pyqtSlot()
    def _downIngFlag(self) -> None:
        self.file_label.stateStart()

    @pyqtSlot()
    def _downCancelFlag(self) -> None:
        self.file_label.stateDone(Qt.transparent)

    _downBeforeFlag = _downCancelFlag

    @pyqtSlot()
    def _downFailFlag(self) -> None:
        self.file_label.waveStop(100, QColor(COLORS.down_fail))


def setIconsToolTip(show: bool) -> None:
    IconWidget.SHOW_TIP = show
    SubscribeWidget.SHOW_TIP = show


def getIconsToolTipState() -> bool:
    return IconWidget.SHOW_TIP


class ShadowLabel(QLabel):
    def __init__(self, *args, **kwargs):
        self._flag = kwargs.pop("flag", False)
        self.subscribe_state = kwargs.pop("subscribe_state", False)
        self.shadow_color = kwargs.pop("shadow", QColor(50, 50, 50, 50))
        super().__init__(*args, **kwargs)

    def addSubscribeState(self) -> None:
        self.subscribe_state = True

    def removeSubscribeState(self) -> None:
        self.subscribe_state = False

    def setSubscribeState(self, state: bool) -> None:
        self.subscribe_state = state
        self.update()

    def createShadow(self):
        self._flag = True
        # self.update()

    def _addRect(self, pixmap: QPixmap) -> None:
        pen = QPen()
        pen.setColor(Qt.lightGray)
        pen.setWidth(2)
        painter = QPainter()
        painter.begin(pixmap)
        painter.setPen(pen)
        painter.drawRect(pixmap.rect())
        painter.end()

    def clearShadow(self) -> None:
        self._flag = False
        # self.update()

    def _drawShadow(self) -> None:
        fill_color = self.shadow_color if self._flag else Qt.transparent
        painter = QPainter()
        painter.begin(self)
        painter.fillRect(QRectF(self.rect()), fill_color)
        if self.subscribe_state:
            points = [QPoint(0, 0), QPoint(0, 40), QPoint(40, 0)]
            painter.setPen(QColor(50, 50, 50, 20))
            painter.setBrush(QColor(50, 50, 50, 20))
            painter.drawPolygon(*points)
            painter.drawPixmap(0, 0, 20, 20,
                               QPixmap(CommonPixmaps.state_pixmap))
        painter.end()

    def paintEvent(self, event):
        super().paintEvent(event)
        self._drawShadow()


class ProgressLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._drawWaveInit()

    def _drawWaveInit(self) -> None:
        # ?????????????????????
        self.wa_color = QColor(150, 150, 150, 180)  # ????????????

        # ????????????????????????
        self.time_id = None
        self.lb_color = None
        self.timer_alive = True
        self.stop_wave = True
        self.m_waterOffset = 0.05
        self.m_offset = 50
        self.m_borderwidth = 10
        self.per_num = -10
        self.flag = 0  # 0??????, 1??????, 2??????,3??????, 4??????
        self.start_flag = -1  # -1, 0, 1

    def _drawWave(self) -> None:
        # ?????????????????????
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing, True)  # ?????????
        # ??????????????????????????????
        width, height = self.width(), self.height()
        percentage = 1 - self.per_num / 100
        # ??????????????????????????? y = A(wx+l) + k
        # w ?????? ??????????????????????????????
        w = 2 * math.pi / (width)
        # A ???????????? ?????????????????????????????????
        A = height * self.m_waterOffset
        # k ?????? y ?????????????????????????????????
        k = height * percentage

        water1 = QPainterPath()
        water2 = QPainterPath()
        # ?????????
        # water1.moveTo(5, height)
        # water2.moveTo(5, height)
        water1.moveTo(-50, height)
        water2.moveTo(-50, height)

        self.m_offset += 0.6

        if self.m_offset > (width / 2):
            self.m_offset = 0
        i = 5
        while i < width - 5:
            waterY1 = A * math.sin(w * i + self.m_offset) + k
            waterY2 = A * math.sin(w * i + self.m_offset + width / 2 * w) + k

            water1.lineTo(i, waterY1)
            water2.lineTo(i, waterY2)
            i += 1

        # ?????????
        water1.lineTo(width + 50, height)
        water2.lineTo(width + 50, height)
        totalpath = QPainterPath()
        totalpath.addRect(QRectF(0, 0, self.width(), self.height()))
        painter.save()
        painter.setPen(Qt.NoPen)

        # ????????????????????????
        watercolor1 = QColor(self.wa_color)
        watercolor1.setAlpha(100)
        watercolor2 = QColor(self.wa_color)
        watercolor2.setAlpha(150)

        path = totalpath.intersected(water1)
        painter.setBrush(watercolor1)
        painter.drawPath(path)

        path = totalpath.intersected(water2)
        painter.setBrush(watercolor2)
        painter.drawPath(path)
        painter.restore()
        painter.end()

    def paintEvent(self, event) -> None:
        if self.flag in (1, 2, 3):
            self._drawWave()
        elif self.flag == 4:
            painter = QPainter()
            painter.begin(self)
            painter.fillRect(QRectF(self.rect()), self.lb_color)
            painter.end()
        super().paintEvent(event)

    def timerEvent(self, event):
        self.per_num += 1
        if self.per_num == 101:
            self.per_num = 10
        if self.stop_wave == True and self.timer_alive == False and self.time_id:
            self.killTimer(self.time_id)
            self.time_id = None
        self.update()

    @pyqtSlot()
    def waveStart(self) -> None:
        self.per_num = 0
        self.stop_wave = False
        self.timer_alive = True
        self.time_id = self.startTimer(80)
        self.flag = 1

    @pyqtSlot(int, QColor)
    def waveStop(self, height: int, lb_color: QColor) -> None:
        self.flag = 3
        self.stop_wave = True
        self.timer_alive = False
        self.lb_color = lb_color
        self.per_num = height

    def stateStart(self) -> None:
        self.flag = 1
        self.per_num = 0
        self.stop_wave = False
        self.timer_alive = True
        self.time_id = self.startTimer(80)

    def statePause(self) -> None:
        if self.time_id is None:
            self.stateStart()
        self.flag = 2
        self.stop_wave = True
        self.timer_alive = False

    def stateResume(self) -> None:
        self.flag = 3
        self.stop_wave = False
        self.timer_alive = True
        self.time_id = self.startTimer(80)

    def stateDone(self, done_color=Qt.red):
        self.flag = 4
        self.per_num = -10
        self.stop_wave = True
        self.timer_alive = False
        self.lb_color = QColor(done_color)


class SubmitLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_latest_update = False
        self.is_broken = False

    def haslatestChapterState(self, state: bool) -> None:
        self.has_latest_update = state
        self.update()

    def isBrokenLink(self, state: bool) -> None:
        self.is_broken = state
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self.is_broken:
            color = Qt.red
            painter = QPainter()
            painter.begin(self)
            painter.setRenderHints(QPainter.Antialiasing, True)
            painter.setBrush(color)
            painter.setPen(color)
            painter.drawEllipse(QPoint(5, 10), 5, 5)
            painter.end()
        if self.has_latest_update:
            color = Qt.darkGreen
            painter = QPainter()
            painter.begin(self)
            painter.setRenderHints(QPainter.Antialiasing, True)
            painter.setBrush(color)
            painter.setPen(color)
            painter.drawEllipse(QPoint(5, 10), 5, 5)
            painter.end()


class TaskWidgetSubmitLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscribe_state = False
        self.chapter_have_latest = False
        self.shadow_color = None

    def setSubscribeState(self, state: bool) -> None:
        self.subscribe_state = state
        self.update()

    def setChaptersState(self, state: bool) -> None:
        self.chapter_have_latest = state
        self.update()

    def createShadow(self, shadow_color) -> None:
        self.shadow_color = shadow_color
        self.update()

    def destroyShadow(self) -> None:
        self.shadow_color = None
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self.subscribe_state:
            points = [QPoint(0, 0), QPoint(0, 40), QPoint(40, 0)]
            painter = QPainter()
            painter.begin(self)
            painter.setRenderHints(QPainter.Antialiasing, True)
            painter.setPen(QColor(50, 50, 50, 20))
            painter.setBrush(QColor(50, 50, 50, 20))
            painter.drawPolygon(*points)
            painter.drawPixmap(0, 0, 20, 20,
                               QPixmap(CommonPixmaps.state_pixmap))
            painter.end()
        if self.chapter_have_latest:
            color = Qt.red
            w, h = self.width(), self.height()
            painter = QPainter()
            painter.begin(self)
            painter.setRenderHints(QPainter.Antialiasing, True)
            painter.setBrush(color)
            painter.setPen(color)
            painter.drawEllipse(QPoint(w - 10, 10), 5, 5)
            painter.end()

        if self.shadow_color:
            painter = QPainter(self)
            painter.fillRect(QRectF(self.rect()), self.shadow_color)


class IconsListWidget(QListWidget):

    switch_sig = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.setVerticalScrollMode(QListWidget.ScrollPerPixel)  # ????????????
        self.setHorizontalScrollMode(QListWidget.ScrollPerPixel)  # ????????????
        self.verticalScrollBar().setSingleStep(15)  # ??????
        self.setUniformItemSizes(True)  # ???????????????????????????
        self.setViewMode(QListView.IconMode)  # ????????????,??????
        self.setMovement(QListView.Static)
        self.setResizeMode(QListView.Adjust)
        self.setFrameShape(QFrame.NoFrame)
        self.setSpacing(1)
        self.widget_results = []  # ????????????
        self.novel_crawl_all_flag = False
        self.verticalScrollBar().setTracking(True)  # ??????
        self.verticalScrollBar().valueChanged.connect(
            lambda position: self.refreshNovelImages())

    def crawlAllImages(self, flag: bool) -> None:
        self.novel_crawl_all_flag = flag

    def crawlImagesFlagsReset(self) -> None:
        self.novel_crawl_all_flag = False

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.buttons() & Qt.MidButton:
            self.switch_sig.emit()

    def resizeIconWidget(self, scaled: float) -> None:
        IconWidget.scaled = scaled
        SubscribeWidget.scaled = scaled
        if self.count() > 0:
            widget = self.itemWidget(self.item(0))
            size = widget.resizeNovelImage(scaled)
            self.setGridSize(size)
            for i in range(self.count()):
                item = self.item(i)
                item.setSizeHint(size)
                widget = self.itemWidget(item)
                widget.resizeNovelImage(scaled)

    def clear(self) -> None:
        super().clear()
        self.novel_crawl_all_flag = False
        self.widget_results.clear()

    def addIconWidget(self, widget: IconWidget) -> None:
        size = widget.size()
        self.addItemWidget(size, widget)

    def removeIconWidget(self, index: int) -> None:
        item = self.item(index)
        self.removeItemWidget(item)
        self.takeItem(index)
        i = 0
        for widget in self.itemWidgets():
            i += 1
            widget.inf.novel_index = i

    def addItemWidget(self, itemsize: QSize,
                      widget: QWidget) -> None:  # ??????item
        item = QListWidgetItem()
        item.setSizeHint(itemsize)
        self.addItem(item)
        self.setItemWidget(item, widget)
        self.widget_results.append(widget)  # icon_widget
        self.setGridSize(itemsize)

    def getItemWidget(self, index: int) -> IconWidget:
        item = self.item(index)
        return self.itemWidget(item)

    def itemWidgets(self) -> List[IconWidget]:
        res = []
        for count in range(self.count()):
            widget = self.getItemWidget(count)
            if widget:
                res.append(widget)
        return res

    def columns(self) -> int:
        if self.count() == 0:
            return 0
        icon = self.getItemWidget(0)
        size = icon.size()
        icons_width = self.width() - 12 - 2
        return (icons_width + 1) // (size.width() + 1)

    def refreshNovelImages(self) -> None:  # ??????????????????
        if self.count() > 0:
            vertical_bar = self.verticalScrollBar()
            if self.novel_crawl_all_flag == False:
                results = self.iconWidgetsPutStates()
                for widget in results:
                    widget.put = True
                    widget.crawlNovelImage()
                if vertical_bar.sliderPosition() == vertical_bar.maximum():
                    self.novel_crawl_all_flag = True

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.count() > 0:
            size = self.getItemWidget(0).size()
            self.setGridSize(size)
        self.refreshNovelImages()

    def enterEvent(self, event) -> None:
        self.setCursor(Qt.ArrowCursor)
        return super().enterEvent(event)

    def iconWidgetsPutStates(self) -> Iterable[IconWidget]:
        top_left = self.indexAt(QPoint(1, 1)).row()
        icon_size = self.widget_results[0].size()
        w, h = icon_size.width(), icon_size.height()
        icons_width = self.width() - 14
        column = (icons_width + 1) // (icon_size.width() + 1)
        l_colum = column - 1
        p = QPoint(l_colum * (w + 1) + l_colum - 1 + 1 + 0.5 * w,
                   self.height())
        bottom = self.indexAt(p).row()
        # bottom = top_left + 25 if bottom == -1 else bottom
        sliced = slice(top_left, None if bottom == -1 else bottom, None)
        return (widget for widget in self.widget_results[sliced]
                if widget.put == False)


class SubState(IntEnum):
    update_no = 0  # ???????????????
    update_fail = 1  # ????????????
    update_latest = 2  # ?????????????????????


class SubscribeWidget(QWidget):

    SHOW_TIP = True

    HOVER_COLOR = COLORS.icon_hover_color

    IMG_DFT_SIZE = 180, 240

    RANDOM_COLORS = [
        "#CEFFCE",
        "#97CBFF",
        "#7D7DFF",
        "#D6D6AD",
        "#5CADAD",
        "#FF95CA",
        "#B15BFF",
        "#F1E1FF",
        "#5F9EA0",
        "#9ACD32",
    ]
    scaled = 0.67

    clicked_signal = pyqtSignal(InfoObj)

    introutced_signal = pyqtSignal(InfoObj)  # double click

    subscribe_signal = pyqtSignal(InfoObj, bool)

    def resizeNovelImage(self, scaled: float) -> QSize:
        w, h = self.IMG_DFT_SIZE
        SubscribeWidget.scaled = scaled
        self.setFixedWidth(w * self.scaled + self.margins + self.margins)
        self.setFixedHeight(h * self.scaled + self.margins * 2 + self.spacing +
                            self.text_height)
        return QSize(self.width(), self.height())

    @classmethod
    def novel_size(cls) -> QSize:
        return QSize(cls.IMG_DFT_SIZE[0] * cls.scaled,
                     cls.IMG_DFT_SIZE[1] * cls.scaled)

    @lasyproperty
    def novel_colors(self) -> List:
        return sample(self.RANDOM_COLORS, 2)

    @lasyproperty
    def novel_widget(self) -> 'NovelWidget':
        return self.info.novel_app

    @lasyproperty
    def subscribe_downloader(self) -> ChapterDownloader:
        novel_widget = self.novel_widget
        new_loop = asyncio.new_event_loop()
        loader = ChapterDownloader(novel_widget.thread_seam, self.info,
                                   new_loop)
        loader.update_signal.connect(self.chapterUpdateInfos)
        loader.flag_signal.connect(self.processFlags)
        return loader

    def subscribeDownload(self) -> None:
        if self.info.novel_subs_state:
            if self.info.novel_flag == False:
                self.info.novel_down_cancel = False
                self._downIngFlag()
                task_widget = self.novel_widget.getCurrentTaskWidget()
                if task_widget:
                    task_widget._downIngFlag()
                self.subscribe_downloader.download(self.info)
                self._downIngFlag()

    def chapterUpdateInfos(self, inf: InfoObj) -> None:
        novel_widget = self.novel_widget
        task_widget = novel_widget.getCurrentTaskWidget()
        self.clicked_msg = "?????????..."
        if task_widget:
            if inf.novel_index == task_widget._inf.novel_index:
                task_widget.updateFromInf(inf)

    def processFlags(self, info: InfoObj) -> None:
        inf = info
        novel_widget = self.novel_widget
        task_widget = novel_widget.getCurrentTaskWidget()
        if inf.novel_status == DownStatus.down_fail:
            msg = inf.novel_name + f"[{inf.novel_site}]????????????"
            if task_widget:
                task_widget._downFailFlag()
            novel_widget.titleMsgInfo(msg)
            self.clicked_msg = "????????????"
            self._downFailFlag()
        elif inf.novel_status == DownStatus.down_ok:
            msg = inf.novel_name + f"[{inf.novel_site}]?????????"
            novel_widget.addDownRecord(inf, first=True)
            if task_widget:
                task_widget._downOkFlag()
            novel_widget.titleMsgInfo(msg)
            self.clicked_msg = "?????????"
            self._downOkFlag()
        elif inf.novel_status == DownStatus.down_ing:
            if task_widget:
                task_widget._downIngFlag()
            self.clicked_msg = ""
        elif inf.novel_status == DownStatus.down_before:
            if task_widget:
                task_widget._downBeforeFlag()
            self.clicked_msg = ""
            self._downBeforeFlag()

    def prepare_restart(self) -> None:
        self.info.novel_status = DownStatus.down_before
        self.info.novel_percent = 0
        self._downBeforeFlag()

    @pyqtSlot()
    def _downOkFlag(self) -> None:
        w, h = self.width(), self.height()
        x = self.margins
        y = h - self.text_height - self.margins
        _w = w - self.margins * 2
        _h = self.text_height
        self.text_color = QColor(COLORS.down_ok)
        self.update(x, y, _w, _h)

    @pyqtSlot()
    def _downIngFlag(self) -> None:
        self.time_id = self.startTimer(100)

    @pyqtSlot()
    def _downCancelFlag(self) -> None:
        self.text_color = Qt.black
        self.update()

    _downBeforeFlag = _downCancelFlag

    @pyqtSlot()
    def _downFailFlag(self) -> None:
        self.text_color = QColor(COLORS.down_fail)
        self.update()

    def __init__(self, info: InfoObj, list_widget, **kwargs):
        super().__init__()
        self.info = info
        self.info.novel_temp_data['type'] = 'subscribe'
        self.list_widget = list_widget
        self.novel_pix = None
        self.text_content = None
        self._enter = False
        self.subscribe_state = True  # ???????????????
        self.subscribe_link_state = 0  # 0, 1 ??????, 2 ??????
        self.novel_exists = False
        self.time_id = None
        self.clicked_msg: str = ""
        self.margins = kwargs.pop("margins", 10)
        self.spacing = kwargs.pop("spacing", 2)
        self.text_font = QFont("????????????", 9)
        self.text_color = Qt.black
        self.text_height = QFontMetrics(self.text_font).height() * 2
        scaled_x = self.IMG_DFT_SIZE[0] * self.scaled
        scaled_y = self.IMG_DFT_SIZE[1] * self.scaled
        fix_w = scaled_x + self.margins * 2
        fix_h = scaled_y + self.margins * 2 + self.spacing + self.text_height
        # y = (scaled_y / 4 - 25) / 2
        self.setCursor(Qt.PointingHandCursor)
        self.setSubscribeState(True)
        self.setFixedSize(fix_w, fix_h)
        h = QFontMetrics(self.text_font).height()
        self.read_button = ColorButton(self, clicked=self._read)
        self.read_button.setHoverLeave(CommonPixmaps.hl_subs_read,
                                       ('#2E5AA6', '#2E5AA6'),
                                       ('#4585F5', '#4585F5'), h)
        self.read_button.setStyleSheet('border: none')
        self.read_button.setFixedSize(h, h)
        self.read_button.hide()
        self.addInfo(info)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._menuPolicy)
        self.installEventFilter(self)
        self.setStyleSheet('QToolTip{background: white}')

    def _read(self):
        novel_app = self.info.novel_app
        novel_app.gotoIntroutced(self.info)
        novel_app.getCurrentTaskWidget().read_button.click()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        y = self.height() - self.text_height - self.margins# 
        _h = self.text_height
        scaled_x = self.IMG_DFT_SIZE[0] * self.scaled
        y = y + (_h - self.read_button.height()) / 2
        self.read_button.move(self.margins + scaled_x - self.read_button.width() - 2, y)

    def _menuPolicy(self) -> None:
        if self.info:
            novel_app = self.info.novel_app
            menu = QMenu(self)
            menu.setStyleSheet(StyleSheets.menu_style)
            fm = menu.fontMetrics()
            width = fm.width("???" * 10)
            menu.setFixedWidth(width)
            a1 = menu.addAction(
                QIcon(":/ico/book_128px_1138983_easyicon.net.ico"), "????????????")
            a2 = menu.addAction("????????????")
            a3 = menu.addAction("??????????????????")
            menu.addSeparator()
            a4 = menu.addAction("??????????????????")
            menu.addSeparator()
            at_title = ("????????????" if self.info.novel_read_infos.get(
                "chapter_name", None) is not None else "????????????")
            a5 = menu.addAction(at_title)
            act = menu.exec_(QCursor.pos())
            if act == a1:
                self.introutced_signal.emit(self.info)
            elif act == a2:
                self.subscribe_signal.emit(self.info, False)
            elif act == a3:
                for subscribe in self.list_widget.itemWidgets():
                    info = subscribe.info
                    novel_app._removeSubsInfo(info)
                novel_app.titleMsgInfo("?????????: 0?????????", True)
            elif act == a4:
                novel_app.main_gui.showUI(
                    scaled_w=0.65,
                    scaled_h=0.5,
                    hide=True,
                    with_title=False,
                    add_shadow=True,
                )
            elif act == a5:
                self._read()

    def novelImageExists(self) -> bool:
        file_info = QFileInfo(
            QDir(self.info.novel_img_save_path).absoluteFilePath(
                self.info.novel_img_name))
        flag1 = file_info.exists()
        flag2 = True
        try:
            Image.open(file_info.absoluteFilePath()).verify()
        except:
            flag2 = False
        res = flag1 and flag2
        self.novel_exists = res
        return res

    def addInfo(self, info: InfoObj) -> None:
        QToolTip.setFont(QFont("????????????", 10))
        self.info = info
        self.info.novel_meta.setdefault("novel_colors", self.novel_colors)
        tool_tip = (self.info.novel_name + "\n" +
                    self.info.novel_introutced).replace("<br>", "\n")
        self.tool_tip = fill(tool_tip.strip(),
                             40,
                             max_lines=16,
                             placeholder="...")
        self.setToolTip(self.tool_tip)
        file_path = QDir(info.novel_img_save_path).absoluteFilePath(
            info.novel_img_name)
        self.setNovelName(info.novel_name)
        if self.novelImageExists():
            self.setNovelPixmap(file_path)
        else:
            novel_pixmap = self.drawNovelImage(info.novel_name)
            self.setNovelPixmap(novel_pixmap)
        self.update()

    def drawNovelImage(self, name: str) -> QPixmap:  # ???????????????
        colors = self.info.novel_meta.get("novel_colors", self.novel_colors)
        colors = [QColor(color_str) for color_str in colors]
        pixmap = QPixmap(180, 240)
        pixmap.fill(Qt.white)
        painter = QPainter()
        painter.begin(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        font = QFont("??????", 15)
        font.setBold(True)
        painter.setFont(font)
        name = self._textAutoWrap(name, 140, painter.fontMetrics(), rows=3)
        painter.fillRect(QRect(20, 0, 160, 120), colors[0])
        painter.drawText(20, 122, 160, 138, Qt.AlignLeft, name)
        font = QFont("????????????", 28)
        font.setBold(True)
        pen = QPen()
        pen.setColor(colors[1])
        painter.setPen(pen)
        painter.setFont(font)
        painter.drawText(20, 0, 140, 120, Qt.AlignCenter, "Read")
        painter.setPen(Qt.lightGray)
        painter.drawRect(pixmap.rect().adjusted(1, 1, -1, -1))
        if self.info._is_file:
            painter.setBrush(Qt.lightGray)
        else:
            painter.setBrush(QColor("#B8DAEF"))
        site_points = [
            QPoint(180 / 4 * 2.5, 240),
            QPoint(180, 240 / 8 * 6),
            QPoint(180, 240),
        ]
        painter.drawPolygon(*site_points)
        painter.setPen(Qt.black)
        painter.setFont(QFont("??????", 13))
        painter.drawText(
            180 / 4 * 2,
            240 / 8 * 7,
            180 / 4 * 2,
            240 / 8,
            Qt.AlignRight,
            self.info.novel_site[0] + " ",
        )
        painter.end()
        return pixmap

    def setNovelPixmap(self, file: Any):
        self.novel_pix = QPixmap(file).scaled(
            self.IMG_DFT_SIZE[0],
            self.IMG_DFT_SIZE[1],
            transformMode=Qt.SmoothTransformation,
        )

    def setNovelName(self, text: str):
        self.text_content = text

    def setSubscribeState(self, state: bool):
        self.subscribe_state = state
        self.update()

    def setSubscirbeLinkState(self, state: SubState):
        self.subscribe_link_state = state
        self.update()

    def enterEvent(self, a0) -> None:
        super().enterEvent(a0)
        self._enter = True
        if self.read_button.isHidden():
            self.read_button.show()
        if self.SHOW_TIP:
            if not self.toolTip():
                self.setToolTip(self.tool_tip)
            QToolTip.showText(a0.globalPos(), self.tool_tip, self)
        else:
            self.setToolTip("")
        self.update()

    def leaveEvent(self, a0) -> None:
        super().leaveEvent(a0)
        self.read_button.hide()
        self._enter = False
        self.update()

    def _textAutoWrap(self,
                      content: str,
                      limit: int,
                      fm: QFontMetrics,
                      rows: int = None) -> str:
        if fm.width(content) >= limit:
            final = []
            res = []
            row_count = 1
            for alpha in content:
                res.append(alpha)
                if fm.horizontalAdvance("".join(res)) >= limit:
                    row_count += 1
                    if rows:
                        if row_count > rows:
                            break
                    final.append("".join(res))
                    res.clear()
            newst = "\n".join(final) + "\n" + "".join(res)
            if rows:
                newst = fm.elidedText(newst, Qt.ElideRight, limit * rows)
        else:
            newst = content
        return newst

    def timerEvent(self, event) -> None:
        if self.info.novel_status != DownStatus.down_ing:
            if self.time_id is not None:
                self.killTimer(self.time_id)
                self.time_id = None
        else:
            w, h = self.width(), self.height()
            x = self.margins
            y = h - self.text_height - self.margins
            _w = w - self.margins * 2
            _h = self.text_height
            self.update(x, y, _w, _h)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        if self.novel_pix:  # ????????????
            x = self.margins
            y = self.margins
            _w = w - self.margins * 2
            _h = h - self.text_height - self.margins * 2 - self.spacing
            pixmap = self.novel_pix.scaled(
                _w, _h, transformMode=Qt.SmoothTransformation)
            painter.drawPixmap(x, y, _w, _h, pixmap)
            if self.novel_exists:
                pen = QPen(Qt.lightGray, 1)
                painter.setPen(pen)
                painter.drawRect(x, y, _w, _h)

        if self.text_content:  # ????????????
            x = self.margins
            y = h - self.text_height - self.margins
            _w = w - self.margins * 2
            _h = self.text_height
            painter.setPen(self.text_color)
            painter.setFont(self.text_font)
            if not self._enter:
                draw_text = self._textAutoWrap(self.text_content, _w - 10,
                                               painter.fontMetrics(),
                                               2).strip()
                flags = Qt.AlignTop | Qt.AlignHCenter if len(
                    draw_text.splitlines()) == 1 else Qt.AlignLeft
                painter.drawText(x, y, _w, _h, flags, draw_text)
                if self.info.novel_status == DownStatus.down_ing:
                    percent_w = self.info.novel_percent / 100 * _w
                    painter.setBrush(QColor(78, 184, 83, 80))
                    painter.setPen(Qt.transparent)
                    painter.drawRect(x, y, percent_w, _h)
            else:
                latest = self.info.getLatestRead()
                text = "????????????" if latest.chapter_name is not None else "????????????"
                color = Qt.darkRed if text == '????????????' else Qt.darkGreen
                painter.setPen(color)
                f = painter.font()
                f.setBold(True)
                painter.setFont(f)
                painter.drawText(x, y, _w, _h, Qt.AlignLeft | Qt.AlignVCenter,
                                 '   ' + text)

        if self._enter:  # ??????????????????
            x = self.margins
            y = self.margins
            _w = w - self.margins * 2
            _h = h - self.text_height - self.margins * 2 - self.spacing
            painter.save()
            painter.setPen(Qt.transparent)
            painter.setBrush(QColor(20, 20, 20, 20))
            painter.drawRect(x, y, _w, _h / 4)

            painter.setPen(QColor('#F4F4F4'))  #636262
            painter.setFont(QFont('????????????', 9, QFont.Bold))
            painter.setCompositionMode(
                QPainter.CompositionMode_Difference)  # ????????????

            text = self.info.getLatestRead().chapter_name
            text = self.info.first_chapter() if text is None else text
            text = self._textAutoWrap(text, _w - 8, painter.fontMetrics(),
                                      1).strip()
            painter.drawText(x, y, _w, _h / 4, Qt.AlignCenter, text)
            painter.restore()

            # path = QPainterPath()
            # path.addRoundedRect(QRectF(self.rect()), 5, 5)
            # painter.fillPath(path, self.HOVER_COLOR)

        if self.subscribe_state:  # ??????state
            painter.setBrush(QColor(50, 50, 50, 20))
            painter.setPen(QColor(50, 50, 50, 20))
            points = [
                QPoint(self.margins, self.margins),
                QPoint(self.margins + 40, self.margins),
                QPoint(self.margins, self.margins + 40),
            ]
            pixmap = QPixmap(CommonPixmaps.state_pixmap)
            painter.drawPixmap(self.margins, self.margins, 20, 20, pixmap)
            painter.drawPolygon(*points)

        # ??????????????????
        if self.subscribe_link_state == SubState.update_no:  # ???????????????
            painter.setBrush(Qt.transparent)
            painter.setPen(Qt.transparent)
        if self.subscribe_link_state == SubState.update_fail:  # ????????????
            painter.setBrush(Qt.darkRed)
            painter.setPen(Qt.darkRed)
        elif self.subscribe_link_state == SubState.update_latest:  # ?????????
            painter.setBrush(Qt.darkGreen)
            painter.setPen(Qt.darkGreen)
        x = self.margins + 5
        y = h - self.text_height - self.margins + 5
        painter.drawEllipse(QPoint(x, y), 5, 5)

    def eventFilter(self, a0: "QObject", a1: "QEvent") -> bool:
        if a1.type() == QEvent.MouseButtonDblClick:
            if self.info:
                self.introutced_signal.emit(self.info)
            return True
        elif a1.type() == QEvent.MouseButtonPress:
            if a1.button() == Qt.LeftButton:
                if self.info:
                    self.clicked_signal.emit(self.info)
        return super().eventFilter(a0, a1)


class SubscribeListWidget(IconsListWidget):
    def refreshNovelImages(self) -> None:
        return

    def iconWidgetsPutStates(self) -> None:
        return

    def addSubscribeWidget(self, widget: SubscribeWidget) -> None:
        self.addIconWidget(widget)

    def removeSubscribeWidget(self, index: int) -> None:
        item = self.item(index)
        self.removeItemWidget(item)
        self.takeItem(index)
        i = 0
        for widget in self.itemWidgets():
            i += 1
            widget.info.novel_index = i
            widget.info.novel_subs_index = i - 1

    def removeSubscribeWidgetByInfo(self, info: InfoObj) -> bool:
        novel_widget = info.novel_app
        sets = novel_widget.subscribe_urls
        if info.novel_subs_url in sets:
            for index, subs in enumerate(self.itemWidgets()):
                if info.novel_subs_url == subs.info.novel_subs_url:
                    self.removeSubscribeWidget(index)
                    return True
        return False

    def subscribeWidgets(self) -> List[SubscribeWidget]:
        return self.itemWidgets()


class SiteButton(QPushButton):

    site_changed = pyqtSignal(bool, int)  # state, index

    select_signal = pyqtSignal(bool)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        width = self.fontMetrics().width("????????????") * 2 + 15
        height = self.fontMetrics().height() * 2
        self.setFixedSize(width, height)
        self.__combobox = QComboBox(self)
        self.__listwidget = QListWidget()
        self.__listwidget.verticalScrollBar().setStyleSheet(
            StyleSheets.vertical_scroll_style)  #site_button_v_scrollbar
        self.__combobox.setModel(self.__listwidget.model())
        self.__combobox.setView(self.__listwidget)
        self.__combobox.setGeometry(0, 0, width, height)
        self.__combobox.setMaxVisibleItems(21)
        self.__combobox.hide()
        self.__sitenames = []
        self.__seprator = False
        self.select_all = False
        self.clicked.connect(self.showPopup)
        self.__listwidget.setStyleSheet(StyleSheets.site_button_listview_style)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.customContext)

    def customContext(self):
        menu = QMenu(self)
        a1 = menu.addAction('?????????????????????')
        a2 = menu.addAction('?????????????????????')
        action = menu.exec_(QCursor.pos())
        if action == a1:
            self.selectAll(True)
        elif action == a2:
            self.selectAll(False)

    def addPopWidth(self, width: int) -> None:
        self.__combobox.setGeometry(0, 0, self.width() + width, self.height())

    def selectAll(self, state: bool = True) -> None:
        self.select_all = state
        for index in range(self.__listwidget.count()):
            item = self.__listwidget.item(index)
            widget = self.__listwidget.itemWidget(item)
            if widget.is_sperator == False:
                widget.checkbox.setChecked(state)

    @property
    def site_names(self) -> List[str]:
        return self.__sitenames

    def showPopup(self) -> None:
        self.__combobox.showPopup()

    def siteCount(self) -> int:
        return self.__listwidget.count()

    def removeSite(self, name: str) -> bool:
        index = self.__sitenames.index(name)
        if index >= 0:
            self.__listwidget.takeItem(index)
            return True
        return False

    def clear(self) -> None:
        self.__combobox.clear()
        self.__listwidget.clear()
        self.__sitenames.clear()
        self.__seprator = False

    def addSite(self,
                site: str,
                state: bool,
                is_file: bool = True,
                clicked: Callable = None) -> bool:
        if "**==**" not in self.__sitenames:
            self.__sitenames.append("**==**")
        if self.__seprator == False:
            widget = QWidget()
            widget.setStyleSheet("background-color:#66D166")
            widget.is_sperator = True
            item = QListWidgetItem()
            item.setSizeHint(QSize(300, 3))
            self.__listwidget.addItem(item)
            self.__listwidget.setItemWidget(item, widget)
            self.__seprator = True
        if site in self.__sitenames:
            return False
        else:
            flag_index = self.__sitenames.index("**==**")
            if is_file:
                self.__sitenames.insert(flag_index, site)
            else:
                self.__sitenames.append(site)

            item = QListWidgetItem()
            widget = QWidget()
            widget.is_sperator = False
            lay = QHBoxLayout(widget)
            lay.setContentsMargins(8, 2, 0, 2)
            checkbox = QCheckBox()
            checkbox.setFont(QFont("????????????", 9))
            checkbox.setText(site)
            checkbox.setChecked(state)
            lay.addWidget(checkbox)
            mb_c = ":/ico/delete_1301146_easyicon.net.svg"
            mb_uc = ":/ico/delete_1301146_easyicon.net.svg"
            mb_t = "<b>??????????????????</b>"
            mb_ut = "<b>??????????????????</b>"
            mode_button = MenuButton(mb_c, mb_uc, 26, start_state=False)
            mode_button.setToolTips(mb_t, mb_ut)
            lay.addWidget(mode_button)
            item.setSizeHint(widget.sizeHint())
            if clicked:
                mode_button.clicked.connect(clicked)
            if is_file:
                self.__listwidget.insertItem(flag_index, item)
            else:
                self.__listwidget.addItem(item)
            self.__listwidget.setItemWidget(item, widget)
            widget.checkbox = checkbox
            for index in range(self.__listwidget.count()):
                item = self.__listwidget.item(index)
                widget = self.__listwidget.itemWidget(item)
                if widget.is_sperator == False:
                    _ss = partial(self.__onsitechange, index)
                    try:
                        widget.checkbox.stateChanged.disconnect()
                    except:
                        ...
                    widget.checkbox.stateChanged.connect(_ss)
            return True

    def __onsitechange(self, index: int, state: int) -> None:
        flag = self.__listwidget.count() - 1
        i = 0
        for j in range(self.__listwidget.count()):
            item = self.__listwidget.item(j)
            widget = self.__listwidget.itemWidget(item)
            if not widget.is_sperator:
                if widget.checkbox.isChecked():
                    i += 1
        if i == flag:
            self.select_signal.emit(True)
        elif i < flag:
            self.select_signal.emit(False)

        if state == Qt.Checked:
            self.site_changed.emit(True, index)
        elif state == Qt.Unchecked:
            self.site_changed.emit(False, index)

    def getSiteState(self, index: int) -> bool:
        item = self.__listwidget.item(index)
        widget = self.__listwidget.itemWidget(item)
        if widget.is_sperator == False:
            return widget.checkbox.isChecked()
        return False

    def getSiteName(self, index: int) -> str:
        item = self.__listwidget.item(index)
        widget = self.__listwidget.itemWidget(item)
        if widget.is_sperator == False:
            return widget.checkbox.text()
        return "**==**"

    def siteStates(self) -> list:
        v = []
        for i in range(self.siteCount()):
            v.append(self.getSiteState(i))
        return v

    def statesDict(self) -> dict:
        res = {}
        for i in range(self.siteCount()):
            res[self.getSiteName(i)] = self.getSiteState(i)
        return res


class DebugTextEdit(QPlainTextEdit):
    def __repr__(self) -> str:
        return "DebugTextEdit"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme_color = "white"
        self.setReadOnly(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.highlighter = DebugHighlighter(self.document())
        self.number_area = _LineNumberArea(self)
        self.blockCountChanged.connect(
            self.updateLineNumberAreaWidth)  # ??????,????????????
        self.updateRequest.connect(self.updateLineNumberArea)  # ????????????
        self.customContextMenuRequested.connect(self._menuPolicy)
        self.updateLineNumberAreaWidth(0)
        self.setStyleSheet(
            "selection-background-color: lightblue;selection-color:black;background:white"
        )
        self.verticalScrollBar().setStyleSheet(
            StyleSheets.debugtextedit_v_scroll_style)
        self.horizontalScrollBar().setStyleSheet(
            StyleSheets.debugtextedit_h_scroll_style)

    @lasyproperty
    def logger(self) -> logging.Logger:
        root = logging.getLogger()
        root.setLevel(logging.NOTSET)
        logger = logging.getLogger("?????????")
        logger.setLevel(logging.NOTSET)
        formater = logging.Formatter(
            "[%(name)s] [%(asctime)s] [%(novelname)s] %(levelname)s: %(message)s"
        )
        debug_hanlder = logging.StreamHandler()
        debug_hanlder.terminator = ""
        debug_hanlder.setStream(self)
        debug_hanlder.setFormatter(formater)
        debug_hanlder.setLevel(logging.DEBUG)
        logger.addHandler(debug_hanlder)
        return logger

    def forceLog(self, msg: str, level: int, **kwargs) -> None:
        self.logger.log(level, msg, **kwargs)

    def write(self, value: str) -> None:
        self.append(value)

    def flush(self) -> None:
        pass

    def _menuPolicy(self) -> None:
        clip = QApplication.clipboard()
        menu = QMenu(self)
        menu.setStyleSheet(StyleSheets.menu_style)
        a1 = menu.addAction("??????")
        a2 = menu.addAction("????????????")
        a1.setShortcut("ctrl+c")
        a2.setShortcut("ctrl+a")
        act = menu.exec_(QCursor.pos())
        if act == a1:
            txt = self.textCursor().selectedText()
            clip.setText(txt)
        elif act == a2:
            self.selectAll()

    def setTheme(self, theme_mode: str, color: str = "") -> None:
        self.highlighter.retheme(theme_mode)
        self.theme_color = color
        if theme_mode.find("dark") >= 0:
            self.theme_color = "#000C18"
            color = self.theme_color if self.theme_color else "#000C18"
            self.setStyleSheet(
                f"selection-background-color: lightblue;selection-color:black;background:{color}"
            )
        elif theme_mode.find("light") >= 0:
            self.theme_color = "white"
            color = self.theme_color if self.theme_color else "white"
            self.setStyleSheet(
                f"selection-background-color: lightblue;selection-color:black;background: transparent"
            )

    def clearAllLines(self) -> None:
        self.clear()

    def append(self, value: str) -> None:
        self.appendPlainText(value)

    def resizeEvent(self, event):  # ???????????????????????????
        super().resizeEvent(event)
        rect = self.contentsRect()
        new_geo = QRect(rect.left(), rect.top(), self.lineNumberAreaWidth(),
                        rect.height())
        self.number_area.setGeometry(new_geo)

    def updateLineNumberArea(self, rect: QRect, dy: int) -> None:
        if dy:
            self.number_area.scroll(0, dy)
        else:
            self.number_area.update(0, rect.y(), self.number_area.width(),
                                    rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def updateLineNumberAreaWidth(
            self, count: int) -> None:  # ?????????????????????????????????????????????????????????margin
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def lineNumberAreaWidth(self) -> int:
        # ??????blockCount????????????????????????????????????
        # ???????????????????????????????????????????????????????????????????????????????????????????????????1
        digits = 1
        maxed = max(1, self.blockCount())
        while maxed >= 10:
            maxed /= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def lineNumberAreaPainterEvent(self, event) -> None:
        text = self.toPlainText()
        painter = QPainter()
        painter.begin(self.number_area)
        painter.fillRect(event.rect(), Qt.transparent)
        font = QFont("courier")
        font.setBold(True)
        pen = QPen(Qt.transparent if text == "" else Qt.gray)
        painter.setFont(font)
        painter.setPen(pen)
        block = self.firstVisibleBlock()  # ??????????????????????????????
        block_number = block.blockNumber()  # block????????????
        # blockBoundingGeometry(block)??????????????????block??????????????????
        # contentOffset() ???????????????????????????????????????????????????????????????
        top = qRound(
            self.blockBoundingGeometry(block).translated(
                self.contentOffset()).top())
        bottom = top + qRound(self.blockBoundingRect(block).height())

        # while ??? if  ???????????????????????????????????????????????????
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = block_number + 1
                painter.drawText(
                    0,
                    top,
                    self.number_area.width(),
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    f"{number}",
                )
            block = block.next()
            top = bottom
            bottom = top + qRound(self.blockBoundingRect(block).height())
            block_number += 1
        painter.end()


class FailTextEdit(DebugTextEdit):
    def __repr__(self) -> str:
        return "FailTextEdit"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.highlighter = FailHighlighter(self.document())
        action = QAction(self)
        action.setShortcut("ctrl+f")
        action.triggered.connect(lambda: self.search_cmp.show() or self.
                                 search_cmp.s_line.setFocus(True))
        self.addAction(action)
        self.s_action = action

    @lasyproperty
    def search_cmp(self) -> QWidget:
        search_frame = QWidget(self)
        search_frame.setStyleSheet(
            "background: white;border:1px solid lightgray")
        lay = QHBoxLayout(search_frame, spacing=0)
        lay.setContentsMargins(5, 5, 5, 5)
        search_line = QLineEdit()
        search_line.setPlaceholderText("??????")
        search_line.setContextMenuPolicy(Qt.NoContextMenu)
        fm = search_line.fontMetrics()
        height = fm.height() * 1.5
        search_line.setFixedWidth(fm.width("???" * 12))
        search_line.returnPressed.connect(self.findText)
        search_frame.setFixedWidth(search_line.width() + 10 + 40)
        search_frame.setFixedHeight(height + 10)
        lay.addWidget(search_line)
        close = QPushButton()
        close.setStyleSheet("border: none")
        close.setIcon(QIcon(":/ico/close_512px_1175341_easyicon.net.png"))
        close.clicked.connect(lambda: search_frame.hide())
        lay.addWidget(close)
        x = self.width() - search_frame.width() - 30
        search_frame.move(x, 0)
        search_frame.hide()
        search_frame.s_line = search_line
        return search_frame

    def findText(self) -> None:
        txt = self.sender().text().strip()
        if txt:
            cursor = self.textCursor()
            if not self.find(QRegularExpression(txt),
                             QTextDocument.FindBackward):
                self.moveCursor(QTextCursor.End)
                self.horizontalScrollBar().setValue(0)
                flag = self.find(QRegularExpression(txt),
                                 QTextDocument.FindBackward)
                if not flag:
                    message = QMessageBox(self)
                    message.setStyleSheet("background: #F0F0F0")
                    message.setIcon(QMessageBox.Information)
                    message.setWindowTitle("??????")
                    message.setText(f"????????????{txt}!")
                    yes = message.addButton("??????", QMessageBox.YesRole)
                    no = message.addButton("??????", QMessageBox.NoRole)
                    message.exec_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        x = self.width() - self.search_cmp.width() - 30
        self.search_cmp.move(x, 5)

    def _menuPolicy(self) -> None:
        clip = QApplication.clipboard()
        menu = QMenu(self)
        menu.setStyleSheet(StyleSheets.menu_style)
        a1 = menu.addAction("??????")
        a3 = menu.addAction("??????")
        a2 = menu.addAction("????????????")
        a1.setShortcut("ctrl+c")
        a2.setShortcut("ctrl+a")
        a3.setShortcut("ctrl+f")
        act = menu.exec_(QCursor.pos())
        if act == a1:
            txt = self.textCursor().selectedText()
            clip.setText(txt)
        elif act == a2:
            self.selectAll()
        elif act == a3:
            self.search_cmp.show()
            self.search_cmp.s_line.setFocus(True)

    @lasyproperty
    def logger(self) -> logging.Logger:
        root = logging.getLogger()
        root.setLevel(logging.NOTSET)
        logger = logging.getLogger("????????????")
        logger.setLevel(logging.NOTSET)
        formater = logging.Formatter("%(mytime)s: %(message)s")
        debug_hanlder = logging.StreamHandler()
        debug_hanlder.terminator = ""
        debug_hanlder.setStream(self)
        debug_hanlder.setFormatter(formater)
        debug_hanlder.setLevel(logging.DEBUG)
        logger.addHandler(debug_hanlder)
        return logger


class _LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def paintEvent(self, event):
        super().paintEvent(event)
        self.editor.lineNumberAreaPainterEvent(event)


class _ColorTheme(object):

    __instance = None
    __color_pools = {}

    def __new__(cls) -> '_ColorTheme':
        if _ColorTheme.__instance is None:
            instance = object.__new__(cls)
            instance.__dict__["_attatched"] = None
            _ColorTheme.__instance = instance
        return _ColorTheme.__instance

    def __init__(self):
        raise TypeError("????????????__init__")

    @classmethod
    def getColorTheme(cls) -> '_ColorTheme':
        if cls.__instance is None:
            _ColorTheme.__new__(cls)
        return cls.__instance

    def register(
        self,
        property_name: str,
        value: Union[QColor, str, int],
        theme_name: str = "",
        owner=None,
    ) -> None:
        flag = theme_name.split(".")
        if len(flag) == 1:
            _theme = self._attatched if self._attatched else theme_name
            self.__color_pools.setdefault(_theme, {})
            dft: dict = self.__color_pools.get(_theme)
            dft.setdefault("default", {})
            mode_dict = dft.get("default")
        elif len(flag) >= 2:
            theme, mode = flag[0], flag[1]
            _theme = self._attatched if self._attatched else theme
            self.__color_pools.setdefault(_theme, {})
            color_dic: dict = self.__color_pools.get(_theme)
            color_dic.setdefault(mode, {})
            mode_dict = color_dic.get(mode)

        mode_dict[property_name] = QColor(value)

    def getColor(self, property_name: str, theme_name: str = "") -> QColor:
        flag = theme_name.split(".")

        if len(flag) == 1:
            _theme = theme_name if self._attatched is None else self._attatched
            dft = self.__color_pools.get(_theme, None)
            if dft:
                color_dft = dft.get("default", None)
                if color_dft:
                    return color_dft.get(property_name)
            return None

        elif len(flag) >= 2:
            _theme_name, mode = flag[0], flag[1]
            _theme = _theme_name if self._attatched is None else self._attatched
            color_dict = self.__color_pools.get(_theme, None)
            mode_dict = color_dict.get(mode)
            return mode_dict.get(property_name, None)

    def themeNames(self) -> List[str]:
        return list(self.__color_pools.keys())

    def getTheme(self, theme_name: str) -> dict:
        return self.__color_pools.get(theme_name, None)

    def themes(self) -> List[dict]:
        results = []
        for name in self.themeNames():
            results.append(self.getTheme(name))
        return results

    def getAllThemeModes(self) -> List[dict]:
        results = []
        for theme in self.themes():
            for mode in theme.keys():
                results.append(theme[mode])
        return results

    def themeModes(self, theme_name: str = "") -> Iterable:
        _theme_name = self._attatched if self._attatched else theme_name
        color_dict = self.__color_pools.get(_theme_name, None)
        if color_dict is not None:
            return color_dict.keys()
        return None

    def attatchTheme(self, theme_name: str) -> None:
        self._attatched = theme_name

    def getThemeMode(self, theme_name_mode: str) -> dict:
        flag = theme_name_mode.split(".")
        if len(flag) >= 2:
            theme, mode = flag[0], flag[1]
            _theme = self._attatched if self._attatched else theme
            theme_dic = self.__color_pools.get(_theme, None)
            return theme_dic.get(mode, None)

    def report(self) -> None:
        pprint.pprint(self.__color_pools)


def getColorThemeManager() -> _ColorTheme:
    return _ColorTheme.getColorTheme()


class DebugHighlighter(QSyntaxHighlighter):

    rules = []

    formats = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ignore_case = QRegularExpression.CaseInsensitiveOption
        builtins = [r"datetime", "from", "True"]
        urls = [
            "(http|https|ftp)://(\w+)\.(\w+)(\.?[\.a-z0-9/:?%&=\-_+#;\u4E00-\u9FA5]*)"
        ]
        debugs = [
            r"INFO(?=:)",
            r"DEBUG(?=:)",
            r"ERROR(?=:)",
            r"WARN(?=:)",
            r"WARNING(?=:)",
        ]
        exceptions = [r"Traceback \(most recent call last\):", r"\w+Error:.*"]
        file_pattern = (r"(?<!http|[\w\s]htt|http)([a-z]:)" +
                        r"(\\{1,2}|\/{1,2})" +
                        "[\.a-z0-9_\/\\\:\?\%\&\=\-_\+\#\;\u4E00-\u9FA5]*")
        normals = r"[^0-9]"

        self.rules.append((
            QRegularExpression(
                r"\b[+-]?[0-9]+[lL]?\b"
                r"|\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b"
                r"|\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b"),
            "number",
        ))

        self.rules.append((QRegularExpression(normals,
                                              ignore_case), "normals"))
        self.rules.append((
            QRegularExpression(
                r"(?<=\[)(scrapy|urllib3|root)(\.*\w*)*?(?=\])|referer:|get|post|?????????|?????????|?????????|????????????|????????????",
                ignore_case,
            ),
            "spider_names",
        ))
        self.rules.append((QRegularExpression(r"\d+-\d+-\d+\s\d+:\d+:\d+,\d+",
                                              ignore_case), "times"))
        self.rules.append((QRegularExpression(r"\[|\]|\(|\)|\{|\}|\>|\<",
                                              ignore_case), "symbols"))
        self.rules.append((QRegularExpression("|".join(builtins),
                                              ignore_case), "builtins"))
        self.rules.append((QRegularExpression(urls[0], ignore_case), "urls"))
        self.rules.append((QRegularExpression("|".join(debugs),
                                              ignore_case), "debugs"))
        self.rules.append((QRegularExpression("|".join(exceptions),
                                              ignore_case), "exceptions"))
        self.rules.append((QRegularExpression(r"\d+\.\s",
                                              ignore_case), "comments"))  # ??????
        self.rules.append((QRegularExpression(r"\".*?\"|\'.*?\'",
                                              ignore_case), "string"))
        self.rules.append((QRegularExpression(file_pattern,
                                              ignore_case), "files"))
        self.rules.append((
            QRegularExpression(
                "(?<=\[)[\u4E00-\u9FA5]*?(?=\])|(?<=\[)\-\-(?=\])",
                ignore_case),
            "sitenames",
        ))
        self.initializeFormats(getColorThemeManager())

    def retheme(self, theme_name_mode: str) -> None:
        if self.theme:
            baseFormat = QTextCharFormat()
            baseFormat.setFont(QFont("??????", 9))
            dic = self.theme.getThemeMode(theme_name_mode)
            for name in dic.keys():
                format = QTextCharFormat(baseFormat)
                format.setForeground(dic.get(name))
                if name in (
                        "debugs",
                        "exceptions",
                        "times",
                        "symbols",
                        "spider_names",
                        "comments",
                        "string",
                        "builtins",
                        "normals",
                        "number",
                        "sitenames",
                ):
                    format.setFontWeight(QFont.Bold)
                if name in ("urls", ):
                    # format.setFontItalic(True)
                    format.setFontUnderline(True)
                if name in ("files", ):
                    format.setFontUnderline(True)
                self.formats[name] = format
        self.rehighlight()

    def initializeFormats(self, theme: _ColorTheme) -> None:
        self.theme = theme
        baseFormat = QTextCharFormat()
        baseFormat.setFont(QFont("??????", 9))  # courier
        for name, dark, color in (
            ("normals", Qt.lightGray, Qt.black),
            ("spider_names", QColor("#667998"), QColor("#667998")),
            ("debugs", Qt.red, Qt.red),
            ("times", Qt.darkGreen, Qt.darkGreen),
            ("urls", QColor("#46A1FD"), Qt.darkBlue),
            ("files", QColor("#2EA3F1"), QColor("#2EA3F1")),
            ("comments", Qt.gray, Qt.gray),
            ("string", QColor("#D9EF60"), QColor("#972A98")),
            ("number", QColor("#F5F1E8"), QColor("#986112")),
            ("exceptions", QColor("#FD798F"), Qt.darkRed),
            ("sitenames", QColor("#7CA1BA"), QColor("#B2839F")),
            ("symbols", QColor("#EDEFD0"), Qt.black),
            ("builtins", Qt.darkYellow, Qt.darkYellow),
        ):
            format = QTextCharFormat(baseFormat)
            format.setForeground(QColor(color))
            if name in (
                    "debugs",
                    "exceptions",
                    "times",
                    "symbols",
                    "spider_names",
                    "comments",
                    "string",
                    "builtins",
                    "normals",
                    "number",
                    "sitenames",
            ):
                format.setFontWeight(QFont.Bold)
            if name in ("urls", ):
                format.setFontUnderline(True)
            if name in ("files", ):
                format.setFontUnderline(True)
            self.formats[name] = format
            self.theme.register(name, color, "debugtextbrowser.light")
            self.theme.register(name, dark, "debugtextbrowser.dark")

    def highlightBlock(self, text: str) -> None:
        for regex, format in self.rules:
            if isinstance(regex, QRegularExpression):
                iterator: QRegularExpressionMatchIterator = regex.globalMatch(
                    text)
                while iterator.hasNext():
                    match = iterator.next()
                    start = match.capturedStart()
                    length = match.capturedLength()
                    value = match.captured()
                    self.setFormat(start, length, self.formats[format])
            elif isinstance(regex, QRegExp):
                i = regex.indexIn(text)
                while i >= 0:
                    length = regex.matchedLength()
                    self.setFormat(i, length, self.formats[format])
                    i = regex.indexIn(text, i + length)


class FailHighlighter(QSyntaxHighlighter):
    rules = []

    formats = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ignore_case = QRegularExpression.CaseInsensitiveOption
        novel_name = "^.+(?=\s\d+\-\d+\-\d+)|(?<=\:\s).+(?=\s\-\-)"
        time = r"\d+\-\d+\-\d+ \d{2}\:\d{2}\:\d{2}\.\d+"
        symbols = r"????????????|????????????|?????????|?????????|????????????"
        chapter_name = "(?<=\-\-\s).*(?=http)*"
        urls = (
            "(http|https|ftp)://(\w+)\.(\w+)(\.?[\.a-z0-9/:?%&=\-_+#;\u4E00-\u9FA5]*)"
        )
        characters = r"\[|\]"
        exception = r"\w+"
        self.rules.append((QRegularExpression(exception,
                                              ignore_case), "exception"))
        self.rules.append((QRegularExpression(novel_name,
                                              ignore_case), "novel_name"))
        self.rules.append((QRegularExpression(time, ignore_case), "time"))
        self.rules.append((QRegularExpression(symbols,
                                              ignore_case), "symbols"))
        self.rules.append((QRegularExpression(chapter_name,
                                              ignore_case), "chapter_name"))
        self.rules.append((QRegularExpression(urls, ignore_case), "urls"))
        self.rules.append((QRegularExpression(characters,
                                              ignore_case), "characters"))

        self.initializeFormats()

    def setNovelNameFormat(self,
                           font_family: str,
                           font_size=9,
                           *,
                           font: QFont = None) -> None:
        novelFormat = QTextCharFormat()
        if font:
            novelFormat.setFont(font)
        else:
            novelFormat.setFont(QFont(font_family, font_size))
        format = QTextCharFormat(novelFormat)
        format.setForeground(QColor("#0B2942"))
        self.formats["novel_name"] = format

    def initializeFormats(self) -> None:
        baseFormat = QTextCharFormat()
        baseFormat.setFont(QFont("??????", 9))
        for name, color in (
            ("novel_name", QColor("#0B2942")),
            ("symbols", Qt.red),
            ("chapter_name", QColor("#AF521F")),
            ("time", Qt.darkGreen),
            ("urls", Qt.darkBlue),
            ("exception", QColor("#2A2A2E")),
            ("characters", Qt.black),
        ):
            format = QTextCharFormat(baseFormat)
            format.setForeground(QColor(color))
            if name == "exception":
                format.setFontWeight(QFont.Bold)
            if name == "urls":
                format.setFontUnderline(True)
            self.formats[name] = format

    def highlightBlock(self, text: str) -> None:
        for regex, format in self.rules:
            iterator: QRegularExpressionMatchIterator = regex.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                value = match.captured()
                self.setFormat(start, length, self.formats[format])


class InfoLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_TransparentForMouseEvents,
                          True)  # ????????????,???????????????????????????????????????????????????
        self._cu = time.time()
        self.startTimer(1000)

    def timerEvent(self, event):
        now = time.time()
        if now - self._cu >= 10:
            self.setText("")

    def setText(self, value: str) -> None:
        super().setText(value)
        self._cu = time.time()


class HistoryComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_len = 10
        self.history = deque(maxlen=self.max_len)
        self.search_line = HistoryLineEdit(max_len=self.max_len)
        self.search_line.setPlaceholderText("????????????????????????")
        self.search_line.setHistoryMaxLength(self.max_len)
        view = QListView()
        font = QFont("????????????", 9)
        font.setBold(True)
        view.setFont(font)
        view.setStyleSheet(StyleSheets.historycombobox_listview_style)
        self.setView(view)
        self.setLineEdit(self.search_line)
        self.setStyleSheet(StyleSheets.historycombobox_style)
        self.setContextMenuPolicy(Qt.NoContextMenu)

    def setMaxLength(self, length: int) -> None:
        self.max_len = length

    def clearItems(self) -> None:
        self.clear()
        self.s_line.clearHistories()

    def appendTop(self, text: str) -> bool:
        if text and (text not in self.history):
            self.history.appendleft(text)
            if len(self.history) < self.max_len:
                self.insertItem(0, text)
            else:
                for i in range(self.max_len):
                    self.setItemText(i, self.history[i])
            return True
        return False

    def appendBottom(self, text: str) -> bool:
        if text and (text not in self.history):
            self.history.append(text)
            if len(self.history) < self.max_len:
                self.addItem(text)
            else:
                for i in range(self.max_len):
                    self.setItemText(i, self.history[i])
            return True
        return False

    def extendLogs(self, values: Sequence[str]) -> None:
        for value in values:
            self.appendBottom(value)

    def searchLogs(self) -> List[str]:
        result = []
        for i in range(self.count()):
            result.append(self.itemText(i))
        return result


class FontCombobox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_len = 10
        self.font_line = QLineEdit()
        self.font_line.setStyleSheet("color:white")
        self.font_line.setReadOnly(True)
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(StyleSheets.font_combo_listwidget_style)
        self.setView(self.list_widget)
        self.setModel(self.list_widget.model())
        self.setLineEdit(self.font_line)
        self.setContextMenuPolicy(Qt.NoContextMenu)

    def addFontTag(self, font_name: str, font: QFont = None) -> None:
        item = QListWidgetItem()
        if font is None:
            item.setFont(QFont(font_name, 10))
        else:
            font = QFont(font)
            font.setPointSize(10)
            item.setFont(font)
        item.setText(font_name)
        self.list_widget.addItem(item)

    def getFontFamily(self, index: int) -> str:
        item = self.list_widget.item(index)
        return item.font().family()

    def setCurrent(self, family: str) -> None:
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.font().family() == family:
                text = item.text()
                self.font_line.setText(text)
                self.setCurrentIndex(i)
                break


class HistoryLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        self.max_len = kwargs.pop("max_len", 10)
        super().__init__(*args, **kwargs)
        self.__short = QShortcut(Qt.Key_Tab,
                                 self,
                                 activated=self._tab_change_value)
        self.state = 0  # 0?????????;1?????????;2????????????
        self.histories = deque(maxlen=self.max_len)

    def setHistoryMaxLength(self, length: int) -> None:
        self.max_len = length
        copyed = list(self.histories)
        self.histories = deque(maxlen=length)
        for value in copyed:
            self.histories.append(value)

    def setHistories(self, records: Sequence[str]) -> None:
        self.histories.clear()
        self.histories.extend(records)
        completer = QCompleter(records)
        completer.setCompletionMode(QCompleter.InlineCompletion)
        self.setCompleter(completer)

    def clearHistories(self) -> None:
        self.histories.clear()
        self.completer().model().setStringList([])

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            text = self.text().strip()
            self._addHistory(text)
        super().keyPressEvent(event)

    def _addHistory(self, text: str) -> None:
        if text not in self.histories:
            self.histories.appendleft(text)
            self.completer().model().setStringList(self.histories)

    def _tab_change_value(self) -> None:
        text = self.text().strip()
        if text == "":
            if len(self.histories) > 0:
                self.setText(self.histories[0])
        else:
            if len(self.histories) > 0:
                self.clear()
                index = self.histories.index(text)
                if index == len(self.histories) - 1:
                    index = -1
                index += 1
                next_value = self.histories[index]
                self.setText(next_value)


class MenuButton(QPushButton):
    def __init__(self,
                 check_icon: str,
                 uncheck_icon: str,
                 button_size: int,
                 icon_scaled: tuple = (0.7, 0.7),
                 start_state: bool = True,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.check_tip = None
        self.uncheck_tip = None
        self.icon_scaled = icon_scaled
        self.buttonSize = button_size
        icon = QIcon()
        icon.addFile(check_icon, state=QIcon.On)
        icon.addFile(uncheck_icon, state=QIcon.Off)
        self.setIcon(icon)
        self.setIconSize(
            QSize(button_size * icon_scaled[0], button_size * icon_scaled[1]))
        self.setCheckable(True)
        self.setChecked(start_state)
        self.setStyleSheet(StyleSheets.menu_button_style)
        self.onClicked()
        self.clicked.connect(self.onClicked)

    @property
    def buttonSize(self) -> int:
        return self.size().height()

    @buttonSize.setter
    def buttonSize(self, value: int) -> None:
        self.setFixedSize(QSize(value, value))
        self.setIconSize(
            QSize(value * self.icon_scaled[0], value * self.icon_scaled[1]))

    def setToolTips(self, check_tip: str, uncheck_tip: str) -> None:
        self.check_tip = check_tip
        self.uncheck_tip = uncheck_tip
        self.onClicked()

    def onClicked(self) -> None:
        if self.isChecked():
            self.setToolTip(self.check_tip if self.check_tip else "")
        else:
            self.setToolTip(self.uncheck_tip if self.uncheck_tip else "")


class OpacityStackWidget(QStackedWidget):  # ????????????
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_widget = None
        self.current_index = -1
        self.opacity = QGraphicsOpacityEffect()
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.valueChanged.connect(self._upDateOpacity)
        self.animation.finished.connect(self.finish_slot)
        self.setDuration()

    def finish_slot(self) -> None:
        super().setCurrentIndex(self.current_index)

    def _upDateOpacity(self, value: float) -> None:
        self.opacity.setOpacity(value)
        if self.current_widget is None:
            self.current_widget = self.currentWidget()
        self.current_widget.setGraphicsEffect(self.opacity)

    def setCurrentIndex(self, index: int, with_animation: bool = True) -> None:
        self.current_widget = self.currentWidget()
        self.current_index = index
        if index == self.currentIndex():
            return
        if with_animation:
            self.animation.start()
        else:
            super().setCurrentIndex(index)

    def setDuration(self, value: int = 150) -> None:
        self.animation.setDuration(value)


class AnimationStackWidget(QStackedWidget):  # ????????????
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.animation = QPropertyAnimation(self, b'')
        self.duration = 1000  #???????????????????????????
        self.isAnimation = False
        self.currentValue = None
        self.widgetCount = 0
        self.nextIndex = -1
        #?????????animation??????????????????????????????
        self.animation.valueChanged.connect(self.valueChanged_slot)
        self.animation.finished.connect(self.animationFinished)

    def paintEvent(self, event) -> None:
        if self.isAnimation:
            paint = QPainter(self)
            #????????????Widget
            self.paintPrevious(paint, self.currentIndex())
            #???????????????widget
            self.paintNext(paint, self.nextIndex)

    def setDuration(self, duration: int) -> None:
        self.duration = duration

    # ???????????????????????????
    def valueChanged_slot(self, value: Union[int, float]) -> None:
        self.currentValue = value
        self.update()

    # ??????????????????
    def animationFinished(self) -> None:
        self.isAnimation = False
        self.widget(self.currentIndex()).show()
        self.setCurrentIndex(self.nextIndex)

    def setCurrentTarget(self, index: int) -> None:
        if index == self.currentIndex():
            return
        if self.isAnimation:
            return
        self.isAnimation = True
        self.widgetCount = self.count()
        c = self.currentIndex()
        #????????????????????????
        self.nextIndex = index
        #???????????????widget
        self.widget(c).hide()
        #????????????????????????????????????????????????
        g = self.geometry()
        x = g.x()
        width = g.width()
        self.animation.setStartValue(width)
        self.animation.setEndValue(0)
        self.animation.setDuration(self.duration)
        self.animation.start()

    def next(self) -> None:
        if self.isAnimation:
            return
        self.isAnimation = True
        self.widgetCount = self.count()
        c = self.currentIndex()
        #????????????????????????
        self.nextIndex = (c + 1) % self.widgetCount
        #???????????????widget
        self.widget(c).hide()
        #????????????????????????????????????????????????
        g = self.geometry()
        x = g.x()
        width = g.width()
        self.animation.setStartValue(width)
        self.animation.setEndValue(0)
        self.animation.setDuration(self.duration)
        self.animation.start()

    def forward(self) -> None:
        if self.isAnimation:
            return
        self.isAnimation = True
        self.widgetCount = self.count()
        c = self.currentIndex()
        #????????????????????????
        self.nextIndex = (c - 1) % self.widgetCount
        #???????????????widget
        self.widget(c).hide()
        #????????????????????????????????????????????????
        g = self.geometry()
        x = g.x()
        width = g.width()
        self.animation.setStartValue(width)
        self.animation.setEndValue(0)
        self.animation.setDuration(self.duration)
        self.animation.start()

    def paintPrevious(self, painter: QPainter, currentIndex: int) -> None:
        w = self.widget(currentIndex)
        pixmap = QPixmap(w.size())
        #???Widget??????????????????QPixmap??????????????????Widget??????????????????
        w.render(pixmap)
        r = w.geometry()
        #???????????????Widget
        value = self.currentValue
        r1 = QRectF(0.0, 0.0, value, r.height())
        r2 = QRectF(r.width() - value, 0, value, r.height())
        painter.drawPixmap(r1, pixmap, r2)

    def paintNext(self, painter: QPainter, nextIndex: int) -> None:
        nextWidget = self.widget(nextIndex)
        r = self.geometry()
        #????????????????????????bug??????????????????????????????QStackedWidget????????????child????????????
        nextWidget.resize(r.width(), r.height())
        nextPixmap = QPixmap(nextWidget.size())
        nextWidget.render(nextPixmap)
        value = self.currentValue
        r1 = QRectF(value, 0.0, r.width() - value, r.height())
        r2 = QRectF(0.0, 0.0, r.width() - value, r.height())
        painter.drawPixmap(r1, nextPixmap, r2)


class FlagAction(IntEnum):
    first_in = 0
    next_chapter = 1
    previous_chapter = 2
    jump_chapter = 3
    scroll_to_split = 4  # ???????????????
    split_to_scroll = 5  # ???????????????
    undefined = 6  # ?????????
    from_bookmark = 7  # ??????????????????


class BaseTaskReadPropertys(object):
    def __init__(self, *args, **kwargs) -> None:
        self.task_widget: 'TaskWidget' = kwargs.pop('task_widget', None)
        self.flag: FlagAction = FlagAction.undefined
        self.messages: dict = None
        self.current_index: int = -1
        self.current_book: str = ''
        self.current_mark: Markup = None
        self.indent_size = 20
        self.margin_size = 40
        self.font_size = 15
        self.letter_spacing = 2
        self.font_family = "TsangerJinKai04 W03"
        self.line_height = 5
        self.is_textmenu = False

    @lasyproperty
    def read_loader(self) -> ChapterDownloader:
        loader = ChapterDownloader(QSemaphore(20), self.info)
        loader.single_signal.connect(self.updateChapter)
        loader.single_fail_signal.connect(self.failUpdateChapter)
        return loader

    @property
    def info(self) -> InfoObj:
        return self.task_widget._inf

    def exists_chapters(self) -> List[int]:
        inf = self.info
        rqir = inf.read_qdir()
        return self.read_loader.exits_chapters(rqir, inf)

    @lasyproperty
    def _bkg_color(self) -> QColorDialog:
        color = TaskReadColorDialog(self)
        color.setWindowFlag(Qt.FramelessWindowHint)
        color.hide()
        return color

    def show_bkg_color(self, color: Any) -> None:
        self._bkg_color.setCurrentColor(QColor(color))
        self._bkg_color.exec_()

    @lasyproperty
    def _text_color(self) -> QColorDialog:
        color = TaskBkgColorDialog(self)
        color.setWindowFlag(Qt.FramelessWindowHint)
        color.hide()
        return color

    def show_text_color(self, color: Any) -> None:
        self._text_color.setCurrentColor(QColor(color))
        self._text_color.exec_()

    def _show_marks(self) -> None:
        self.task_widget.showChaptersWidget(True)
        self.task_widget.chapters_widget.pushButton_4.click()

    def _show_chapters(self) -> None:
        self.task_widget.showChaptersWidget(True)
        self.task_widget.chapters_widget.pushButton_3.click()
        self.task_widget.updateRequestState()

    def chapters(self) -> List[str]:
        res = []
        for u, c, s in self.info.novel_chapter_urls:
            res.append(c)
        return res

    def request_chapter(self,
                        url_index: int,
                        chapter_name: str = "",
                        current_book: str = "",
                        family: str = "",
                        indent: int = 20,
                        margin: int = 40,
                        font_size: int = 15,
                        letter_spacing: int = 2,
                        line_height: int = 5,
                        flag: FlagAction = FlagAction.first_in,
                        **kwargs) -> None:
        self.flag = flag
        self.indent_size = indent
        self.margin_size = margin
        self.font_size = font_size
        self.font_family = family
        self.letter_spacing = letter_spacing
        self.line_height = line_height
        self.current_index = url_index
        self.current_book = current_book
        self.read_loader.readChapter(url_index, chapter_name, self.info)

    def next_chapter(self) -> None:
        index = self.current_index + 1
        if index <= self.info.chapter_count() - 1:
            chapter_name = self.info.novel_chapter_urls[index][1]
            self.request_chapter(
                index,
                chapter_name,
                self.current_book,
                self.font_family,
                self.indent_size,
                self.margin_size,
                self.font_size,
                self.letter_spacing,
                self.line_height,
                flag=FlagAction.next_chapter,
            )

    def preview_chapter(self) -> None:
        index = self.current_index - 1
        if index >= 0:
            chapter_name = self.info.novel_chapter_urls[index][1]
            self.request_chapter(
                index,
                chapter_name,
                self.current_book,
                self.font_family,
                self.indent_size,
                self.margin_size,
                self.font_size,
                self.letter_spacing,
                self.line_height,
                flag=FlagAction.next_chapter,
            )

    def jump_chapter(self, index: int, percent: float = 0) -> None:
        chapter_name = self.info.novel_chapter_urls[index][1]
        self.jump_percent = percent
        self.request_chapter(
            index,
            chapter_name,
            self.current_book,
            self.font_family,
            self.indent_size,
            self.margin_size,
            self.font_size,
            self.letter_spacing,
            self.line_height,
            flag=FlagAction.jump_chapter,
        )

    def _customTextMenu(self) -> None:
        pala = self.palette()
        bkg_color = pala.color(QPalette.Background).name()
        text_color = pala.color(QPalette.Text).name()

        font = QFont("????????????", 9)
        menu = QMenu(self)
        menu.setStyleSheet(StyleSheets.dynamic_menu_style %
                           (text_color, text_color, text_color, bkg_color))
        menu.setFixedWidth(menu.fontMetrics().widthChar("???") * 10 + 5)
        l_style = "QLabel{color:%s; background:%s;font-family:????????????;font-size:9pt;font-weight:bold}QLabel:hover{background:%s;color:%s}" % (
            bkg_color, text_color, bkg_color, text_color)
        l_height = QFontMetrics(font).height() * 1.6

        a0 = None
        if self.textCursor().hasSelection():
            l0 = QLabel('??????????????????')
            l0.setFixedHeight(l_height)
            l0.setAlignment(Qt.AlignCenter)
            l0.setStyleSheet(l_style)
            a0 = QWidgetAction(menu)
            a0.setDefaultWidget(l0)
            menu.addAction(a0)

        l1 = QLabel("????????????")
        l2 = QLabel("????????????")
        l3 = QLabel("????????????")
        l4 = QLabel("????????????")
        l1.setFixedHeight(l_height)
        l2.setFixedHeight(l_height)
        l3.setFixedHeight(l_height)
        l4.setFixedHeight(l_height)

        l1.setAlignment(Qt.AlignCenter)
        l2.setAlignment(Qt.AlignCenter)
        l3.setAlignment(Qt.AlignCenter)
        l4.setAlignment(Qt.AlignCenter)
        l1.setStyleSheet(l_style)
        l2.setStyleSheet(l_style)
        l3.setStyleSheet(l_style)
        l4.setStyleSheet(l_style)

        a1 = QWidgetAction(menu)
        a2 = QWidgetAction(menu)
        a3 = QWidgetAction(menu)
        a4 = QWidgetAction(menu)

        a1.setDefaultWidget(l1)
        a2.setDefaultWidget(l2)
        a3.setDefaultWidget(l3)
        a4.setDefaultWidget(l4)

        menu.addAction(a1)
        menu.addAction(a2)
        menu.addAction(a3)
        menu.addAction(a4)

        act = menu.exec_(QCursor.pos())
        self.is_textmenu = True
        if act == a4:
            self._exit_read()
        elif act == a1:
            self._add_mark()
        elif act == a2:
            self._show_marks()
        elif act == a3:
            self._show_chapters()
        elif act == a0:
            QApplication.clipboard().setText(self.textCursor().selectedText())
        self.is_textmenu = False

    def _exit_read(self):  # ????????????
        self.task_widget.exit_button.click()

    @pyqtSlot(dict)  # ????????????
    def updateChapter(self, messages: dict) -> None:
        pass

    @pyqtSlot(dict)  # ????????????
    def failUpdateChapter(self, message: dict) -> None:
        pass

    def renderOk(self, *args, **kwargs) -> str:
        pass

    def renderFail(self, *args, **kwargs) -> str:
        pass

    def flushLatested(self, p_value: int = None):  # ????????????????????????
        pass

    def readTextColor(self) -> str:
        pass

    def readBackColor(self) -> str:
        pass

    def selectionText(self) -> str:
        pass


PageContents = Union[List['_AutoLine'], List['_AutoPage']]


class MySequence(MutableSequence):
    @abstractmethod
    def _container_(self):
        pass

    def __getitem__(self, index):
        return self._container_()[index]

    def __setitem__(self, index, value):
        self._container_()[index] = value

    def __delitem__(self, index):
        del self._container_()[index]

    def __len__(self):
        return len(self._container_())

    def insert(self, index: int, value: PageContents):
        self._container_().insert(index, value)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{self._container_()}'

    def __add__(self, other: '_AutoPages'):
        self._container_() + other._containter_()

    @abstractmethod
    def copy(self):
        pass

    def __deepcopy__(self, memo):
        return self.copy()


class _AutoPages(MySequence):

    __slots__ = ('pages', )

    def __init__(self) -> None:
        self.pages: PageContents = []

    def _container_(self):
        return self.pages

    def copy(self) -> '_AutoPages':
        res = _AutoPages()
        pages = deepcopy(self.pages)
        res.pages = pages
        return res

    def split_page(self,
                   page_count: int,
                   start: int = None,
                   stop: int = None,
                   step: int = None) -> '_AutoPages':  # ??????, lines -> pages
        flag = start or stop or step
        if flag is None:
            dst = self._container_()
        else:
            dst = self._container_()[slice(start, stop, step)]
        pages = [
            _AutoPage(dst[i:i + page_count])
            for i in range(0, len(dst), page_count)
        ]
        result = _AutoPages()
        result.pages = pages
        return result

    def addLines(self,
                 lines: List[str],
                 compute_func: Callable,
                 args=(),
                 kwargs={},
                 first_title: bool = True) -> None:  # ?????????
        self.clear()
        for line in lines:
            self._addLine(compute_func(line, *args, **kwargs))
        if self:
            self[0][-1] = first_title

    def _addLine(self, lines: List[str]):
        i = -1
        for line in lines:
            i += 1
            has_indent = True if i == 0 else False
            self.append(_AutoLine(line, has_indent, False))


class _AutoPage(MySequence):

    __slots__ = ('lines', )

    def __init__(self, lines: List['_AutoLine'] = None) -> None:
        self.lines = lines or []

    def _container_(self):
        return self.lines

    def copy(self) -> '_AutoPage':
        lines = deepcopy(self.lines)
        return _AutoPage(lines)


class _AutoLine(MySequence):

    __slots__ = ('line', )

    def __init__(self,
                 content: str = '',
                 has_indent: bool = False,
                 is_title: bool = False,
                 content_index: int = -1,
                 content_pos: int = -1) -> None:
        self.line = [content, has_indent, is_title, content_index, content_pos]

    def _container_(self):
        return self.line

    def copy(self) -> '_AutoLine':
        content, has_indent, is_title, c_index, c_pos = self
        return _AutoLine(content, has_indent, is_title, c_index, c_pos)

    @property
    def content(self):
        return self[0]

    @property
    def has_indent(self):
        return self[1]

    @property
    def is_title(self):
        return self[2]

    @property
    def content_index(self):
        return self[3]

    @property
    def content_pos(self):
        return self[4]


class AutoSplitContentTaskReadWidget(QWidget,
                                     BaseTaskReadPropertys):  # ????????????????????????
    class MouseAvtion(IntEnum):
        undefined = -1
        next_chapter = 0
        previous_chapter = 1
        context_click = 2

    def _customTextMenu(self) -> None:
        def exit_context():
            self.is_textmenu = False

        bkg_color = self.bkg_color.name()
        text_color = self.text_color.name()

        font = QFont("????????????", 9)
        menu = QMenu(self)
        menu.setStyleSheet(StyleSheets.dynamic_menu_style %
                           (text_color, text_color, text_color, bkg_color))
        menu.setFixedWidth(menu.fontMetrics().widthChar("???") * 10 + 5)
        l_style = "QLabel{color:%s; background:%s;font-family:????????????;font-size:9pt;font-weight:bold}QLabel:hover{background:%s;color:%s}" % (
            bkg_color, text_color, bkg_color, text_color)
        l_height = QFontMetrics(font).height() * 1.6

        l2 = QLabel("????????????")
        l3 = QLabel("????????????")
        l4 = QLabel("????????????")

        l2.setFixedHeight(l_height)
        l3.setFixedHeight(l_height)
        l4.setFixedHeight(l_height)

        l2.setAlignment(Qt.AlignCenter)
        l3.setAlignment(Qt.AlignCenter)
        l4.setAlignment(Qt.AlignCenter)

        l2.setStyleSheet(l_style)
        l3.setStyleSheet(l_style)
        l4.setStyleSheet(l_style)

        a2 = QWidgetAction(menu)
        a3 = QWidgetAction(menu)
        a4 = QWidgetAction(menu)

        a2.setDefaultWidget(l2)
        a3.setDefaultWidget(l3)
        a4.setDefaultWidget(l4)

        menu.addAction(a2)
        menu.addAction(a3)
        menu.addAction(a4)

        act = menu.exec_(QCursor.pos())
        self.is_textmenu = True
        if act == a4:
            self._exit_read()
            self.is_textmenu = False
        elif act == a2:
            self._show_marks()
            self.is_textmenu = False
        elif act == a3:
            self._show_chapters()
            self.is_textmenu = False
        else:
            self.context_timer.singleShot(100, exit_context)

    @property
    def read_font(self):
        return self._read_font

    @read_font.setter
    def read_font(self, font: QFont):
        self.font_family = font.family()
        self.font_size = font.pointSize()
        self._read_font = font
        self._read_font.setLetterSpacing(QFont.AbsoluteSpacing,
                                         self.letter_spacing)
        self._title_font = QFont(self._read_font)
        self._title_font.setPointSize(max(16, self.font_size + 2))

    @property
    def current_chapter(self) -> str:
        if self.chapter_content:
            return self.chapter_content[0].strip()
        return ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._read_font = QFont(self.font_family, self.font_size)
        self._read_font.setLetterSpacing(QFont.AbsoluteSpacing,
                                         self.letter_spacing)

        self._title_font = QFont(self._read_font)
        self._title_font.setPointSize(max(16, self.font_size + 2))

        self.bkg_color = Qt.white
        self.text_color = Qt.black
        self.current_page = 0
        self.dst_page = 0
        self.auto_pages: _AutoPages = _AutoPages()
        self._page_count: int = 0
        self.chapter_content: List[str] = None
        self.by_first_line: str = None
        self.is_title: bool = None
        self.content_length: int = 0
        self.mouse_action = self.MouseAvtion.undefined
        self.read_layout = QVBoxLayout(self)
        self.read_layout.setSpacing(self.line_height)
        self.read_layout.setContentsMargins(0, 0, 0, 0)

        self.change_animation = QPropertyAnimation()
        self.change_animation.valueChanged.connect(self._updateAnimation)
        self.change_animation.finished.connect(self._finishAnimation)
        self.change_type = 0  # ?????????, 1????????????

        self.context_timer = QTimer(self)  #

        self.setReadStyle()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._customTextMenu)

    @lasyproperty
    def opacity(self):
        return QGraphicsOpacityEffect()

    def _finishAnimation(self) -> None:
        MouseAction = self.MouseAvtion
        if self.mouse_action == MouseAction.next_chapter:
            self.next_chapter()
        elif self.mouse_action == MouseAction.previous_chapter:
            self.preview_chapter()
        self.opacity.setOpacity(1)
        self.setGraphicsEffect(self.opacity)

    def _updateAnimation(self, value: float) -> None:
        if self.change_type == 1:
            self.opacity.setOpacity(value)
            self.setGraphicsEffect(self.opacity)

    @property
    def change_type(self):
        return self.__change_type

    @change_type.setter
    def change_type(self, type: int):
        self.__change_type = type
        if type == 1:
            self.change_animation.setTargetObject(self)
            self.change_animation.setPropertyName(b'windowOpacity')
            self.change_animation.setStartValue(1)
            self.change_animation.setEndValue(0)
            self.change_animation.setDuration(200)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            if self.task_widget.more_widget.isHidden(
            ) and self.is_textmenu == False:
                if event.pos().x() <= (self.width() / 2):
                    self.mouse_action = self.MouseAvtion.previous_chapter
                    if self.change_type == 0:
                        self.preview_chapter()
                    elif self.change_type == 1:
                        self.change_animation.start()
                else:
                    self.mouse_action = self.MouseAvtion.next_chapter
                    if self.change_type == 0:
                        self.next_chapter()
                    elif self.change_type == 1:
                        self.change_animation.start()
            if not self.task_widget.more_widget.isHidden():
                self.task_widget.more_widget.hide()

        return super().mousePressEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        super().wheelEvent(event)
        if event.angleDelta().y() > 0:
            self.preview_chapter()
        else:
            self.next_chapter()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.read_width = self.width() - 10
        self.read_height = self.height()
        first_line, has_indent, is_title, content_index, content_pos = self.first_line(
        )
        self._clearReadLines()
        if self.chapter_content and self.sender() is None:
            # print('resize: ', first_line, is_title, content_index)
            self.computePages(self.chapter_content,
                              self.current_page,
                              by_first_line=first_line,
                              is_title=is_title)
            msg = self.current_chapter + f'({self.current_page+1}/{self.pageCount()})'
            self.task_widget.load_chapter_init(msg)
            self.update_latest()
            # print('-' * 20)

    @pyqtSlot(dict)  # ????????????
    def updateChapter(self, messages: dict) -> None:
        latest = self.info.getLatestRead()
        content = messages['content']
        content.insert(0, messages['chapter'])
        chapter_name = messages["chapter"]
        if self.flag == FlagAction.first_in:  # ????????????
            self.computePages(content,
                              latest.percent,
                              by_first_line=latest.line,
                              is_title=latest.is_title)  # ???percent??????
            msg = chapter_name + f'({self.current_page + 1}/{self.pageCount()})'

        elif self.flag == FlagAction.next_chapter:  # next
            self.computePages(content)
            msg = chapter_name + f'(1/{self.pageCount()})'

        elif self.flag == FlagAction.previous_chapter:  # previous
            self.computePages(content, self.dst_page, dst_flag=True)
            msg = chapter_name + f'({self.current_page+1}/{self.pageCount()})'

        elif self.flag == FlagAction.jump_chapter:  # jump
            self.computePages(content, self.current_page)
            msg = chapter_name + f'({self.current_page+1}/{self.pageCount()})'

        elif self.flag == FlagAction.scroll_to_split:  # ????????????
            self.computePages(content,
                              latest.percent,
                              by_first_line=self.by_first_line,
                              is_title=False)
            msg = chapter_name + f'({self.current_page+1}/{self.pageCount()})'

        elif self.flag == FlagAction.from_bookmark:
            self.computePages(content,
                              latest.percent,
                              by_first_line=self.by_first_line,
                              is_title=False)
            msg = chapter_name + f'({self.current_page+1}/{self.pageCount()})'
        self.task_widget.load_chapter_init(msg)
        self.content_length = len(''.join(content))
        # print('request ok--', end='')
        self.update_latest()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        use_custom = self.task_widget.more_widget.use_custom
        use_cust_image = self.task_widget.more_widget.use_cust_image
        if self.bkg_image and use_custom and use_cust_image:
            painter = QPainter()
            painter.begin(self)
            painter.drawPixmap(self.rect(), QPixmap(self.bkg_image))
            painter.end()
        elif self.bkg_image and use_custom == False:
            painter = QPainter()
            painter.begin(self)
            painter.drawTiledPixmap(self.rect(), QPixmap(self.bkg_image))
            painter.end()

    def _split_from_lines(self,
                          lines: list,
                          current_page: int,
                          dst_flag: bool = False):
        height = self._textHeight()
        title_height = self._titleHeight()
        self.chapter_content = lines
        self._addLines(lines)
        label_counts = int((self.read_height + height - title_height) /
                           (self.line_height + height))  # title,??????
        p1 = self.auto_pages.split_page(label_counts)[0]
        # p1 = self._split_sequence(self.auto_pages, label_counts)[0]

        label_counts = int(
            (self.read_height) / (self.line_height + height))  # content ??????
        p2 = self.auto_pages.split_page(label_counts, len(p1))
        p2.insert(0, p1)

        self.auto_pages = p2
        self._page_count = len(p2)
        # self.current_page = index if index >=0 else len(self._p_lines) + index
        self.current_page = current_page if not dst_flag else len(
            self.auto_pages) + current_page
        self.read_layout.addSpacing(self.line_height)
        try:
            for line in self.auto_pages[self.current_page]:
                self._setReadLine(line, height)
        except IndexError:
            self.current_page = self._page_count - 1
            for line in self.auto_pages[self.current_page]:
                self._setReadLine(line, height)
        self.read_layout.addStretch()

    def computePages(self,
                     lines: list,
                     index: int = 0,
                     dst_flag: bool = False,
                     by_first_line: str = None,
                     is_title: bool = True):  # ????????????????????????

        latested = self.info.getLatestRead()
        height = self._textHeight()
        title_height = self._titleHeight()
        self.chapter_content = lines

        if is_title is not None:
            self.is_title = is_title

        if self.is_title:
            self._split_from_lines(lines, index, dst_flag)

        elif by_first_line is not None and by_first_line.strip(
        ) == latested.chapter_name:  # first
            self._split_from_lines(lines, 0, dst_flag)

        elif by_first_line is not None and by_first_line and is_title == False:
            self.by_first_line = by_first_line
            if latested.content_index > -1:
                pint = max(1, latested.content_index)
                # print('byfirst: ', by_first_line, pint)
            else:
                for i, line in enumerate(self.chapter_content):
                    if by_first_line in line:
                        pint = i
                        break
                pint = max(1, pint)
                # print('sss', i)
            self._addLines(self.chapter_content[:pint])  # ???????????????
            label_counts = int((self.read_height + height - title_height) /
                               (self.line_height + height))  # title,??????

            p1: _AutoPage = self.auto_pages.split_page(label_counts)[0]
            # p1 = self._split_sequence(self.auto_pages, label_counts)[0]
            label_counts = int(
                (self.read_height) / (self.line_height + height))  # content ??????
            p2 = self.auto_pages.split_page(label_counts, len(p1))
            p2.insert(0, p1)

            lp2 = len(p2)
            self.auto_pages = p2
            copyed_pages = self.auto_pages.copy()
            line_counts = copyed_pages[-1][-1].content_index + 1
            self._addLines(self.chapter_content[pint:], False, start=line_counts)
            p = self.auto_pages.split_page(label_counts)
            copyed_pages.extend(p)
            self.auto_pages = copyed_pages

            self._page_count = len(self.auto_pages)
            self.current_page = lp2
            self.read_layout.addSpacing(self.line_height)
            for line in self.auto_pages[self.current_page]:
                self._setReadLine(line, height)
            self.read_layout.addStretch()

    def first_line(self) -> _AutoLine:
        for i in range(self.read_layout.count()):
            item = self.read_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    label = widget.label
                    # if label.p_first_flag:
                    return label.line
        return _AutoLine()

    def current_page_line_counts(self) -> int:  # ????????????????????????
        count = 0
        for i in range(self.read_layout.count()):
            item = self.read_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    count += 1
        return count

    def update_latest(self) -> None:  # ????????????????????????
        auto_line = self.first_line()
        # print('in update: ', auto_line.content, auto_line.content_index)
        latested = self.info.getLatestRead()
        latested.index = self.current_index
        latested.chapter_name = self.current_chapter
        latested.percent = self.current_page
        latested.line = auto_line.content
        latested.content_index = auto_line.content_index
        latested.content_pos = auto_line.content_pos

        if latested.line.strip() == latested.chapter_name:
            latested.is_title = True
        else:
            latested.is_title = False
        if self.content_length:
            pages = self.auto_pages[:self.current_page]
            page_lines = [lines[0] for page in pages for lines in page]
            latested.float_percent = len(
                ''.join(page_lines)) / self.content_length
            # read_info.min, read_info.max, read_info.value = text_browser.barRangeandValue()
        # print('update_latested: ', latested.line, latested.content_index)

    def setReadStyle(self, bkg_color=None, text_color=None, bkg_image=None):
        self.bkg_color = QColor(
            self.bkg_color) if bkg_color is None else QColor(bkg_color)
        self.text_color = QColor(
            self.text_color) if text_color is None else QColor(text_color)
        self.bkg_image = bkg_image
        sytles = 'QLabel{color: %s} QFrame{background:transparent} AutoSplitContentTaskReadWidget{background: %s}' % (
            self.text_color.name(), self.bkg_color.name())
        self.setStyleSheet(sytles)

    def setTextColor(self, color):
        self.text_color = QColor(color)
        self.update()

    def setBkgColor(self, color):
        self.bkg_color = QColor(color)
        self.update()

    def setBkgImage(self, image: str):
        self.bkg_image = image
        self.update()

    def pageCount(self) -> int:  # ????????????
        return self._page_count

    def next_page(self):
        height = self._textHeight()
        next_index = (self.current_page + 1) % self.pageCount()
        if next_index > 0:
            self.current_page = next_index
            self._clearReadLines()
            self.read_layout.addSpacing(self.line_height)
            for line in self.auto_pages[self.current_page]:
                self._setReadLine(line, height)
            self.read_layout.addStretch()
            self.update_latest()

    def previous_page(self):
        height = self._textHeight()
        previous = (self.current_page - 1) % self.pageCount()

        if previous < self.pageCount() - 1:
            self.current_page = previous
            self._clearReadLines()
            self.read_layout.addSpacing(self.line_height)
            for line in self.auto_pages[self.current_page]:
                self._setReadLine(line, height)
            self.read_layout.addStretch()
            self.update_latest()

    def _split_sequence(self, dst: Sequence, split_num: int) -> List:
        return [dst[i:i + split_num] for i in range(0, len(dst), split_num)]

    def _textHeight(self):  # ??????
        return QFontMetrics(self._read_font).height()

    def _titleHeight(self):  # ??????
        return QFontMetrics(self._title_font).height()

    def _setReadLine(self, auto_line: _AutoLine,
                     height: int) -> None:  # ??????????????????, ???????????????

        line, p_first_flag, p_title, *_ = auto_line

        frame = QFrame()
        frame.setFrameShape(QFrame.NoFrame)
        frame.setFixedHeight(height)

        frame_h = QHBoxLayout(frame)
        frame_h.setContentsMargins(0, 0, 0, 0)
        frame_h.setSpacing(0)

        label = QLabel(frame)
        label.setStyleSheet('border:0px solid black')
        if p_title:
            label.setFont(self._title_font)
            label.setStyleSheet('font-weight:bold')
        else:
            label.setFont(self._read_font)
        label.setText(line)

        if p_first_flag:
            label.setIndent(self.indent_size)
        if p_title:
            label.setIndent(0)

        label.p_title = p_title
        label.p_first_flag = p_first_flag
        label.line = auto_line
        if p_title:
            frame_h.addSpacing(10)
        else:
            frame_h.addSpacing(self.margin_size)
        frame_h.addWidget(label)
        frame_h.addStretch()
        frame.label = label
        self.read_layout.addWidget(frame)

    def _clearReadLines(self):  # ???????????????
        layout = self.read_layout
        child = layout.takeAt(0)
        while (child is not None):
            if child.widget():
                child.widget().setParent(None)
            child = layout.takeAt(0)

    def _addLine(self, line: str, fm: QFontMetrics,
                 content_index: int) -> None:
        lines = self._text_compute(line, fm, self.read_width)
        content_pos = 0
        for i, pline in enumerate(lines):
            has_indent = True if i == 0 else False
            content_pos += len(pline)
            self.auto_pages.append(
                _AutoLine(pline, has_indent, False, content_index,
                          content_pos))

    def _addLines(self, lines: List[str], first_title: bool = True, start: int = 0):  # ????????????
        self.auto_pages.clear()
        fm = QFontMetrics(self._read_font)
        for index, line in enumerate(lines):
            self._addLine(line, fm, index + start)
        if self.auto_pages:
            self.auto_pages[0][2] = first_title

    def _text_compute(self, text: str, fm: QFontMetrics,
                      width: int) -> list:  # ??????????????????
        if fm.width(text) <= width - self.indent_size - self.margin_size * 2:
            return [text]
        else:
            res = []
            lines = []
            row = 1
            for alpha in text:
                res.append(alpha.strip())
                if row == 1:
                    flag = width - self.indent_size - self.margin_size * 2
                if fm.width(''.join(res)) >= flag:
                    lines.append(''.join(res).strip())
                    flag = width - self.margin_size * 2
                    row += 1
                    # last = res[-1].strip()
                    res.clear()
                    # res.append(last)
            lines.append(''.join(res).strip())
            return lines

    @pyqtSlot(dict)  # ????????????
    def failUpdateChapter(self, messages: dict) -> None:
        content = messages['content']
        content.insert(0, messages['chapter'])
        self.chapter_content = content
        self.computePages(content, 0)

    def request_chapter(self,
                        url_index: int,
                        chapter_name: str = "",
                        current_book: str = "",
                        family: str = "",
                        indent: int = 20,
                        margin: int = 40,
                        font_size: int = 15,
                        letter_spacing: int = 2,
                        line_height: int = 100,
                        flag: int = 0,
                        page: int = 0,
                        **kwargs) -> None:
        for key in kwargs:
            setattr(self, key, kwargs[key])

        self.dst_page = page
        line_height = (line_height / 100) * 5
        self._read_font = QFont(family, font_size)
        self._read_font.setLetterSpacing(QFont.AbsoluteSpacing, letter_spacing)
        self._title_font = QFont(family, font_size + 2)
        super().request_chapter(url_index, chapter_name, current_book, family,
                                indent, margin, font_size, letter_spacing,
                                line_height, flag)

    def next_chapter(self) -> None:
        chapter_name = self.info.novel_chapter_urls[self.current_index][1]
        if self.current_page < self.pageCount() - 1:
            self.next_page()
            self.task_widget.load_chapter_init(
                chapter_name + f'({self.current_page + 1}/{self.pageCount()})')
        else:
            index = self.current_index + 1
            if index <= self.info.chapter_count() - 1:
                chapter_name = self.info.novel_chapter_urls[index][1]
                line_height = 20 * self.line_height
                self._clearReadLines()
                self.request_chapter(
                    index,
                    chapter_name,
                    self.current_book,
                    self.font_family,
                    self.indent_size,
                    self.margin_size,
                    self.font_size,
                    self.letter_spacing,
                    line_height,
                    flag=1,
                )

    def preview_chapter(self) -> None:
        chapter_name = self.info.novel_chapter_urls[self.current_index][1]
        if self.current_page > 0:
            self.previous_page()
            self.task_widget.load_chapter_init(
                chapter_name + f'({self.current_page + 1}/{self.pageCount()})')
        else:
            index = self.current_index - 1
            if index >= 0:
                chapter_name = self.info.novel_chapter_urls[index][1]
                line_height = 20 * self.line_height
                self._clearReadLines()
                self.request_chapter(index,
                                     chapter_name,
                                     self.current_book,
                                     self.font_family,
                                     self.indent_size,
                                     self.margin_size,
                                     self.font_size,
                                     self.letter_spacing,
                                     line_height,
                                     flag=2,
                                     page=-1)

    def jump_chapter(self, index: int, percent: float = 0) -> None:
        chapter_name = self.info.novel_chapter_urls[index][1]
        self.current_page = 0
        self.jump_percent = percent
        self._clearReadLines()
        self.request_chapter(index,
                             chapter_name,
                             self.current_book,
                             self.font_family,
                             self.indent_size,
                             self.margin_size,
                             self.font_size,
                             self.letter_spacing,
                             self.line_height,
                             flag=FlagAction.jump_chapter)

    def jump_from_bookmark(self, index: int, line: str, is_title: bool):
        chapter_name = self.info.novel_chapter_urls[index][1]
        self.current_page = 0
        self._clearReadLines()
        self.by_first_line = line
        self.is_title = is_title
        if is_title:
            self.by_first_line = self.current_chapter
        self.request_chapter(index,
                             chapter_name,
                             self.current_book,
                             self.font_family,
                             self.indent_size,
                             self.margin_size,
                             self.font_size,
                             self.letter_spacing,
                             self.line_height,
                             flag=FlagAction.from_bookmark)

    def renderOk(self, *args, **kwargs) -> str:
        by_line = kwargs.pop('by_first_line', None)
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

        self.read_font = QFont(self.font_family, self.font_size)
        self.read_font.setLetterSpacing(QFont.AbsoluteSpacing,
                                        self.letter_spacing)

        self.line_height = (self.line_height / 100) * 5
        self._clearReadLines()
        self.computePages(self.chapter_content,
                          self.current_page,
                          by_first_line=by_line,
                          is_title=False)
        chapter_name = self.chapter_content[0].strip()
        self.task_widget.load_chapter_init(
            chapter_name + f'({self.current_page + 1}/{self.pageCount()})')

    def renderFail(self, *args, **kwargs) -> str:
        pass

    def readTextColor(self) -> str:
        return QColor(self.text_color).name()

    def readBackColor(self) -> str:
        return QColor(self.bkg_color).name()

    def selectionText(self) -> str:
        pass


class TaskReadBrowser(QTextBrowser, BaseTaskReadPropertys):
    def visableText(self) -> str:
        cursor = self.cursorForPosition(QPoint(0, 0))
        bottom_right = QPoint(self.viewport().width() - 1,
                              self.viewport().height() - 1)
        end_pos = self.cursorForPosition(bottom_right).position()
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        return cursor.selectedText()

    def barRangeandValue(self) -> Tuple:
        bar = self.verticalScrollBar()
        return bar.minimum(), bar.maximum(), bar.value()

    def visableParas(self) -> List[str]:
        return self.visableText().split('\u2029')

    def firstVisablePara(self) -> str:
        return self.visableParas()[0].strip()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.task_widget.more_widget.isHidden():
                self.task_widget.more_widget.hide()
        return super().mousePressEvent(event)

    def resizeEvent(self, event) -> None:
        latested = self.info.getLatestRead()
        if self.sender() is None:
            self.verticalScrollBar().setValue(latested.float_percent *
                                              self.total_length())
        super().resizeEvent(event)

    @lasyproperty
    def _template(self) -> jinja2.Template:
        f_loader = FileSystemLoader("./tpls")
        env = Environment(loader=f_loader)
        return env.get_template("read.html")

    def renderOk(self, *args, **kwargs) -> str:
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
        return self._template.render(*args, **kwargs)

    @lasyproperty
    def _failtemplate(self) -> jinja2.Template:
        f_loader = FileSystemLoader("./tpls")
        env = Environment(loader=f_loader)
        return env.get_template("fail.html")

    def renderFail(self, *args, **kwargs) -> str:
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
        return self._failtemplate.render(*args, **kwargs)

    def flushLatested(self, p_value: int = None) -> LatestRead:
        line = self.firstVisablePara()
        bar = self.verticalScrollBar()
        value = bar.value() if p_value is None else p_value
        percent = round(value / self.total_length(), 4)
        if percent >= 0.99:
            percent = 1
        index = self.current_index
        chapter_name = self.current_chapter
        latested = self.info.getLatestRead()
        latested.float_percent = percent
        latested.chapter_name = chapter_name
        latested.index = index
        latested.line = line
        latested.is_title = True if line.strip() == chapter_name else False
        latested.page_step = bar.pageStep()
        latested.min = bar.minimum()
        latested.max = bar.maximum()
        latested.value = value
        latested.content_index = -1
        latested.content_pos = -1
        return latested

    @pyqtSlot(dict)
    def failUpdateChapter(self, message: dict) -> None:
        html = self.renderFail(
            messages=message,
            indent_size=self.indent_size,
            font_family=self.font_family,
            line_height=self.line_height,
            margin_size=self.margin_size,
            font_size=self.font_size,
            letter_spacing=self.letter_spacing,
        )
        self.setHtml(html)
        self.task_widget.mark_button.hide()
        self.task_widget.load_chapter_init(message["chapter"])

    @pyqtSlot(dict)  # ????????????
    def updateChapter(self, messages: dict) -> None:
        latest = self.info.getLatestRead()
        latest.index = self.current_index
        latest.chapter_name = messages.get("chapter", "")
        percent = latest.float_percent
        page_step = latest.page_step
        html = self.renderOk(
            messages=messages,
            indent_size=self.indent_size,
            font_family=self.font_family,
            line_height=self.line_height,
            margin_size=self.margin_size,
            font_size=self.font_size,
            letter_spacing=self.letter_spacing,
        )
        self.verticalScrollBar().blockSignals(True)
        self.setHtml(html)
        chapter_name = messages["chapter"]
        if self.flag == FlagAction.first_in:  # ????????????
            self.verticalScrollBar().setPageStep(page_step)
            self.verticalScrollBar().setRange(latest.min, latest.max)
            self.verticalScrollBar().setValue(latest.value)
            if percent > 0:
                self.task_widget.load_chapter_init(chapter_name + "(%.2f%%)" %
                                                   (percent * 100))
            else:
                self.task_widget.load_chapter_init(chapter_name)

        elif self.flag == FlagAction.next_chapter:  # next, preview
            self.task_widget.load_chapter_init(chapter_name)
            latest.float_percent = 0
            latest.line = chapter_name.strip()
            latest.is_title = True
            self.verticalScrollBar().setValue(0)

        elif self.flag == FlagAction.jump_chapter:  # ???percent??????
            self.verticalScrollBar().setValue(self.jump_percent *
                                              self.total_length())
            self.task_widget.load_chapter_init(chapter_name + "(%.2f%%)" %
                                               (self.jump_percent * 100))

        elif self.flag == FlagAction.split_to_scroll:
            self.verticalScrollBar().setValue(self.total_length() *
                                              latest.float_percent)
            self.task_widget.load_chapter_init(chapter_name + "(%.2f%%)" %
                                               (latest.float_percent * 100))

        latested = self.flushLatested()
        latested.is_title = True
        latested.line = chapter_name
        latested.content_index = 0
        latested.content_pos = 0

        markup = self.task_widget.info.bookmark_exists(self.current_index,
                                                       self.current_chapter)
        if markup:
            self.current_mark = markup
            self.task_widget._show_mark_button()
        else:
            self.current_mark = None
            self.task_widget.mark_button.hide()
        self.task_widget.updateRequestState()
        self.verticalScrollBar().blockSignals(False)

    def total_length(self) -> int:
        length = (self.verticalScrollBar().maximum() -
                  self.verticalScrollBar().minimum() + 1)
        return length

    @property
    def percent(self) -> float:
        return self.verticalScrollBar().value() / self.total_length()

    @property
    def current_chapter(self) -> str:
        if self.current_index is not None:
            return self.info.novel_chapter_urls[self.current_index][1]
        return ""

    @property
    def current_markup(self) -> Optional[Markup]:
        return self.current_mark

    @current_markup.setter
    def current_markup(self, mark: Optional[Markup]):
        self.current_mark = mark

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._customTextMenu)

    def _exit_read(self) -> None:
        self.task_widget.exit_button.click()

    def _add_mark(self) -> None:
        self.task_widget.addMarkUp()

    def _show_marks(self) -> None:
        self.task_widget.showChaptersWidget(True)
        self.task_widget.chapters_widget.pushButton_4.click()

    def _show_chapters(self) -> None:
        self.task_widget.showChaptersWidget(True)
        self.task_widget.chapters_widget.pushButton_3.click()
        self.task_widget.updateRequestState()

    def request_chapter(self,
                        url_index: int,
                        chapter_name: str = "",
                        current_book: str = "",
                        family: str = "",
                        indent: int = 20,
                        margin: int = 40,
                        font_size: int = 15,
                        letter_spacing: int = 2,
                        line_height: int = 5,
                        flag: FlagAction = FlagAction.first_in,
                        **kwargs) -> None:

        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.flag = flag
        self.indent_size = indent
        self.margin_size = margin
        self.font_size = font_size
        self.font_family = family
        self.letter_spacing = letter_spacing
        self.line_height = line_height
        self.current_index = url_index
        self.current_book = current_book
        self.read_loader.readChapter(url_index, chapter_name, self.info)

    def next_chapter(self) -> None:
        index = self.current_index + 1
        if index <= self.info.chapter_count() - 1:
            chapter_name = self.info.novel_chapter_urls[index][1]
            self.request_chapter(
                index,
                chapter_name,
                self.current_book,
                self.font_family,
                self.indent_size,
                self.margin_size,
                self.font_size,
                self.letter_spacing,
                self.line_height,
                FlagAction.next_chapter,
            )

    def preview_chapter(self) -> None:
        index = self.current_index - 1
        if index >= 0:
            chapter_name = self.info.novel_chapter_urls[index][1]
            self.request_chapter(
                index,
                chapter_name,
                self.current_book,
                self.font_family,
                self.indent_size,
                self.margin_size,
                self.font_size,
                self.letter_spacing,
                self.line_height,
                FlagAction.next_chapter,
            )

    def jump_chapter(self, index: int, percent: float = 0) -> None:
        chapter_name = self.info.novel_chapter_urls[index][1]
        self.jump_percent = percent
        self.request_chapter(
            index,
            chapter_name,
            self.current_book,
            self.font_family,
            self.indent_size,
            self.margin_size,
            self.font_size,
            self.letter_spacing,
            self.line_height,
            FlagAction.jump_chapter,
        )


class TaskReadColorDialog(QColorDialog):
    _style = '''
        QColorDialog{background: black; border:1px solid gray;border-radius:5px} 
        QLabel{color:white;font-family:????????????} 
        QPushButton{font-family:????????????} 
    '''
    selected_color = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(self._style)
        btns = self.findChildren(QPushButton)
        btns[0].setText('????????????????????????')
        btns[-1].setText('??????')
        btns[-2].setText('??????')
        self.colorSelected.connect(
            lambda v: self.selected_color.emit(v.name()))


class TaskBkgColorDialog(TaskReadColorDialog):
    pass


class ReadBar(TitleBar):
    StyleSheet = """
        /*????????????????????????????????????????????????*/
        #buttonMinimum,#buttonMaximum,#buttonClose {
            color: %s;
            border: none;
            background-color:transparent
        }
        /*??????*/
        #buttonMinimum:hover,#buttonMaximum:hover {
            color: %s;
        }
        #buttonClose:hover {
            color: %s;
        }
        /*??????????????????*/
        #buttonMinimum:pressed,#buttonMaximum:pressed {
            background-color: Firebrick;
        }
        #buttonClose:pressed {
            color: %s;
            background-color: Firebrick;
        }
    """

    def titleMsgInfo(self, msg: str, strong=False, color=None) -> None:
        show_color = QColor(color)
        info_msg = f"<b>{msg}</b>" if strong else msg
        info_msg = (f'<font color="{show_color.name()}">{info_msg}</font>'
                    if color else info_msg)
        self.info_label.setText(info_msg)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.titleLabel.hide()
        self.iconLabel.hide()
        self.task_widget = None
        self.setContentsMargins(0, 0, 0, 0)

        layout = self.layout()
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(5)

        font = QFont("????????????", 10)

        frame = QFrame()
        frame.setFrameShape(QFrame.NoFrame)
        frame.setStyleSheet("background:transparent;border:none")
        flay = QHBoxLayout(frame)
        flay.setContentsMargins(0, 0, 0, 0)
        label = QLabel()
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        label.setFont(font)
        label.setIndent(5)
        label.setStyleSheet(
            "QLabel{border: none; color:white; background:transparent}")
        info_label = InfoLabel()
        info_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        info_label.setFont(QFont("????????????", 9))
        info_label.setStyleSheet("QLabel{border: none;background:transparent}")
        info_label.setIndent(5)
        flay.addWidget(label)
        flay.addWidget(info_label, 100)
        self.label = label
        self.info_label = info_label
        self.addLeftTitleWidget(frame, 100)

        button = ColorButton()
        h = self.label.fontMetrics().height()
        button.setStyleSheet("ColorButton{border:none;background:transparent}")
        button.setHoverLeave(CommonPixmaps.hl_leftarrow_svg, "white",
                             "#999999", h)
        button.setToolTip("<b>????????????</b>")

        self.exit_button = button
        self.addLeftTitleWidget(button)

        self.setHeight(label.fontMetrics().height() * 1.5 + 6)
        self.setBarColor("#161819")
        self.setTextColor(Qt.white)

    def setBarColor(self, color: Any) -> None:
        palatte = QPalette(self.palette())
        palatte.setColor(QPalette.Background, QColor(color))
        self.setAutoFillBackground(True)
        self.setPalette(palatte)
        self.update()

    def setTextColor(self, color: Any) -> None:
        color_name = QColor(color).name()
        c_t = color_name, color_name, color_name, color_name
        self.label.setStyleSheet(
            f"color: {color_name};border: none; background:transparent")
        self.buttonMinimum.setStyleSheet(self.StyleSheet % c_t)
        self.buttonMaximum.setStyleSheet(self.StyleSheet % c_t)
        self.buttonClose.setStyleSheet(self.StyleSheet % c_t)
        self.update()

    @property
    def book_name(self) -> str:
        return self.label.text()

    @book_name.setter
    def book_name(self, value: str) -> None:
        self.label.setText(value)

class GifButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.movie = None

    def setGif(self, file_name: str) -> None:
        self.movie = QMovie(file_name)
        self.movie.setSpeed(100)
        # self.movie.setCacheMode() # ?????????????????????
        self.movie.frameChanged.connect(self._update)
        self.movie.start()

    def setIcon(self, icon: QIcon) -> None:
        if self.movie:
            self.movie.stop()
        super().setIcon(icon)

    def stopGif(self) -> None:
        if self.movie:
            self.movie.stop()

    def reStartGif(self) -> None:
        if self.movie:
            self.movie.start()

    def _update(self, index: int) -> None:
        pixmap = self.movie.currentPixmap()
        super().setIcon(QIcon(pixmap))

    def closeEvent(self, event):
        if self.movie:
            self.movie.stop()
        super().closeEvent(event)


class HoverButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__normal_icon = None
        self.__hover_icon = None

    def setNHSize(self, w, h):
        self.setIconSize(QSize(w, h))
        self.setFixedSize(QSize(w, h))

    def setNormal(self, path: str) -> None:
        self.__normal_icon = QIcon(path)

    def setHover(self, path: str) -> None:
        self.__hover_icon = QIcon(path)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.setIcon(self.__hover_icon)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.setIcon(self.__normal_icon)

class ColorButton(QPushButton):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.svg = kwargs.pop("svg", "")
        self.setCheckable(True)
        self.setStyleSheet('border: none')

    def setHoverLeave(
        self,
        source: str,
        hover_fill: tuple,
        leave_fill: tuple,
        size: Union[int, tuple, QSize, float] = 32,
    ) -> None:
        self._setSource(source)
        if isinstance(size, (int, float)):
            sized = QSize(size, size)
        elif isinstance(size, tuple):
            sized = QSize(*size)
        elif isinstance(size, QSize):
            sized = size
        self.hover = self._get_by_color(hover_fill, sized)
        self.leave = self._get_by_color(leave_fill, sized)
        self.setIconSize(sized)
        self.setIcon(QIcon(self.leave))
        self.setFixedSize(sized)

    def enterEvent(self, a0) -> None:
        self.setIcon(QIcon(self.hover))
        return super().enterEvent(a0)

    def leaveEvent(self, a0) -> None:
        self.setIcon(QIcon(self.leave))
        return super().leaveEvent(a0)

    def _setSource(self, svg_file: str) -> None:
        file = QFile(svg_file)
        if file.open(QFile.ReadOnly | QFile.Text):
            text_stream = QTextStream(file)
            content = text_stream.readAll()
            self.svg = content

    def _get_by_color(self, fill: tuple, size=QSize(32, 32)) -> QPixmap:
        svg_render = QSvgRenderer()
        svg_bytes = (self.svg % fill).encode(encoding="utf-8")
        svg_render.load(svg_bytes)
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        svg_render.render(painter)
        return pixmap

class BorderButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enter = False

    def enterEvent(self, event) -> None:
        self._enter = True
        return super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._enter = False
        return super().leaveEvent(event)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing, True)
        if self._enter:
            painter.setPen(QPen(QColor('#CC295F'), 2))
        else:
            painter.setPen(QPen(Qt.white, 2))
        painter.drawRoundedRect(self.rect().adjusted(1,1,-1,-1), 3, 3)
   
class FInValidator(QIntValidator):
    def fixup(self, input: str) -> str:  # return?????????
        new_value = input.replace('0', '')
        value = int(new_value) if new_value else 0
        if value >= self.top():
            return '%s' % self.top()
        if value <= self.bottom():
            return '%s' % self.bottom()
