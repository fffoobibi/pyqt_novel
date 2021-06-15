from PyQt5.QtWidgets import (
    QApplication, QListWidget, QListWidgetItem, QDialog, QButtonGroup, QMessageBox)
from PyQt5.QtGui import (QIcon, QPixmap, QTextDocument, QTextCursor, QTextDocument,
                         QDesktopServices, QColor, QPainter, QFontMetrics, QFont, QPen, QPainterPath, QBrush)
from PyQt5.QtCore import (QSize, QRect, Qt, QEvent, QDir, pyqtSlot,
                          QRegularExpression, QStandardPaths, QUrl, QSemaphore)
from datetime import datetime, timedelta
from .customwidgets import _DownRecordWidget, _SearchRecordWidget
from .styles import listwidget_v_scrollbar, listview_style
from .popwindowui import Ui_Dialog
from .log_supports import getSearchLog
from .plugins_support import generate_plugin, HumReadMixin

import re

from contextlib import suppress
from typing import List, NoReturn, Iterable
from crawl_novel import InfoObj, BasicFileSpider
from math import sqrt


class PopDialog(Ui_Dialog, QDialog, HumReadMixin):

    @staticmethod
    def _textAutoWrap(content: str, limit: int, fm: QFontMetrics, rows: int = None) -> str:
        if fm.width(content) >= limit:
            final = []
            res = []
            row_count = 1
            for alpha in content:
                res.append(alpha)
                if fm.width(''.join(res)) >= limit:
                    row_count += 1
                    if rows:
                        if row_count > rows:
                            break
                    final.append(''.join(res))
                    res.clear()
            newst = '\n'.join(final) + '\n' + ''.join(res)
            if rows:
                newst = fm.elidedText(newst, Qt.ElideRight, limit * rows)
        else:
            newst = content
        return newst

    @staticmethod
    def drawNovelImage(name, scaled: float = 1.0) -> QPixmap:
        pixmap = QPixmap(180, 240)
        pixmap.fill(Qt.white)
        painter = QPainter()
        painter.begin(pixmap)
        font = QFont('宋体', 15)
        font.setBold(True)
        painter.setFont(font)
        name = PopDialog._textAutoWrap(
            name, 140, painter.fontMetrics(), rows=2)
        # fm = painter.fontMetrics()
        painter.fillRect(QRect(20, 0, 160, 120), QColor('#CEFFCE'))
        painter.drawText(20, 122, 160, 138, Qt.AlignLeft, name)
        painter.save()

        font = QFont('微软雅黑', 28)
        font.setBold(True)
        pen = QPen()
        pen.setColor(QColor('#97CBFF'))
        painter.setPen(pen)
        painter.setFont(font)
        painter.drawText(20, 0, 140, 120, Qt.AlignCenter, 'Read')
        painter.restore()
        painter.setPen(Qt.lightGray)
        painter.drawRect(pixmap.rect().adjusted(0, 0, -1, -1))
        painter.end()
        if scaled == 1:
            return pixmap
        return pixmap.scaled(QSize(180 * scaled, 240 * scaled), transformMode=Qt.SmoothTransformation)

    @property
    def novel_widget(self) -> 'NovelWidget':
        return self.root.novel_widget

    def generate_plugins_by_tpl(self) -> NoReturn:
        type = self.comboBox_2.currentIndex()
        output_path = QDir.toNativeSeparators(QDir(QStandardPaths.writableLocation(
            QStandardPaths.HomeLocation)).absoluteFilePath('plugins'))
        now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        site_name = self.lineEdit_5.text().strip()
        if site_name in [spider_cls.name for spider_cls in BasicFileSpider.get_cached_spiders()]:
            QMessageBox.warning(
                self.root, '警告', f'<font color=red>{site_name}</font>已存在,重新设置名称!')
        else:
            if site_name:
                generate_plugin(site_name, site_name, site_name,
                                site_name, output_path, type)
                _msg = 'filePlg' if type == 0 else 'chapterPlg'
                msg = f'模板插件{_msg}{site_name}.py已保存在plugins目录下'
                self.root.titleMsgInfo(msg)

    def __init__(self, root: 'GuiMain'):
        super().__init__()
        self.setupUi(self)
        self.blockSignals(True)
        self.root = root
        self.flag = 0
        self.search_logs = getSearchLog()
        self.down_records: List[InfoObj] = []
        self.bk_down_records: List[InfoObj] = []
        self.resize(700, 500)
        self.is_debug = False
        self.listWidget.itemClicked.connect(self._executeCmdMacros)
        self.default_sheet = self.styleSheet()
        self.current_list = None
        self.current_day = None
        self._add_shadow = False
        # self.textBrowser_1.hide()

        self.listWidget_2.setVerticalScrollMode(
            QListWidget.ScrollPerPixel)  # 像素滚动
        self.listWidget_2.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.listWidget_2.verticalScrollBar().setSingleStep(5)  # 重要
        self.listWidget_2.verticalScrollBar().setStyleSheet(listwidget_v_scrollbar)
        self.listWidget_2.setStyleSheet(listview_style)
        self.listWidget_2.remove_sig.connect(self.updateLabelMsg)

        self.listWidget_3.setVerticalScrollMode(
            QListWidget.ScrollPerPixel)  # 像素滚动
        self.listWidget_3.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.listWidget_3.verticalScrollBar().setSingleStep(15)  # 重要
        self.listWidget_3.verticalScrollBar().setStyleSheet(listwidget_v_scrollbar)
        self.listWidget_3.setStyleSheet(listview_style)
        self.listWidget_3.remove_sig.connect(self.updateLabelMsg)
        self.addDownRecordsFromPath(self.novel_widget.getDownRecords())
        self.addSearchRecordsFromSearchlog()

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.pushButton_3)  # 下载记录
        self.button_group.addButton(self.pushButton_8)
        self.button_group.addButton(self.pushButton_9)
        self.button_group.addButton(self.pushButton_10)

        self.button_group.addButton(self.pushButton_6)  # 搜索记录
        self.button_group.addButton(self.pushButton_11)
        self.button_group.addButton(self.pushButton_12)
        self.button_group.addButton(self.pushButton_13)

        self.button_group.buttonClicked.connect(self.buttonGroupsPolicy)
        self.pushButton_4.clicked.connect(self.buttonsPolicy)  # 下载记录
        self.pushButton_7.clicked.connect(self.buttonsPolicy)  # 搜索记录
        self.pushButton_14.clicked.connect(
            lambda: self.textBrowser.clearAllLines())
        self.pushButton.clicked[bool].connect(self.clearDownRecords)
        self.lineEdit_4.returnPressed.connect(self.findText)
        fm = self.pushButton_14.fontMetrics()
        self.pushButton_14.setFixedSize(fm.width('清理')*2.5, fm.height() * 1.6)
        self.label_4.setText(self.novel_widget.getSavePath())
        self.comboBox.currentIndexChanged.connect(self._changeDebugTheme)
        plugin_path = QDir(QStandardPaths.writableLocation(
            QStandardPaths.HomeLocation)).absoluteFilePath('plugins')
        self.label_8.setText(plugin_path)
        self.pushButton_16.clicked.connect(self.openPluginDir)
        self.textBrowser.clearAllLines()
        self.lineEdit_3.returnPressed.connect(self.search)

        self.horizontalSlider.valueChanged.connect(self.resizeTitleBar)
        self.horizontalSlider_2.valueChanged.connect(self.resizeIconWidget)
        self.spinBox_2.valueChanged.connect(self.resizeTitleBar)

        fm = self.label_11.fontMetrics()
        self.label_11.setFixedWidth(fm.width('100%'))
        scaled = self.novel_widget._novelScaled()
        self.label_11.setText(f'{scaled * 100}%')
        pixmap = self.drawNovelImage('搜书虫', float(scaled))
        self.label_10.setPixmap(pixmap)
        self.horizontalSlider_2.setValue(int(scaled * 100))

        title_height = self.novel_widget._titleHeight()
        self.label_9.setFixedHeight(title_height)
        self.spinBox_2.setValue(title_height)
        self.horizontalSlider.setValue(title_height)
        self.label_10.setPixmap(self.drawNovelImage('搜书虫'))
        self.pushButton_17.clicked.connect(
            self.generate_plugins_by_tpl)  # 模板导出
        self.pushButton_5.clicked.connect(self.clearSearchRecords)
        # self.novel_widget.computeSearchCacheSize()
        # self.novel_widget.computeImagesCacheSize()
        self.radioButton.toggled.connect(self.changeSearchMode)
        self.radioButton_2.toggled.connect(self.changeSearchMode)
        self.pushButton_18.clicked.connect(self.novel_widget.clearHttpCaches)
        self.pushButton_18.setNormal(':/ico/trash-o.svg')
        self.pushButton_18.setHover(':/ico/trash-o_hover.svg')
        self.pushButton_19.setNormal(':/ico/trash-o.svg')
        self.pushButton_19.setHover(':/ico/trash-o_hover.svg')
        self.spinBox.valueChanged.connect(self.setThreadCounts)
        self.installEventFilter(self)
        self.blockSignals(False)
        self.label_16.setText(self.size_hum_read(self.novel_widget.search_cache_size))
        self.label_18.setText(self.size_hum_read(self.novel_widget.image_cache_size))

    def setThreadCounts(self, value):
        self.novel_widget.max_threads = value
        self.novel_widget.thread_seam = QSemaphore(value)

    def changeSearchMode(self, state: bool) -> NoReturn:
        if self.sender() == self.radioButton:
            if state:
                self.root.search_mode = '极速模式'
            else:
                self.root.search_mode = '最新模式'
            self.root._setState()

    def openPluginDir(self, flag: bool) -> NoReturn:
        with suppress(Exception):
            plugin_path = QDir(QStandardPaths.writableLocation(
                QStandardPaths.HomeLocation)).absoluteFilePath('plugins')
            QDesktopServices.openUrl(QUrl.fromLocalFile(plugin_path))

    def resizeTitleBar(self, value: int) -> NoReturn:
        self.spinBox_2.setValue(value)
        self.label_9.setFixedHeight(value)
        self.root.resizeTitleBar(value)
        self.novel_widget.settings.setValue('Settings/titleheight', value)
        if self.sender() == self.spinBox_2:
            self.horizontalSlider.setValue(value)

    def resizeIconWidget(self, value: int) -> NoReturn:
        self.label_11.setText(f'{value}%')
        pixmap = self.drawNovelImage('搜书虫', value / 100)
        self.label_10.setPixmap(pixmap)
        width = pixmap.width()
        height = pixmap.height()
        self.size_label.setText(f'{width} x {height}')
        self.root.resizeIconWidget(value / 100)
        self.novel_widget.settings.setValue('Settings/novelscaled', value / 100)

    def updateLabelMsg(self, msg: str) -> NoReturn:
        self.label_5.setText(f' 共:{self.sender().filterCount()}个{msg}')

    def search(self) -> NoReturn:
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        content = self.sender().text()
        if self.current_day == 0:
            s_txt = today + '.*' + content
        elif self.current_day == 1:
            s_txt = yesterday + '.*' + content
        else:
            s_txt = content
        if self.current_list == self.listWidget_2:
            self.listWidget_2.filter(s_txt)
            self.label_5.setText(f' 共:{self.listWidget_2.filterCount()}个下载记录')
        elif self.current_list == self.listWidget_3:
            self.listWidget_3.filter(s_txt)
            self.label_5.setText(f' 共:{self.listWidget_3.filterCount()}个搜索记录')

    def _changeDebugTheme(self, index: int) -> NoReturn:
        if index == 0:
            self.textBrowser.setTheme('debugtextbrowser.light')
        elif index == 1:
            self.textBrowser.setTheme('debugtextbrowser.dark')
        self.textBrowser.update()

    def findText(self) -> NoReturn:
        txt = self.sender().text().strip()
        if txt:
            cursor = self.textBrowser.textCursor()
            if self.textBrowser.find(QRegularExpression(txt), QTextDocument.FindBackward) == False:
                self.textBrowser.moveCursor(QTextCursor.End)
                self.textBrowser.horizontalScrollBar().setValue(0)
                retry = self.textBrowser.find(
                    QRegularExpression(txt), QTextDocument.FindBackward)
                if retry == False:
                    QMessageBox.warning(self, '提示', f'未查找到{txt}!')

    def buttonGroupsPolicy(self, a0) -> NoReturn:
        if a0 == self.pushButton_3:
            self.pushButton_4.click()
        elif a0 == self.pushButton_6:
            self.pushButton_7.click()
        elif a0 == self.pushButton_8:
            self.selectTodayDownRecords()
        elif a0 == self.pushButton_9:
            self.selectYesterDownRecords()
        elif a0 == self.pushButton_10:
            self.selectTotalDownRecords()
        elif a0 == self.pushButton_11:
            self.selectTodaySearchRecords()
        elif a0 == self.pushButton_12:
            self.selectYesterdaySearchRecords()
        elif a0 == self.pushButton_13:
            self.selectTotalSearchRecords()

    def buttonsPolicy(self) -> NoReturn:
        if self.sender() == self.pushButton_4:
            if self.pushButton_4.isChecked():
                self.frame_8.hide()
            else:
                self.frame_8.show()
        elif self.sender() == self.pushButton_7:
            if self.pushButton_7.isChecked():
                self.frame_10.hide()
            else:
                self.frame_10.show()

    def _executeCmdMacros(self, item: QListWidgetItem) -> NoReturn:
        text = re.findall(r'[a-zA-Z]*', item.text())[0]
        self.lineEdit.clear()
        self.lineEdit.setText(text)
        if self.root:
            self.root.lineedit.clear()
            self.root.lineedit.setText(text)
            self.root.macros()

    def selectTotalDownRecords(self) -> NoReturn:
        self.current_list = self.listWidget_2
        self.stackedWidget_2.setCurrentIndex(0)
        self.pushButton_10.setChecked(True)
        self._filterDownRecords(-1)
        self.label_5.setText(f' 共:{self.listWidget_2.filterCount()}个下载记录')

    def selectTodayDownRecords(self) -> NoReturn:
        self.current_list = self.listWidget_2
        self.stackedWidget_2.setCurrentIndex(0)
        self.pushButton_8.setChecked(True)
        self._filterDownRecords(0)
        self.label_5.setText(f' 共:{self.listWidget_2.filterCount()}个下载记录')

    def selectYesterDownRecords(self) -> NoReturn:
        self.current_list = self.listWidget_2
        self.stackedWidget_2.setCurrentIndex(0)
        self.pushButton_9.setChecked(True)
        self._filterDownRecords(1)
        self.label_5.setText(f' 共:{self.listWidget_2.filterCount()}个下载记录')

    def selectTodaySearchRecords(self) -> NoReturn:
        self.current_list = self.listWidget_3
        self.stackedWidget_2.setCurrentIndex(1)
        self.pushButton_11.setChecked(True)
        self._filterSearchRecords(0)
        self.label_5.setText(f' 共:{self.listWidget_3.filterCount()}个搜索记录')

    def selectYesterdaySearchRecords(self) -> NoReturn:
        self.current_list = self.listWidget_3
        self.stackedWidget_2.setCurrentIndex(1)
        self.pushButton_12.setChecked(True)
        self._filterSearchRecords(1)
        self.label_5.setText(f' 共:{self.listWidget_3.filterCount()}个搜索记录')

    def selectTotalSearchRecords(self) -> NoReturn:
        self.current_list = self.listWidget_3
        self.stackedWidget_2.setCurrentIndex(1)
        self.pushButton_13.setChecked(True)
        self._filterSearchRecords(-1)
        self.label_5.setText(f' 共:{self.listWidget_3.filterCount()}个搜索记录')

    def gotoSettings(self) -> NoReturn:
        self.flag = 0
        self.is_debug = False
        self.setStyleSheet('background-color: white')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.stackedWidget.setCurrentIndex(2)
        self._addShadow(False)

    def gotoMacros(self) -> NoReturn:
        self.flag = 0
        self.is_debug = False
        self.setStyleSheet('QDialog{background-color: white;border:1px solid lightgray}')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.stackedWidget.setCurrentIndex(0)
        self._addShadow(False)

    def gotoRecords(self) -> NoReturn:
        self.current_list = self.listWidget_2
        self.flag = 1
        self.is_debug = False
        self.setWindowIcon(QIcon(':/ico/footprint_1293427_easyicon.net.svg'))
        self.setWindowTitle('我的足迹')
        self.setStyleSheet(self.default_sheet)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.pushButton_5.hide()
        self.pushButton.show()
        self.stackedWidget.setCurrentIndex(1)
        self.stackedWidget_2.setCurrentIndex(0)
        self._addShadow(False)

    def gotoSearchRecords(self) -> NoReturn:
        self.current_list = self.listWidget_3
        self.flag = 1
        self.is_debug = False
        self.setWindowIcon(QIcon(':/ico/footprint_1293427_easyicon.net.svg'))
        self.setWindowTitle('我的足迹')
        self.setStyleSheet(self.default_sheet)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.pushButton.hide()
        self.pushButton_5.show()
        self.stackedWidget.setCurrentIndex(1)
        self.stackedWidget_2.setCurrentIndex(1)
        self._addShadow(False)

    def gotoDebug(self) -> NoReturn:
        self.flag = 1
        self.is_debug = True
        self.setWindowIcon(QIcon(':/ico/debug_1153442_easyicon.net.svg'))
        self.setWindowTitle('调试面板')
        self.setStyleSheet(self.default_sheet)
        self.setWindowFlags(Qt.WindowCloseButtonHint |
                            Qt.WindowMinMaxButtonsHint | Qt.WindowStaysOnTopHint)
        self.stackedWidget.setCurrentIndex(3)
        self.textBrowser.verticalScrollBar().setSliderPosition(0)
        self.textBrowser.horizontalScrollBar().setSliderPosition(0)
        self._addShadow(False)

    def _addShadow(self, state: bool):
        self._add_shadow = state
        self.update()

    def gotoUi(self, hide=False, with_title=True, add_shadow=True) -> NoReturn:
        if with_title:
            self.flag = 1
            self.setWindowFlags(Qt.WindowCloseButtonHint)
        else:
            self.flag = 0
            self.setWindowFlags(Qt.FramelessWindowHint)
        self.is_debug = False
        self.setWindowTitle('界面预览')
        self.setStyleSheet(self.default_sheet)
        self.stackedWidget.setCurrentIndex(4)
        scaled = self.novel_widget._novelScaled()
        self.label_10.setPixmap(self.drawNovelImage('搜书虫', scaled))
        if hide:
            self.groupBox.hide()
        else:
            self.groupBox.show()
        self._addShadow(add_shadow)

    def gotoFail(self):
        self.flag = 1
        self.is_debug = False
        self.setWindowIcon(
            QIcon(':/ico/EditDocument_1194764_easyicon.net.svg'))
        self.setWindowTitle('下载日志')
        self.setStyleSheet(self.default_sheet)
        self.setWindowFlags(Qt.WindowCloseButtonHint |
                            Qt.WindowMinMaxButtonsHint | Qt.WindowStaysOnTopHint)
        self.stackedWidget.setCurrentIndex(5)
        self.fail_edit.moveCursor(QTextCursor.Start)
        self._addShadow(False)

    def clearDownRecords(self, flag=False) -> NoReturn:
        for inf in self.down_records:
            inf.remove()
        self.down_records.clear()
        self.listWidget_2.clear()
        self.label_5.setText(' 共:0个下载记录')

    def clearSearchRecords(self) -> NoReturn:
        self.listWidget_3.clear()
        getSearchLog().clear()
        self.label_5.setText(' 共:0个搜索记录')

    def _filterDownRecords(self, type: int) -> NoReturn:
        self.pushButton_5.hide()
        self.pushButton.show()
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        if type == 0:  # 今天
            self.current_day = 0
            self.listWidget_2.filter(today.strftime('%Y-%m-%d'))
        elif type == 1:  # 昨天
            self.current_day = 1
            self.listWidget_2.filter(yesterday.strftime('%Y-%m-%d'))
        else:  # 所有
            self.current_day = -1
            self.listWidget_2.filter('.*')

    def _filterSearchRecords(self, type: int) -> NoReturn:
        self.pushButton_5.show()
        self.pushButton.hide()
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        search_log = getSearchLog()
        if type == 0:  # 今天
            self.current_day = 0
            self.listWidget_3.filter(today.strftime('%Y-%m-%d'))
        elif type == 1:  # 昨天
            self.current_day = 1
            self.listWidget_3.filter(yesterday.strftime('%Y-%m-%d'))
        else:  # 所有
            self.current_day = -1
            self.listWidget_3.filter('.*')

    def updateScrapyMessage(self, msg: str) -> NoReturn:
        self.textBrowser.append(msg)

    @pyqtSlot()
    def addDownRecord(self, inf: InfoObj, first: bool = False) -> NoReturn:
        if inf in self.down_records:
            index = self.down_records.index(inf)
            self.down_records[index].update(inf.__dict__)
            return
        if not first:
            self.down_records.append(inf)
            self.bk_down_records.append(inf)
            filter_value = inf.novel_end_time + inf.novel_name
            self.listWidget_2.appendItem(
                filter_value, _DownRecordWidget(inf, self.listWidget_2), meta={'inf': inf})
        else:
            self.down_records.insert(0, inf)
            self.bk_down_records.insert(0, inf)
            filter_value = inf.novel_end_time + inf.novel_name
            self.listWidget_2.appendTop(filter_value, _DownRecordWidget(
                inf, self.listWidget_2), meta={'inf': inf})
        if self.current_list:
            msg = '下载记录' if self.current_list == self.listWidget_2 else '搜索记录'
            self.label_5.setText(f' 共:{self.current_list.filterCount()}个{msg}')

    def addDownRecordsFromPath(self, inf_path: Iterable[str]) -> NoReturn:
        for file_path in inf_path:
            with open(file_path, 'r', encoding='utf8') as fp:
                inf = InfoObj.fromJson(fp=fp)
                self.addDownRecord(inf)
        self.bk_down_records = self.down_records.copy()

    def addSearchRecordsFromSearchlog(self) -> NoReturn:
        logs = getSearchLog()
        for log in logs.allLogs():
            self.addSearchRecord(from_log=log)

    def addSearchRecord(self, search_info: str = '', *, from_log: str = None, first: bool = False) -> NoReturn:
        logs = self.search_logs
        s_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        d_datetime = datetime.now()
        filter_value = from_log if from_log else s_time + ': ' + search_info
        if first == False:
            if self.listWidget_3.count() >= logs.max_length:
                self.listWidget_3.removeItem(logs.max_length - 1)
            swidget = _SearchRecordWidget(
                filter_value, self.listWidget_3, logs)
            swidget.datetime = d_datetime
            self.listWidget_3.appendItem(
                filter_value, swidget, meta={'logs': logs, 'time': d_datetime})
        else:
            if self.listWidget_3.count() >= logs.max_length:
                self.listWidget_3.removeItem(logs.max_length - 1)
            swidget = _SearchRecordWidget(
                filter_value, self.listWidget_3, logs)
            swidget.datetime = d_datetime
            self.listWidget_3.appendTop(filter_value, swidget, meta={
                                        'logs': logs, 'time': d_datetime})
        if self.current_list:
            msg = '下载记录' if self.current_list == self.listWidget_2 else '搜索记录'
            self.label_5.setText(f' 共:{self.current_list.filterCount()}个{msg}')

    def eventFilter(self, obj, event) -> NoReturn:
        if event.type() == QEvent.WindowDeactivate:
            if self.flag == 0:
                self.close()
        return QDialog.eventFilter(self, obj, event)

    def closeEvent(self, event) -> NoReturn:
        super().closeEvent(event)
        self.is_debug = False

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self._add_shadow:
            shadow_width = 5
            path = QPainterPath()
            path.setFillRule(Qt.WindingFill)
            path.addRect(shadow_width, shadow_width, self.width()-shadow_width * 2, self.height()-shadow_width * 2)

            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.fillPath(path, QBrush(Qt.white))

            color = QColor(0, 0, 0, 50)
            for i in range(10):
                path = QPainterPath()
                path.setFillRule(Qt.WindingFill)
                # path.addRoundedRect(10-i, 10-i, self.width()-(10-i) * 2, self.height()-(10-i)*2, 5, 5)
                path.addRect(10-i, 10-i, self.width()-(10-i)
                             * 2, self.height()-(10-i)*2)
                color.setAlpha(150 - sqrt(i)*50)
                painter.setPen(color)
                painter.drawPath(path)


if __name__ == '__main__':
    app = QApplication([])
    dialog = PopDialog('')
    dialog.show()
    app.exec_()
