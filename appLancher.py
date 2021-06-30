#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: fatebibi

import sys

from pyqt_app import (NovelWidget, FramelessWindow, PopDialog, MenuButton,
                      SelectDialog, CommonPixmaps, StyleSheets, ncalls,
                      InfoLabel, setIconsToolTip, startTransferSever,
                      get_local_ip, PageState, TransferSeverState, load_plugin,
                      qmixin)

from multiprocessing import freeze_support, Queue

from PyQt5.QtCore import QRectF, Qt, QPoint, QUrl, QRegExp, pyqtSignal, pyqtSlot, QTranslator
from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QCompleter, QHBoxLayout, QMessageBox, QMenu, QFrame
from PyQt5.QtGui import QColor, QDesktopServices, QFontDatabase, QFontMetrics, QIcon, QFont, QPainter, QPixmap

from crawl_novel import InfoObj


@qmixin
class GuiMain(FramelessWindow):

    plugin_loaded = load_plugin()

    title = 'F.xx.k'

    ico = CommonPixmaps.app_ico

    # ico_size = 20

    # bar_height = 38

    restart_code = 1000

    bar_color = Qt.lightGray

    select_signal = pyqtSignal(bool)

    def __init__(self, queue: Queue):
        super().__init__()
        self.titleBarInit()
        self.setMenubar()
        self.setCommand()
        self.loadSources()
        self.search_mode = '极速模式'
        self.novel_widget = NovelWidget(queue, self)
        self.popdialog = PopDialog(self)
        self.selectdialog = SelectDialog(self)
        self.setWidget(self.novel_widget)
        self.setMinimumWidth(QApplication.desktop().width() * .5)
        self.setMinimumHeight(QApplication.desktop().height() * .65)
        self.setContentsMargins(0, 0, 0, 0)
        self.transfer_state = TransferSeverState()
        self.dft_style = self.styleSheet()
        self.novel_dft_style = self.novel_widget.styleSheet()
        self.pop_dft_style = self.popdialog.styleSheet()
        self.setSlots()

    def closeEvent(self, event) -> None:
        if self.novel_widget.activeDownCounts() > 0:
            message = QMessageBox(self)
            message.setIcon(QMessageBox.Warning)
            message.setWindowTitle('警告')
            message.setText('小说下载未完成, 确认退出么?')
            yes = message.addButton('确认', QMessageBox.YesRole)
            no = message.addButton('取消', QMessageBox.NoRole)
            message.exec_()
            answer = message.clickedButton()
            if answer == yes:
                self.novel_widget.beforeClose()
                self.popdialog.close()
                event.accept()
            else:
                event.ignore()
        else:
            self.novel_widget.beforeClose()
            self.popdialog.close()
            event.accept()

    def setSlots(self) -> None:
        site_button = self.novel_widget.site_button
        self.select_signal.connect(site_button.selectAll)
        site_button.select_signal.connect(
            lambda state: self.select_action.setChecked(state))

    def titleBarInit(self) -> None:
        fm = QFontMetrics(QFont('微软雅黑', 9))
        self.bar_height = fm.height() * 1.5 + 6
        self.setIconSize(self.bar_height - 6)  # 标题栏尺寸
        self.setTitleBarColor(self.bar_color)  # 标题栏颜色
        self.setTitleBarHeight(self.bar_height)  # 标题栏高度
        self.setWindowIcon(QIcon(self.ico))  # 标题ico
        self.setWindowTitle(self.title)  # 设置标题

    def setCommand(self) -> None:
        frame = QFrame()
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        help_button = QPushButton()
        help_button.setStyleSheet('border:none')
        help_button.setFixedWidth(32)
        help_button.setIcon(QIcon(CommonPixmaps.command_help_button))
        help_button.setCursor(Qt.PointingHandCursor)
        help_button.clicked.connect(lambda: QMessageBox.information(
            self, '更多命令',
            '''url:1 :打开第一个搜索结果的原始页面\ngoto:1 :定位到第一个搜索结果页面\nprogramDir: 打开项目配置文件目录\n
        '''))

        self.lineedit = QLineEdit()
        self.lineedit.setFont(QFont('黑体', 9))
        self.lineedit.setPlaceholderText('命令窗口')
        self.lineedit.setContextMenuPolicy(Qt.NoContextMenu)
        self.lineedit.setStyleSheet('border-radius: 0px; border:none')
        completer = QCompleter([
            'home', 'imagesview', 'listview', 'resetSettings', 'log',
            'clearCache', 'programDir', 'goto:', 'url:', 'debug', 'path',
            'cancelEngines', 'openSettings'
        ])
        completer.setCompletionMode(QCompleter.InlineCompletion)  # 不全模式
        self.lineedit.setCompleter(completer)
        self.setStrWidth(self.lineedit, '  11111111111        ')

        exit_button = QPushButton()
        exit_button.setStyleSheet('border:none')
        exit_button.setIcon(QIcon(CommonPixmaps.command_exit_button))
        exit_button.setCursor(Qt.PointingHandCursor)
        exit_button.clicked.connect(self.openCmdline)

        lay.addWidget(help_button, 0)
        lay.addWidget(self.lineedit, 20)
        lay.addWidget(exit_button, 0)

        self.cmd_frame = frame
        self.addTitleWidget(self.cmd_frame, 0, True)
        self.lineedit.returnPressed.connect(self.macros)
        self.cmd_frame.hide()
        self.cmd_frame.setFixedWidth(help_button.width() +
                                     self.lineedit.width())

        label = InfoLabel()
        label.setStyleSheet('background:transparent;color: #495062')
        label.setFont(QFont('微软雅黑', 9))
        label.setIndent(5)
        label.setAlignment(Qt.AlignVCenter)
        self.addTitleWidget(label, 50)
        self.msg_label = label

    def titleMsgInfo(self, text: str) -> None:
        self.msg_label.setText(text)

    def resizeTitleBar(self, height: int) -> None:
        self.setTitleBarHeight(height)
        self.b1.setFixedHeight(height)
        self.b2.setFixedHeight(height)
        self.mode_button.buttonSize = height
        self.tip_button.buttonSize = height
        self.transfer_button.buttonSize = height

    def resizeIconWidget(self, scaled: float) -> None:
        self.novel_widget.listWidget_2.resizeIconWidget(scaled)
        self.novel_widget.listWidget_3.resizeIconWidget(scaled)

    def setMenubar(self) -> None:
        def tipButtonPolicy():
            self.tip_button.onClicked()
            if self.tip_button.isChecked():
                self.titleMsgInfo('显示搜索提示信息')
                setIconsToolTip(True)
                self.novel_widget.settings.setValue('Settings/infomode', True)
            else:
                self.titleMsgInfo('关闭搜索提示信息')
                setIconsToolTip(False)
                self.novel_widget.settings.setValue('Settings/infomode', False)

        def modeButtonPolicy():
            self.mode_button.onClicked()
            if self.mode_button.isChecked():
                self.search_mode = '极速模式'
                self.popdialog.radioButton.setChecked(True)
                msg = '极速模式: 搜索速度较快,不保证查找内容最新,缓存搜索结果'
            else:
                self.search_mode = '最新模式'
                self.popdialog.radioButton_2.setChecked(True)
                msg = '最新模式: 搜索速度较慢,但保证查找内容为最新,不缓存搜索结果'
            self.titleMsgInfo(msg)

        def transferButtonPolicy():
            self.transfer_button.onClicked()
            if self.transfer_button.isChecked():
                p = startTransferSever(self.novel_widget.getSavePath())
                self.transfer_state.set_process(p)
                ip_address = get_local_ip()
                self.showTransferPage(ip_address,
                                      self.transfer_state.is_alive())
                msg = f'无线传输已打开: 访问 <b>http{ip_address}</b> 或扫描二维码'
            else:
                self.transfer_state.terminte_process()
                msg = f'无线传输已关闭'
            self.titleMsgInfo(msg)

        tr_c1 = CommonPixmaps.menu_wifi_transfer
        tr_uc1 = CommonPixmaps.menu_wifi_close
        transfer_button = MenuButton(tr_c1, tr_uc1, self.bar_height, (.7, .6),
                                     False)
        transfer_button.setToolTips('<b>无线传输已打开</b>', '<b>无线传输已关闭</b>')
        self.addTitleWidget(transfer_button, 0)
        self.transfer_button = transfer_button
        self.transfer_button.clicked.connect(transferButtonPolicy)

        rc_c = CommonPixmaps.menu_info_show
        rc_uc = CommonPixmaps.menu_info_close
        rc_t = '<b>显示搜索结果提示内容</b>'
        rc_ut = '<b>关闭搜索结果提示信息</b>'
        tip_button = MenuButton(rc_c, rc_uc, self.bar_height)
        tip_button.setToolTips(rc_t, rc_ut)
        self.addTitleWidget(tip_button, 0)
        self.tip_button = tip_button
        self.tip_button.clicked.connect(tipButtonPolicy)

        mb_c = CommonPixmaps.menu_search_fast
        mb_uc = CommonPixmaps.menu_search_slow
        mb_t = '<b>搜索模式:极速模式</b>'
        mb_ut = '<b>关闭搜索结果提示信息</b>'
        mode_button = MenuButton(mb_c, mb_uc, self.bar_height)
        mode_button.setToolTips(mb_t, mb_ut)
        self.addTitleWidget(mode_button, 0)
        self.mode_button = mode_button
        self.mode_button.clicked.connect(modeButtonPolicy)

        menu_frame = QFrame()
        menu_frame.setFrameShape(QFrame.NoFrame)
        menu_frame.setStyleSheet(StyleSheets.menubar_button_style)
        frame_lay = QHBoxLayout(menu_frame)
        frame_lay.setContentsMargins(0, 0, 0, 0)
        frame_lay.setSpacing(0)
        self.addLeftTitleWidget(menu_frame, autoheight=False)

        menu = QMenu()
        menu.setStyleSheet(StyleSheets.menubar_menu_style)
        menu_width = menu.fontMetrics().width('设置所有搜索源头') * 1.5
        menu.setFixedWidth(menu_width)
        a1 = menu.addAction(
            QIcon(
                QPixmap(CommonPixmaps.menu_command).scaled(
                    18, 18, transformMode=Qt.SmoothTransformation)), '命令面板')
        a2 = menu.addAction(QIcon(CommonPixmaps.menu_logs), '输出日志')
        menu.addSeparator()
        a3 = menu.addAction('搜索记录')
        a4 = menu.addAction('下载记录')
        menu.addSeparator()
        a0 = menu.addAction(QIcon(CommonPixmaps.menu_debug), '调试面板')
        a5 = menu.addAction('命令窗口')
        a5.setShortcut('x')
        menu.addSeparator()
        a6 = menu.addAction(QIcon(CommonPixmaps.menu_wifi_address), '传输地址')
        a6.setShortcut('F1')
        a6.triggered.connect(lambda: self.showTransferPage(
            get_local_ip(), self.transfer_state.is_alive()))
        a0.setShortcut('q')
        a1.setShortcut('p')
        a2.setShortcut('l')
        a3.setShortcut('s')
        a4.setShortcut('d')
        a0.triggered.connect(self.showDebug)
        a1.triggered.connect(self.showMacros)
        a2.triggered.connect(lambda: self.novel_widget.openLogFile())
        a3.triggered.connect(self.showSearchRecords)
        a4.triggered.connect(self.showRecords)
        a5.triggered.connect(self.openCmdline)

        button_width = QFontMetrics(QFont('微软雅黑', 9)).width('设') * 4 + 6
        button = QPushButton()
        button.setMenu(menu)
        button.setFixedSize(button_width, self.bar_height)
        button.setText('查看')
        self.b1 = button

        menu = QMenu()
        menu.setStyleSheet(StyleSheets.menubar_menu_style)
        menu.setFixedWidth(menu_width)
        a1 = menu.addAction(QIcon(CommonPixmaps.menu_search_mode), '搜索模式')
        a1.setShortcut('f2')
        a2 = menu.addAction('下载线程')
        a3 = menu.addAction(
            QIcon(
                QPixmap(CommonPixmaps.menu_load_plugins).scaled(
                    18, 18, transformMode=Qt.SmoothTransformation)), '插件加载')
        a4 = menu.addAction('界面预览')
        menu.addSeparator()
        a5 = menu.addAction('选择所有搜索源')
        self.select_action = a5
        a5.setCheckable(True)
        a6 = menu.addAction('关于')
        a1.triggered.connect(self.showSettings)
        a2.triggered.connect(self.showSettings)
        a3.triggered.connect(self.showSettings)
        a4.triggered.connect(self.showUI)
        a5.triggered.connect(lambda: self.select_signal.emit(a5.isChecked()))
        a6.triggered.connect(self.information)

        button = QPushButton()
        button.setMenu(menu)
        button.setFixedSize(button_width, self.bar_height)
        button.setText('设置')
        self.b2 = button
        frame_lay.addWidget(self.b2)
        frame_lay.addWidget(self.b1)

    def information(self) -> None:
        message = QMessageBox(self)
        message.setWindowTitle('关于')
        message.setText('版本: v1.0\n作者: fatebibi\n')
        message.addButton(QMessageBox.Ok)
        message.button(QMessageBox.Ok).hide()
        message.setFixedSize(200, 100)
        message.exec_()

    def _setState(self) -> None:
        if self.search_mode == '极速模式':
            self.mode_button.setChecked(True)
            self.mode_button.setToolTip('<b>搜索模式: 极速模式</b>')
            self.popdialog.radioButton.setChecked(True)
            msg = '极速模式: 搜索速度较快,不保证查找内容最新,缓存搜索结果'
        elif self.search_mode == '最新模式':
            self.mode_button.setChecked(False)
            self.mode_button.setToolTip('<b>搜索模式: 最新模式</b>')
            self.popdialog.radioButton_2.setChecked(True)
            msg = '最新模式: 搜索速度较慢,但保证查找内容为最新,不缓存搜索结果'
        self.titleMsgInfo(msg)

    def prepareRestart(self) -> None:
        self.showRecords.clear()
        self.showDebug.clear()
        self.showSearchRecords.clear()
        self.showUI.clear()
        self.showFail.clear()
        self.popdialog.textBrowser.clearAllLines()

    def loadSources(self) -> None:
        self.de_focus_color = QColor(30, 30, 30, 50)
        self.font_familys = []
        font_index = QFontDatabase.addApplicationFont('./fonts/仓耳今楷04-W03.ttf')
        self.font_family = QFontDatabase.applicationFontFamilies(
            font_index).pop()
        self.font_familys.append(self.font_family)

        font_index = QFontDatabase.addApplicationFont(
            './fonts/FZYanSJW_Xian.ttf')
        font_name = QFontDatabase.applicationFontFamilies(font_index).pop()
        self.font_familys.append(font_name)

        font_index = QFontDatabase.addApplicationFont(
            './fonts/FZYouSJW_507R.TTF')
        font_name = QFontDatabase.applicationFontFamilies(font_index).pop()
        self.font_familys.append(font_name)

    def _showpopdialog(self, *, resize: tuple = None, dy: int = None) -> None:
        if resize:
            self.popdialog.resize(*resize)
        width, height = self.width(), self.height()
        width_d, height_p = self.popdialog.width(), self.popdialog.height()
        y = dy if dy else self.bar_height
        point = self.mapToGlobal(QPoint((width - width_d) / 2, y))
        self.popdialog.move(point)

    def _showselectdialog(self, *, resize: tuple = None) -> None:
        if resize:
            self.selectdialog.resize(*resize)
        width, height = self.width(), self.height()
        width_d, height_p = self.selectdialog.width(
        ), self.selectdialog.height()
        point = self.mapToGlobal(
            QPoint((width - width_d) / 2, self.bar_height + 50))
        self.selectdialog.move(point)

    def showSelected(self, inf: InfoObj) -> None:
        w, h = self.minimumWidth(), self.minimumHeight()
        self._showselectdialog(resize=(w * .7, h * .7))
        self.selectdialog.addChapter(inf)
        self.selectdialog.show()
        self.selectdialog.gotoSelectedPage()
        self.novel_widget.infs_widget.desFocus(self.de_focus_color)
        self.update()

    def showTransferPage(self, ip_address: str, is_alive: bool) -> None:
        w, h = self.minimumWidth(), self.minimumHeight()
        self._showselectdialog(resize=(w * .7, h * .7))
        self.selectdialog.show()
        self.selectdialog.gotoTransferPage(ip_address, is_alive)
        if self.novel_widget.infs_widget:
            self.novel_widget.infs_widget.desFocus(self.de_focus_color)
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.selectdialog.is_show:
            painter = QPainter(self)
            painter.fillRect(QRectF(self.rect()), self.de_focus_color)

    @pyqtSlot()
    def macros(self) -> None:
        command = self.lineedit.text().lower().strip()
        if command:
            if command == 'home':
                self.novel_widget.gotoHello()
            elif command == 'imagesview':
                self.novel_widget.gotoImgPage()
            elif command == 'listview':
                self.novel_widget.gotoListPage()
            elif command == 'resetsettings':
                self.novel_widget.resetSettings()
            elif command == 'opensettings':
                self.novel_widget.openSettings()
            # elif command == 'restart':
            #     QApplication.exit(self.restart_code)  # 重启
            elif command == 'path':
                self.novel_widget.chooseSavePath()
            elif command == 'log':
                self.novel_widget.openLogFile()
            elif command == 'clearcache':
                self.novel_widget.clearHttpCaches()
            elif command == 'programdir':
                self.novel_widget.openProgramDir()
            elif command.startswith('goto:'):
                page = command.replace('goto:', '')
                rx = QRegExp(r'^goto:\d+$')
                if rx.exactMatch(command):
                    widget = self.novel_widget.getSearchWidget(int(page) - 1)
                    if widget:
                        self.novel_widget.gotoIntroutced(widget.info)
            elif command.startswith('url:'):
                page = command.replace('url:', '')
                rx = QRegExp(r'^url:\d+$')
                if rx.exactMatch(command):
                    if self.novel_widget.page_state != PageState.subscribe_page:
                        widget = self.novel_widget.getSearchWidget(
                            int(page) - 1)
                    else:
                        widget = self.novel_widget.getSubscribeWidget(
                            int(page) - 1)
                    if widget:
                        url = widget.info.novel_info_url
                        QDesktopServices.openUrl(QUrl(url))
            elif command == 'debug':
                self.showDebug()

    @pyqtSlot()
    def openCmdline(self) -> None:
        if self.cmd_frame.isHidden():
            self.cmd_frame.show()
            self.novel_widget.comboBox_2.search_line.clearFocus()
            self.lineedit.setFocus(True)
        else:
            self.cmd_frame.hide()
            self.lineedit.clear()
            self.lineedit.clearFocus()
            self.novel_widget.setFocus(True)

    @pyqtSlot()
    def showMacros(self) -> None:
        w, h = self.minimumWidth(), self.minimumHeight()
        self._showpopdialog(resize=(w * .7, h * .7))
        self.popdialog.gotoMacros()
        self.popdialog.show()

    @pyqtSlot(bool)
    def showSettings(self, flag: bool = False) -> None:
        # self.novel_widget.computeSearchCacheSize()
        self.novel_widget.computeImagesCacheSize()
        w, h = self.minimumWidth(), self.minimumHeight()
        self._showpopdialog(resize=(w * .7, h * .7))
        self.popdialog.gotoSettings()
        self.popdialog.show()

    @ncalls
    def showSearchRecords(self, flag: bool = False) -> None:
        if self.showSearchRecords.ncalls() == 1:
            self.popdialog.selectTodaySearchRecords()
        w, h = self.minimumWidth(), self.minimumHeight()
        self._showpopdialog(resize=(w * .8, h * .7))
        self.popdialog.gotoSearchRecords()
        self.popdialog.show()

    @ncalls
    def showRecords(self, flag: bool = False) -> None:
        if self.showRecords.ncalls() == 1:
            self.popdialog.selectTodayDownRecords()
        w, h = self.minimumWidth(), self.minimumHeight()
        self._showpopdialog(resize=(w * .8, h * .7))
        self.popdialog.gotoRecords()
        self.popdialog.show()

    @ncalls
    def showDebug(self, flag: bool = False) -> None:
        if self.showDebug.ncalls() == 1:
            self.popdialog.textBrowser.horizontalScrollBar().setValue(0)
        w, h = self.minimumWidth(), self.minimumHeight()
        self._showpopdialog(resize=(w * .8, h * .8))
        self.popdialog.gotoDebug()
        self.popdialog.show()

    @ncalls
    def showUI(self,
               flag: bool = False,
               scaled_w: float = .8,
               scaled_h: float = .8,
               hide: bool = False,
               with_title: bool = True,
               add_shadow: bool = False) -> None:
        if self.showUI.ncalls() == 1:
            self.popdialog.textBrowser.horizontalScrollBar().setValue(0)
        w, h = self.minimumWidth(), self.minimumHeight()
        self._showpopdialog(resize=(scaled_w * w, scaled_h * h),
                            dy=self.bar_height + 20)
        self.popdialog.gotoUi(hide, with_title, add_shadow)
        self.popdialog.setWindowIcon(QIcon(CommonPixmaps.pop_window_ico))
        self.popdialog.show()

    @ncalls
    def showFail(self, flag: bool = False) -> None:
        w, h = self.minimumWidth(), self.minimumHeight()
        self._showpopdialog(resize=(w * .8, h * .8))
        self.popdialog.gotoFail()
        self.popdialog.show()

    def styleRead(self) -> None:
        self.novel_widget.layout().setContentsMargins(5, 5, 5, 5)
        self.novel_widget.setStyleSheet(self.novel_dft_style)
        self.popdialog.setStyleSheet(self.pop_dft_style)
        self.setStyleSheet(self.dft_style)

    @staticmethod
    def application_main(queue: Queue) -> None:
        while True:
            app = QApplication(sys.argv)
            translator = QTranslator()
            translator.load('./tpls/qt_zh_CN.qm')
            app.installTranslator(translator)
            window = GuiMain(queue)
            window.show()
            ret = app.exec_()
            if ret != GuiMain.restart_code:
                break
            window.prepareRestart()
            del window
            del app


if __name__ == '__main__':
    freeze_support()
    process_queue = Queue()
    GuiMain.application_main(process_queue)
