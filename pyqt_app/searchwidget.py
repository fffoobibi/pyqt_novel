import asyncio

from .search_infoui import Ui_Form
from .magic import lasyproperty, qmixin
from .styles import COLOR
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QPoint
from PyQt5.QtGui import QIcon, QFont, QPainter, QColor
from crawl_novel import InfoObj, InfTools, FileDownloader, DownStatus, ChapterDownloader

__all__ = ('SearchInfoWidget',)

@qmixin
class SearchInfoWidget(QWidget, Ui_Form):

    introutced_signal = pyqtSignal(InfoObj)

    @lasyproperty
    def novel_widget(self):
        return self.info.novel_app

    def __init__(self, info: InfoObj):
        super().__init__()
        self.setupUi(self)
        self.setFont(QFont('微软雅黑', 9))
        self.checkBox.setCursor(Qt.PointingHandCursor)
        self.dft_style = self.styleSheet()
        self.info = info
        self.chapter_downloader = None
        self.file_downloader = None
        self.subscribe_state = False
        self.setStrWidth(self.novel_size, '100000000')
        self.novel_size.setAlignment(Qt.AlignRight)
        self._addSlots()
        self.addInfo(info)
        
    def _addSlots(self):
        self.info_pushButton.clicked.connect(
            lambda inf: self.introutced_signal.emit(self.info))
        self.down_pushButton.clicked.connect(self.downLoad)

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        self.info_pushButton.click()

    def addInfo(self, info: InfoObj):
        self.info = info
        index, name = info.novel_index, info.novel_name
        name = InfTools.addColor('red', self.info.novel_app.search_content, self.info)
        self.novel_name.setText(f'{index}. {name}')
        self.novel_size.setText(info.novel_size)
        self.novel_site.setText(info.novel_site)
        if info.novel_download:
            self._downOkFlag()
        if info.novel_status == DownStatus.down_fail: #'下载失败':
            self._downFailFlag()
        elif info.novel_status == DownStatus.down_ok: #'已下载':
            self._downOkFlag()
        elif info.novel_status == DownStatus.down_ing: #'下载中':
            self._downIngFlag()
        elif info.novel_status == DownStatus.down_before: #'未处理':
            self._downBeforeFlag()

    def downLoad(self):  # 开启下载
        if self.info.novel_flag == False:
            self.info.novel_down_cancel = False
            self._downIngFlag()
            self.novel_widget.getIconWidget(self.info.novel_index - 1)._downIngFlag()
            task_widget = self.novel_widget.getCurrentTaskWidget()
            if task_widget:
                task_widget._downIngFlag()
            if self.info._is_file:
                self.createFileDownloader()
            else:
                self.createChapterDownloader()

    def createChapterDownloader(self):
        novel_widget = self.novel_widget
        new_loop = asyncio.new_event_loop()
        if self.chapter_downloader is None:
            self.chapter_downloader = ChapterDownloader(novel_widget.thread_seam, self.info, new_loop)
            self.chapter_downloader.update_signal.connect(self.chapterUpdateInfos)
            self.chapter_downloader.flag_signal.connect(self.processFlags)
            self.chapter_downloader.nourls_signal.connect(self._cancelFlagBoth)
        self.chapter_downloader.download(self.info)

    def createFileDownloader(self):
        novel_widget = self.novel_widget
        if self.file_downloader is None:
            self.file_downloader = FileDownloader(novel_widget.thread_seam, self.info)
            self.file_downloader.update_signal.connect(self.fileUpdateInfos)
            self.file_downloader.flag_signal.connect(self.processFlags)
        self.file_downloader.download(self.info)
    
    @pyqtSlot(InfoObj)
    def processFlags(self, inf):
        self.info.novel_app.processSearchIconFlags(inf)

    def _cancelFlagBoth(self):
        self._downCancelFlag()
        self.novel_widget.getIconWidget(self.info.novel_index - 1)._downCancelFlag()

    @pyqtSlot()
    def _downOkBoth(self):
        self._downOkFlag()
        self.novel_widget.getIconWidget(self.info.novel_index - 1)._downOkFlag()
      
    @pyqtSlot(InfoObj)
    def chapterUpdateInfos(self, inf: InfoObj):
        novel_widget = self.novel_widget
        task_widget = novel_widget.getCurrentTaskWidget()
        if task_widget:
            if inf.novel_index == task_widget._inf.novel_index:
                    task_widget.updateFromInf(inf)
            if inf.novel_status == DownStatus.down_fail: #'下载失败':
                self._cancelFlagBoth()
                if task_widget:
                    task_widget._downFailFlag()
            elif inf.novel_status == DownStatus.down_ok:#'已下载':
                self._downOkBoth()
                if task_widget:
                    task_widget._downOkFlag()
                novel_widget.addDownRecord(inf, first=True)
 
    @pyqtSlot(InfoObj)
    def fileUpdateInfos(self, inf: InfoObj):
        novel_widget = self.novel_widget
        task_widget = novel_widget.getCurrentTaskWidget()
        if task_widget:
            if inf.novel_index == task_widget._inf.novel_index:
                task_widget.updateFromInf(inf)

    @pyqtSlot()
    def _downOkFlag(self):
        self.down_pushButton.setIcon(QIcon(':/ico/checked_1229231_easyicon.net.svg'))
        self.novel_name.setStyleSheet(f'background: {COLOR["down_ok"]};font-family:微软雅黑; font-size:9pt')
        self.info.novel_flag = True

    @pyqtSlot()
    def _downIngFlag(self):
        self.down_pushButton.setGif(':/gif/5-121204193941-50.gif')

    @pyqtSlot()
    def _downCancelFlag(self):
        self.down_pushButton.setIcon(QIcon(':/ico/download_1229240_easyicon.net.svg'))
        self.novel_name.setStyleSheet(f'background: transparent;font-family:微软雅黑; font-size:9pt')

    _downBeforeFlag = _downCancelFlag

    @pyqtSlot()
    def _downFailFlag(self):
        self.down_pushButton.setIcon(QIcon(':/ico/cloud_fail_72px_1137820_easyicon.net.png'))
        self.novel_name.setStyleSheet(f'background: {COLOR["down_fail"]};font-family:微软雅黑; font-size:9pt')

    @pyqtSlot(int)
    def _selectBy(self, checked):
        if checked == Qt.Checked:
            self.select()
        elif checked == Qt.Unchecked:
            self.cancelSelect()

    def _setWaitForDoneIcon(self):
        self.down_pushButton.setGif(':/gif/5-121204193941-50.gif')

    def select(self):
        self.checkBox.setChecked(True)

    def cancelSelect(self):
        self.checkBox.setChecked(False)

    @pyqtSlot()
    def cancelDownload(self):
        self.info.novel_down_cancel = True
        self.info.novel_flag = False
        self._downCancelFlag()

    def setSavePath(self, value: str):
        self.info.novel_save_path = value

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        inf = self.info
        self.novel_widget.getIconWidget(self.info.novel_index - 1).setFocus(True)
        self.novel_widget.titleMsgInfo(f'<b>{inf.novel_site}</b>: {inf.novel_name}-{inf.novel_size}')

    def addSubscribeState(self):
        self.subscribe_state = True
        self.update()

    def removeSubscribeState(self):
        self.subscribe_state = False
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self.subscribe_state:
            color = QColor(61, 95, 185, 70)
            painter = QPainter(self)
            points = [QPoint(0, 0), QPoint(0, 40), QPoint(40, 0)]
            painter.setPen(color)
            painter.setBrush(color)
            painter.drawPolygon(*points)
        
