import os
import shutil
import logging
import requests

from scrapy.utils.project import get_project_settings

from PyQt5.QtWidgets import (QWidget, QApplication, QButtonGroup, QFileDialog,
                             QMessageBox)
from PyQt5.QtCore import (Qt, QStandardPaths, QDir, pyqtSignal, pyqtSlot,
                          QSize, QThread, QThreadPool, QSettings, QUrl,
                          QFileInfo, QFile, QSemaphore)
from PyQt5.QtGui import QIcon, QMovie, QPixmap, QDesktopServices, QFont, QColor

from typing import List, Any, Tuple
from queue import Queue  # 调度下载

from .novelwidgetui import Ui_Form
from .popwindow import PopDialog

from .searchwidget import SearchInfoWidget  # 下载列表容器
from .taskwidget import TaskWidget, PageState  # 下载详情页面
from .customwidgets import IconWidget, get_subscribeLinkobj, setIconsToolTip, SubscribeWidget, SubState  # 下载详情页面

from .common_srcs import StyleSheets

from .startUpScrapy import startBothByOrder
from .magic import lasyproperty, enter_hook
from .log_supports import getSearchLog, _MessageHandler
from .plugins_support import HumReadMixin, load_plugin
from .backstage_support import getBackThread
from .update_supports import AppUpdateManager

from crawl_novel import ImgDownTask, InfoObj, BasicFileSpider, get_cached_spiders, DownStatus


__all__ = ('NovelWidget', )

updater = AppUpdateManager()
updater.get_tpls_update()


class SpiderController(QThread):  # scrapy监视线程
    info_signal = pyqtSignal(InfoObj)
    scrapy_message_signal = pyqtSignal(str)
    display_signal = pyqtSignal()

    def __init__(self, q):
        super().__init__()
        self.process_q = q

    def run(self):
        while True:
            info = self.process_q.get()
            if isinstance(info, InfoObj):
                self.info_signal.emit(info)
            elif isinstance(info, str):  # 更新调试面板信息
                self.scrapy_message_signal.emit(info)
            elif isinstance(info, bool):  # 查找结束
                self.display_signal.emit()
                break


class ImageController(QThread):  # 图片监视线程
    def __init__(self,
                 img_q: Queue,
                 img_pool: QThreadPool,
                 max_threads: int = None):
        super().__init__()
        self.max_threads = max_threads
        self.img_pool = img_pool
        self.img_q = img_q
        self._set = set()

    def run(self):
        if self.max_threads:
            self.img_pool.setMaxThreadCount(self.max_threads)
        while True:
            down_info: InfoObj = self.img_q.get()
            if (down_info.novel_img_url in self._set) == False:
                self._set.add(down_info.novel_img_url)
                down_task = ImgDownTask(down_info)
                down_task.setAutoDelete(True)  # 自动删除
                self.img_pool.start(down_task)

    def schedule(self):
        self.start()


class NovelWidget(QWidget, Ui_Form, HumReadMixin):

    app_name: str = 'qt_novel_search_app'

    app_dir: str = QDir(
        QStandardPaths.writableLocation(
            QStandardPaths.HomeLocation)).absoluteFilePath(f'.{app_name}') # 程序缓存根目录

    # config: str = 'Fxxk.ini'

    caches: str = 'http_caches'

    image_caches: str = 'image_caches'

    log_file: str = 'logs/log.txt'

    down_caches: str = 'down_caches'

    subscribe_caches: str = 'subscribe_caches'

    read_caches: str = 'read_caches'

    active_result: list = []

    hello_size = 160, 160

    def _setNotFound(self):
        model1 = '<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">{}</span></p></body></html>'
        self.label_6.setText(model1.format('抱歉'))
        self.label_5.setText(model1.format(f'未查找到`{self.search_content}`相关内容'))
        self.label.setPixmap(
            QPixmap(':/ico/20210327094128322_easyicon_net_256.ico').scaled(
                QSize(*self.hello_size),
                transformMode=Qt.SmoothTransformation))

    def _helloReset(self):
        model1 = '<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">输入</span></p></body></html>'
        model2 = '<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">小说名</span><span style=" font-size:10pt; color:#7d7d7d;">或者</span><span style=" font-size:11pt; font-weight:600;">作者名</span></p></body></html>'
        self.label_6.setText(model1)
        self.label_5.setText(model2)
        self.label.setPixmap(
            QPixmap(':/ico/search_1311349_easyicon.net.svg').scaled(
                QSize(*self.hello_size),
                transformMode=Qt.SmoothTransformation))

    def activeDownCounts(self) -> int:
        available = self.thread_seam.available()
        active_count = self.max_threads - available
        return active_count

    @staticmethod
    def _scrapyLogHandler() -> _MessageHandler:
        handler = _MessageHandler()
        handler.setLevel(logging.NOTSET)
        return handler

    def internetOk(self, warning=True) -> bool:
        try:
            resp = requests.get('http://www.baidu.com')
            return resp.ok
        except:
            if warning:
                QMessageBox.warning(self, '警告', '请保持网络已连接!')
            return False
        return True

    def updatedSubmitInfos(self) -> List[InfoObj]:
        res = []
        for subs_widget in self.listWidget_3.itemWidgets():
            res.append(subs_widget.info)
        return res

    def load_subscribe_infos(self) -> List[InfoObj]:
        qdir = self.getSubscribeDir()
        qdir.setFilter(QDir.Files | QDir.NoDotAndDotDot)
        res = []
        for info in qdir.entryInfoList():
            path = info.absoluteFilePath()
            if path.endswith('json'):
                inf = InfoObj.fromPath(path)
                res.append(inf)
        res.sort(key=lambda inf: inf.novel_subs_index)
        return res

    def getDownRecords(self) -> List[str]:
        qdir = self.getDownCachesDir()
        qdir.setFilter(QDir.Files | QDir.NoDotAndDotDot)
        res = []
        for info in qdir.entryInfoList():
            path = info.absoluteFilePath()
            if path.endswith('json'):
                res.append(info.absoluteFilePath())
        return res

    def getSearchRecords(self) -> List:
        pass

    @property
    def pop_dialog(self) -> PopDialog:
        return self._parent.popdialog

    @property
    def main_gui(self):
        return self._parent

    @property
    def search_content(self) -> str:
        return self.search_line.text().strip()

    @pyqtSlot(str)
    def titleMsgInfo(self, msg: str, strong=False, color=None) -> None:
        # if self.infs_widget and self.infs_widget.stackedWidget_2.currentIndex(
        # ) == 0:  # 阅读页面
        if self.infs_widget and self.infs_widget.in_read:
            self.infs_widget.readbar_widget.titleMsgInfo(msg, strong, color)
        else:
            show_color = QColor(color)
            info_msg = f'<b>{msg}</b>' if strong else msg
            info_msg = f'<font color="{show_color.name()}">{info_msg}</font>' if color else info_msg
            self._parent.titleMsgInfo(info_msg)

    def computeSearchCacheSize(self) -> str:
        path = self.getCachesDir().absolutePath()
        self.bkg_thread.add_task(self._getFileSize,
                                 args=(path, ),
                                 callback=lambda res: self.bkg_thread.done_sig.
                                 emit('searchCacheSize', res))

    def computeImagesCacheSize(self) -> str:
        path = self.getImagesDir().absolutePath()
        self.bkg_thread.add_task(self._getFileSize,
                                 args=(path, ),
                                 callback=lambda res: self.bkg_thread.done_sig.
                                 emit('imagesCacheSize', res))

    def afterBkgTask(self, func_name: str, result: Any) -> None:
        if func_name == 'searchCacheSize':
            self.search_cache_size = result
        elif func_name == 'imagesCacheSize':
            self.image_cache_size = result
        elif func_name == 'clearhttpcache':
            if result:
                self.titleMsgInfo('搜索缓存已清除')
                self.search_cache_size = 0
            else:
                self.titleMsgInfo('缓存未清除')
        elif func_name in self.site_button.site_names:
            self.search_cache_size -= result
            self.titleMsgInfo(f'<b>{func_name}</b>{result}')

    def _getFileSize(self, filePath: str, size: int = 0) -> int:
        for root, dirs, files in os.walk(filePath):
            for f in files:
                size += os.path.getsize(os.path.join(root, f))
        return size

    @pyqtSlot(str, int)
    def log(self, msg: str, level: int = logging.DEBUG, **kwargs) -> None:
        if self.pop_dialog.is_debug:
            self.pop_dialog.textBrowser.logger.log(level, msg, **kwargs)

    def forceLog(self, msg: str, level: int, **kwargs):
        self.pop_dialog.textBrowser.forceLog(msg, level, **kwargs)

    def programDirs(self) -> QDir:  # 程序缓存，配置文件的保存目录
        return QDir(self.app_dir)  # '~/.app_name'

    def openProgramDir(self) -> None:  # 打开程序目录
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.app_dir))

    def getNovelSize(self) -> QSize:  # 小说封面大小
        return QSize(IconWidget.scaled * IconWidget.IMG_DFT_SIZE[0],
                     IconWidget.scaled * IconWidget.IMG_DFT_SIZE[1])

    def getReadCachesDir(self) -> QDir:
        program_qdir = self.programDirs()
        if program_qdir.exists(self.read_caches) == False:
            program_qdir.mkdir(self.read_caches)
        return QDir(program_qdir.absoluteFilePath(self.read_caches))

    def getLogFilInfo(self) -> QFileInfo:
        jude = QDir()
        app_dir = QDir(self.app_dir)
        file_info = QFileInfo(app_dir.absoluteFilePath(self.log_file))
        if jude.exists(app_dir.absoluteFilePath(self.log_file)) == False:
            jude.mkpath(file_info.absolutePath())
        return QFileInfo(QDir(self.app_dir).absoluteFilePath(self.log_file))

    def getSubscribeDir(self) -> QDir:  # 获取订阅缓存目录
        program_qdir = self.programDirs()
        if program_qdir.exists(self.subscribe_caches) == False:
            program_qdir.mkdir(self.subscribe_caches)
        return QDir(program_qdir.absoluteFilePath(self.subscribe_caches))

    def getDownCachesDir(self) -> QDir:  # 获取下载缓存目录
        program_qdir = self.programDirs()
        if program_qdir.exists(self.down_caches) == False:
            program_qdir.mkdir(self.down_caches)
        return QDir(program_qdir.absoluteFilePath(self.down_caches))

    def getCachesDir(self) -> QDir:  # 获取http缓存目录
        return QDir(QDir(self.app_dir).absoluteFilePath(self.caches))

    def getImagesDir(self) -> QDir:  # 获取image缓存目录
        return QDir(QDir(self.app_dir).absoluteFilePath(self.image_caches))

    def getConfigFileInfo(self) -> QFileInfo:
        return QFileInfo(QDir(self.app_dir).absoluteFilePath(self.config))

    def clearHttpCachesBySite(self, site: str) -> None:
        def task_func(path):
            try:
                res = self._getFileSize(path)
                shutil.rmtree(path)
            finally:
                return res

        http_path = self.getCachesDir().absoluteFilePath(site)
        if os.path.exists(http_path):
            if self.info_thread.isRunning() == False:

                def callback(res):
                    self.bkg_thread.done_sig.emit(site, res)

                def errback(e):
                    self.bkg_thread.done_sig.emit(site, '搜索缓存删除失败!')

                self.bkg_thread.add_task(func=task_func,
                                         args=(http_path, ),
                                         callback=callback,
                                         errback=errback)
            else:
                self.titleMsgInfo(f'<b>{site}</b>搜索缓存已删除')
        else:
            self.titleMsgInfo(f'<b>{site}</b>搜索缓存已删除')

    def clearImageCachesBySite(self, site: str):
        pass

    def _buttonsInit(self) -> None:
        height = self.site_button.height()
        width = self.site_button.width() * 0.7
        self.down_pushButton.setFixedHeight(height)
        self.clear_pushButton.setFixedHeight(height)
        self.search_pushButton.setFixedHeight(height)
        self.down_pushButton.setFixedWidth(width)
        self.clear_pushButton.setFixedWidth(width)
        self.search_pushButton.setFixedWidth(width)
        self.fresh_button.setFixedHeight(height)
        fm = self.fresh_button.fontMetrics()
        width = fm.width('获取最新章节积极级')
        self.fresh_button.setFixedWidth(width)

    def __enter__(self):
        self.thread_seam.acquire()

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.thread_seam.release()

    def __init__(self, queue: 'multiprocessing.Queue', parent=None) -> None:
        super().__init__()
        self.init(queue, parent)

    def setSearchBarVisable(self, state: bool):
        if state:
            self.frame.show()
        else:
            self.frame.hide()

    def init(self, queue: 'multiprocessing.Queue', parent: 'GuiMain') -> None:
        self.setMouseTracking(True)
        self.setupUi(self)
        enter_hook(widgets=[
            self.frame, self.frame_2, self.frame_3, self.stackedWidget,
            self.stackedWidget_2
        ])
        self.setSubscribeSlots()
        self.subscribe_urls = set()
        self.page_state = PageState.other
        self.blockSignals(True)
        self._buttonsInit()
        self.search_log = getSearchLog(self.programDirs().absolutePath())
        self._loger = None
        self._searchloger = None
        self.scrapy_settings = None
        self.infs_widget = None
        self.max_threads = 15
        self.thread_seam = QSemaphore(self.max_threads)

        self.process_queue = queue
        self._parent = parent
        self.config = '%s.ini' % parent.title
        self.info_thread = SpiderController(self.process_queue)  # 更新信息线程

        self._downSchedule()

        self.bkg_thread = getBackThread()
        self.bkg_thread.done_sig.connect(self.afterBkgTask)
        self.bkg_thread.start()

        self.info_thread.info_signal.connect(self.updateSearchMessage)  # 更新结果
        self.info_thread.display_signal.connect(self._switch)  # 搜完成成
        self.info_thread.scrapy_message_signal.connect(self.updateScrapyLogs)
        self.fold_pushButton.clicked.connect(self.chooseSavePath)

        self.listWidget.verticalScrollBar().setStyleSheet(
            StyleSheets.green_v_scroll_style)
        self.listWidget.setStyleSheet(StyleSheets.list_page_style)

        self.listWidget_2.verticalScrollBar().setStyleSheet(
            StyleSheets.green_v_scroll_style)
        self.listWidget_2.setStyleSheet(StyleSheets.icon_page_style)

        self.listWidget_3.verticalScrollBar().setStyleSheet(
            StyleSheets.green_v_scroll_style)
        self.listWidget_3.setStyleSheet(StyleSheets.submit_list_style)

        self.search_movie = QMovie(':/ico/refresh.gif')
        self.search_movie.setCacheMode(QMovie.CacheNone)
        self.search_movie.setSpeed(100)  # 播放速度
        self.search_label.setMovie(self.search_movie)

        self.checkBox.stateChanged.connect(self.selectAllPolicy)
        self.down_pushButton.clicked.connect(self.downAll)

        self.search_line = self.comboBox_2.search_line
        self.search_line.state = 0  # 0,未搜索,1搜索中,2搜索结束
        self.comboBox_2.setFixedHeight(self.site_button.height())
        self.search_line.returnPressed.connect(self.searchNovel)
        self.clear_pushButton.clicked.connect(self.clearSearchRecords)

        self.viewgroup = QButtonGroup()
        self.viewgroup.addButton(self.pushButton)
        self.viewgroup.addButton(self.pushButton_2)
        self.viewgroup.addButton(self.subs_pushButton)
        self.viewgroup.buttonClicked.connect(self._buttons_policy)
        self.site_button.site_changed.connect(self._updateEnginesSetting)
        self.initFromSettings()
        self.setStyleSheet(StyleSheets.menu_style)
        self.pushButton_2.click()
        self.stackedWidget.setCurrentIndex(2)  # 首页面
        self.label.setPixmap(
            QPixmap(':/ico/search_1311349_easyicon.net.svg').scaled(
                QSize(*self.hello_size),
                transformMode=Qt.SmoothTransformation))

        for spider_cls in get_cached_spiders():
            self.filter_button.addSite(spider_cls.name, True,
                                       spider_cls._is_file)

        self.filter_button.site_changed.connect(self._fileterResults)

        self.listWidget.switch_sig.connect(lambda: self.pushButton_2.click())
        self.listWidget_2.switch_sig.connect(lambda: self.pushButton.click())
        self.clear_pushButton.setToolTip('<b>清空搜索记录</b>')
        self.site_button.clicked.connect(self.showPlugins)

        self.search_pushButton.clicked.connect(self.searchNovel)
        self.comboBox.currentIndexChanged.connect(self._filterDownStateResults)
        self.comboBox.setFixedHeight(self.site_button.height())
        self.load_subscribes()
        self.blockSignals(False)
        self.fresh_button.clicked.connect(self.freshSubscribes)
        self.fold_pushButton.setToolTip('<b>选择下载目录</b>')
        if self.listWidget_3.count() > 0:
            self.gotoSubmits()
        #     if self.internetOk():
        #         self.freshSubscribes()
        self.image_list_policy()
        # self.bkg_thread.add_task(updater.get_tpls_update,
        #                          callback=lambda res: self.titleMsgInfo(
        #                              '插件已更新, 请退出重启软件', True, Qt.darkRed)
        #                          if res else None)

    def showPlugins(self) -> None:  # 更新插件
        load_plugin()
        for spider_cls in get_cached_spiders():
            site_name = spider_cls.name
            self.site_button.addSite(
                site_name, True, spider_cls._is_file,
                lambda: self.clearHttpCachesBySite(site_name))
        self.site_button.showPopup()

    def clearLists(self) -> None:
        self.listWidget.clear()
        self.listWidget_2.clear()
        self.count_label.setText('已选择: 0')

    @pyqtSlot(bool, int)
    def _fileterResults(self, state: bool,
                        index: int) -> None:  # filter_button过滤函数
        self.clearLists()
        checked = self.filter_button.statesDict()
        for info in self.active_result:
            if checked[info.novel_site]:
                self.updateSearchMessage(info, add=False)
                QApplication.processEvents()

    @pyqtSlot(int)
    def _filterDownStateResults(self, index: int):
        self.clearLists()
        if index == 0:
            for info in self.active_result:
                self.updateSearchMessage(info, add=False)
                QApplication.processEvents()
        elif index == 1:
            for info in self.active_result:
                if info.novel_download:
                    self.updateSearchMessage(info, add=False)
                    QApplication.processEvents()
        elif index == 2:
            for info in self.active_result:
                if not info.novel_download:
                    self.updateSearchMessage(info, add=False)
                    QApplication.processEvents()

    @pyqtSlot()
    def _buttons_policy(self) -> None:
        if self.viewgroup.checkedButton() == self.pushButton:
            self.page_state = PageState.list_page
            self.stackedWidget.setCurrentIndex(0)
            self.stackedWidget_2.setCurrentIndex(0)
            self.filter_frame.show()
            self.fresh_frame.hide()
            self.count_label.show()
        elif self.viewgroup.checkedButton() == self.pushButton_2:
            self.page_state = PageState.img_page
            self.stackedWidget.setCurrentIndex(0)
            self.stackedWidget_2.setCurrentIndex(1)
            self.filter_frame.show()
            self.fresh_frame.hide()
            self.count_label.show()
        elif self.viewgroup.checkedButton() == self.subs_pushButton:
            self.page_state = PageState.subscribe_page
            self.stackedWidget.setCurrentIndex(0)
            self.stackedWidget_2.setCurrentIndex(2)
            self.filter_frame.hide()
            self.fresh_frame.show()
            self.count_label.hide()
            self.titleMsgInfo(f'已订阅: {self.listWidget_3.count()}本小说', True)

    def searchEngineStates(self) -> Tuple:
        dic = self.site_button.statesDict()
        eng_flag = True if len([value for key, value in dic.items()
                                if value]) >= 1 else False
        return dic, eng_flag

    @pyqtSlot(bool, int)
    def _updateEnginesSetting(self, state: bool, index: int) -> None:
        msg = self.site_button.getSiteName(index), state
        key = 'Engines/eng_%s' % msg[0]
        save_value = f'{msg[0]}*---*{state}'
        self.settings.setValue(key, save_value)

    @pyqtSlot()
    def searchNovel(self) -> None:
        if self.internetOk():
            if self.search_line.state in (0, 2):  # 防止再次搜素
                self.active_result.clear()
                search_content = self.search_line.text().strip()
                self.comboBox_2.appendTop(search_content)
                self.cachesWriteSettings()
                self.startSearch(search_content)
                self.count_label.setStyleSheet(
                    'color: transparent; text-decoration: underline')

    def clearHttpCaches(self) -> bool:
        http_dir = self.getCachesDir()
        if self.info_thread.isRunning() == False:
            self.bkg_thread.add_task(lambda: http_dir.removeRecursively(),
                                     callback=lambda res: self.bkg_thread.
                                     done_sig.emit('clearhttpcache', res))

    def startSearch(self, search_txt: str) -> None:
        self.search_line.state = 1  # 搜索中
        cahce_dir = self.getCachesDir().absolutePath()
        images_dir = self.getImagesDir().absolutePath()

        qfile = QFile(self.getLogFilInfo().absoluteFilePath())
        qfile.remove()

        if not self.programDirs().exists(self.caches):
            self.programDirs().mkdir(self.caches)
        if not self.programDirs().exists(self.image_caches):
            self.programDirs().mkdir(self.image_caches)

        settings = get_project_settings().copy()
        if self._parent.search_mode == '极速模式':
            settings.set('HTTPCACHE_ENABLED', True)
        else:
            settings.set('HTTPCACHE_ENABLED', False)
        settings.set('HTTPCACHE_DIR', cahce_dir)
        settings.set('app_images_caches', images_dir)
        settings.set('app_log_file', self.getLogFilInfo().absoluteFilePath())
        states, flag = self.searchEngineStates()

        if search_txt and flag:
            self.search_log.addLog(search_txt)
            self.pop_dialog.addSearchRecord(search_txt, first=True)
            self.pop_dialog.textBrowser.clearAllLines()
            self.listWidget.clear()
            self.listWidget_2.clear()
            self.info_thread.start()
            start_log = True if self.pop_dialog.is_debug else False
            startBothByOrder(search_txt,
                             self.process_queue,
                             self.getSavePath(),
                             states,
                             settings,
                             start_log=start_log,
                             call_handler=self._scrapyLogHandler)  # 开启进程
            self.stackedWidget.setCurrentIndex(1)  # 搜索动画页面
            self.label_4.setText(
                f'<font color="#102b6a">`{search_txt}`</font>查找中')
            self.search_movie.start()
        if flag == False:
            QMessageBox.warning(self._parent, '提醒', '请选择搜索引擎')
            # self.search_line.blockSignals(False)

    def image_list_policy(self):
        if self.getResultsCount() == 0:
            self.pushButton.hide()
            self.pushButton_2.hide()
            self.subs_pushButton.show()
        else:
            self.pushButton.show()
            self.pushButton_2.show()
            self.subs_pushButton.show()

    def gotoHello(self) -> None:
        self.stackedWidget.setCurrentIndex(2)
        self.image_list_policy()

    def gotoImgPage(self, animation=True) -> None:
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_2.setCurrentIndex(1, animation)
        self.pushButton_2.click()
        self.filter_frame.show()
        self.fresh_frame.hide()

    def gotoSubmits(self):
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_2.setCurrentIndex(2)
        self.subs_pushButton.click()
        self.filter_frame.hide()
        self.fresh_frame.show()
        self.titleMsgInfo(f'已订阅: {self.listWidget_3.count()}本小说', True)
        self.image_list_policy()

    def gotoListPage(self) -> None:
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_2.setCurrentIndex(0)
        self.pushButton.click()

    def cachesWriteSettings(self) -> None:
        self.settings.remove('Search')
        size = self.comboBox_2.count()
        self.settings.beginWriteArray('Search', size)
        for i in range(1, size + 1):
            self.settings.setValue('s_%s' % i, self.comboBox_2.itemText(i - 1))
        self.settings.endArray()

    @pyqtSlot()
    def clearSearchRecords(self) -> None:
        self.settings.remove('Search')
        self.comboBox_2.clear()
        self.search_line.clear()
        self.search_line.clearHistories()
        self.titleMsgInfo('搜索记录已删除', True)

    def _saveSettings(self) -> None:
        self.settings.setValue('Settings/savepath', self.getSavePath())

    def getSavePath(self) -> str:
        return self.label_3.text()

    def setSavePath(self, value: str) -> None:
        self.label_3.setText(value)

    def chooseSavePath(self) -> None:
        path = QFileDialog.getExistingDirectory(self, '保存目录',
                                                self.getSavePath())
        if path:
            self.label_3.setText(path)
            self.pop_dialog.label_4.setText(path)
            self.settings.setValue('Settings/savepath', path)
            for search in self.listWidget.itemWidgets():
                search.setSavePath(path)

    def _initFromSpider(self, spider: BasicFileSpider) -> None:
        keyname = f'Engines/eng_{spider.name}'
        if keyname not in self.settings.allKeys():
            save_value = f'{spider.name}*---*{True}'
            self.settings.setValue(f'Engines/eng_{spider.name}', save_value)
            name = spider.name
            state = True
        else:
            name, state = self.settings.value(keyname).split('*---*')
            state = True if state == 'True' else False
        self.site_button.addSite(name, state, spider._is_file,
                                 lambda: self.clearHttpCachesBySite(name))
        self.filter_button.addSite(name, state, spider._is_file)

    def _initSearchCachesAndPath(self) -> None:
        size = self.settings.beginReadArray('Search')
        search_caches = []
        for i in range(1, size + 1):
            search_caches.append(self.settings.value('s_%s' % i))
        self.settings.endArray()
        self.comboBox_2.extendLogs(search_caches)

        dft = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        savepath = self.settings.value('Settings/savepath', defaultValue=dft)
        qdir = QDir(savepath)
        if qdir.exists() == False:
            qdir.mkdir(savepath)
        self.setSavePath(savepath)

    @lasyproperty
    def settings(self) -> QSettings:
        config_file = self.getConfigFileInfo().absoluteFilePath()
        log_file = self.getLogFilInfo().absoluteFilePath()
        settings = QSettings(config_file, QSettings.IniFormat)
        settings.setIniCodec('UTF-8')
        return settings

    @property
    def search_cache_size(self) -> int:  # 搜索缓存
        return self.settings.value('Settings/search_size', 0, type=int)

    @search_cache_size.setter
    def search_cache_size(self, value: int) -> None:
        size = self.size_hum_read(value)
        self.pop_dialog.label_16.setText(size)
        self.settings.setValue('Settings/search_size', value)

    @property
    def image_cache_size(self) -> int:  # 图片缓存
        return self.settings.value('Settings/image_size', 0, type=int)

    @image_cache_size.setter
    def image_cache_size(self, value: int) -> None:
        size = self.size_hum_read(value)
        self.pop_dialog.label_18.setText(size)
        self.settings.setValue('Settings/image_size', value)

    def _titleHeight(self) -> int:
        height = self.settings.value('Settings/titleheight', None)
        return int(height) if height else self._parent.titleBar.height()

    def _novelScaled(self) -> float:
        scaled = self.settings.value('Settings/novelscaled', None)
        return float(scaled) if scaled else IconWidget.scaled

    def initFromSettings(self) -> None:
        self.blockSignals(True)
        log_file = self.getLogFilInfo().absoluteFilePath()
        for spider_cls in get_cached_spiders():
            self._initFromSpider(spider_cls)
        self._initSearchCachesAndPath()
        self.settings.setValue('Logs/log_file', log_file)
        values = self.comboBox_2.searchLogs()
        self.search_line.setHistories(values)
        flag = self.settings.value('Settings/infomode', False, bool)
        self.main_gui.tip_button.setChecked(flag)
        setIconsToolTip(flag)
        self.blockSignals(False)

    def openSettings(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.settings.fileName()))

    def openLogFile(self) -> None:
        QDesktopServices.openUrl(
            QUrl.fromLocalFile(self.getLogFilInfo().absoluteFilePath()))

    def resetSettings(self) -> None:  # 重置设置
        searchs = self.comboBox_2.searchLogs()

        img_size = self.image_cache_size
        http_size = self.search_cache_size

        config_file = self.getConfigFileInfo().absoluteFilePath()
        self.settings = QSettings(config_file, QSettings.IniFormat)
        self.settings.setIniCodec('UTF-8')  # 中文读写支持
        self.settings.clear()
        self.settings.setValue('Logs/log_file',
                               self.getLogFilInfo().absoluteFilePath())
        self.site_button.selectAll()

        for spider_cls in get_cached_spiders():
            self._initFromSpider(spider_cls)
        self._initSearchCachesAndPath()
        flag = self.settings.value('Settings/infomode', False, bool)
        self.main_gui.tip_button.setChecked(flag)
        self.image_cache_size = img_size
        self.search_cache_size = http_size
        setIconsToolTip(flag)

    @pyqtSlot(int)
    def selectAllPolicy(self, checked: int) -> None:
        if self.page_state != PageState.subscribe_page:
            i = 0
            for search, icon_widget in zip(self.listWidget.itemWidgets(),
                                           self.listWidget_2.itemWidgets()):
                i += 1
                if checked == Qt.Checked:
                    search.select()
                    icon_widget.select()
                elif checked == Qt.Unchecked:
                    search.cancelSelect()
                    icon_widget.cancelSelect()
            else:
                if checked == Qt.Checked:
                    self.count_label.setStyleSheet(
                        'color: #CD5C5C;text-decoration:underline')
                    self.count_label.setText(f'已选择: {i}')
                else:
                    self.count_label.setStyleSheet(
                        'color: transparent;text-decoration:underline')
                    self.count_label.setText('已选择: 0')

    @pyqtSlot(int)
    def _iconselect(self, checked: int) -> None:
        self.count_label.setStyleSheet(
            'color: #CD5C5C;text-decoration:underline')
        if checked == Qt.Checked:
            count = int(self.count_label.text().strip('已选择: ')) + 1
        elif checked == Qt.Unchecked:
            count = int(self.count_label.text().strip('已选择: ')) - 1
        self.count_label.setText(f'已选择: {count}')

    def _downSchedule(self) -> None:
        self.img_pool = QThreadPool()
        # self.down_q = Queue()  # 下载任务队列
        self.image_q = Queue()  # 图片监视队列
        self.image_control = ImageController(self.image_q, self.img_pool,
                                             25)  # 图片线程池
        self.image_control.schedule()  # 启动图片线程池

    def processSearchIconFlags(self, inf: InfoObj) -> None:
        search = inf.novel_app.getSearchWidget(inf.novel_index - 1)
        icon = inf.novel_app.getIconWidget(inf.novel_index - 1)
        task_widget = self.getCurrentTaskWidget()
        if inf.novel_status == DownStatus.down_fail:  # '下载失败':
            msg = inf.novel_name + f'[{inf.novel_site}]下载失败'
            search._downFailFlag()
            icon._downFailFlag()
            if task_widget:
                task_widget._downFailFlag()
            self.titleMsgInfo(msg)
        elif inf.novel_status == DownStatus.down_ok:  # '已下载':
            msg = inf.novel_name + f'[{inf.novel_site}]已下载'
            search._downOkFlag()
            icon._downOkFlag()
            self.addDownRecord(inf, first=True)
            if task_widget:
                task_widget._downOkFlag()
            self.titleMsgInfo(msg)
        elif inf.novel_status == DownStatus.down_ing:  # '下载中':
            search._downIngFlag()
            icon._downIngFlag()
            if task_widget:
                task_widget._downIngFlag()
        elif inf.novel_status == DownStatus.down_before:  # '未处理':
            search._downBeforeFlag()
            icon._downBeforeFlag()
            if task_widget:
                task_widget._downBeforeFlag()

    def _addSearchInfo(self, index: int, info: InfoObj) -> None:
        info.novel_app = self  # 重要
        info.novel_index = index + 1  # 重要

        widget1 = SearchInfoWidget(info)
        item_height = widget1.fontMetrics().height() * 2.5
        widget1.introutced_signal.connect(self.gotoIntroutced)
        self.listWidget.addItemWidget(QSize(10, item_height), widget1)

        widget2 = IconWidget(info, self.listWidget_2, self.image_q)
        if info._is_file == False and info.novel_chapter_urls:
            if info.novel_subs_url in self.subscribe_urls:
                widget2.addSubscribeState()
                widget1.addSubscribeState()
        widget2.clicked_signal.connect(self._bindFocus)
        widget2.introutced_signal.connect(self.gotoIntroutced)
        widget2.down_signal.connect(lambda inf: widget1.downLoad())
        widget2.checkbox.stateChanged.connect(self._iconselect)
        widget2.subscribe_signal.connect(self.subscribePolicy)
        self.listWidget_2.addIconWidget(widget2)

        widget1.checkBox.stateChanged.connect(widget2._selectBy)
        widget2.checkbox.stateChanged.connect(widget1._selectBy)

    @pyqtSlot(InfoObj, bool)
    def subscribePolicy(self, info: InfoObj, flag: bool) -> None:
        if flag == True:
            self._addSubsInfo(info)
        else:
            self._removeSubsInfo(info)

    def load_subscribes(self) -> None:
        temp_infos = self.load_subscribe_infos()
        for info in temp_infos:
            info.novel_subs_state = False
            info.novel_app = self
            info.novel_index = info.novel_subs_index + 1
            info.novel_meta['submit_widget'] = True
            self._addSubsInfo(info, False)

    def subscribeCount(self) -> int:
        return self.listWidget_3.count()

    def setSubscribeSlots(self) -> None:
        self.subscribe_obj = get_subscribeLinkobj()
        self.subscribe_obj.update_info_signal.connect(
            self.updateSubscribeByInfo)
        self.subscribe_obj.fail_info_signal.connect(self.failUpdateByInfo)
        self.subscribe_obj.fresh_down_signal.connect(
            lambda: self.fresh_button.setIcon(
                QIcon(':/ico/refresh_173px_1188146_easyicon.net.png')))

    def _addSubsInfo(self, info: InfoObj, dump_info: bool = True) -> bool:
        def subscribe_msg(subwidget, inf):
            flag = f' -- <b><font color="black">{subwidget.clicked_msg}</font></b>' if subwidget.clicked_msg else ''
            msg = f'<b>{inf.novel_site}</b>: {inf.novel_name}-{inf.novel_size} {flag}'
            self.titleMsgInfo(msg)

        if info.novel_subs_url and (info._is_file
                                    == False) and (info.novel_subs_state
                                                   == False):
            if info.novel_subs_url not in self.subscribe_urls:
                count = self.listWidget_3.count()
                new_info = info.copy()
                new_info.novel_app = self
                new_info.novel_subs_state = True
                new_info.novel_subs_index = count
                new_info.novel_index = count + 1
                new_info.novel_temp_data['root_index'] = info.novel_index
                subscribe_widget = SubscribeWidget(new_info, self.listWidget_3)
                subscribe_widget.clicked_signal.connect(
                    lambda inf: subscribe_msg(subscribe_widget, inf))
                subscribe_widget.introutced_signal.connect(self.gotoIntroutced)
                subscribe_widget.subscribe_signal.connect(self.subscribePolicy)
                self.subscribe_urls.add(new_info.novel_subs_url)
                self.listWidget_3.addSubscribeWidget(subscribe_widget)
                if self.page_state != PageState.subscribe_page and self.getResultsCount(
                ) > 0:
                    icon_widget = self.getIconWidget(info.novel_index - 1)
                    search_widget = self.getSearchWidget(info.novel_index - 1)
                    if icon_widget:
                        icon_widget.img_label.setSubscribeState(True)
                        search_widget.addSubscribeState()
                if dump_info:
                    new_info.dump_subscribe()
                return True
            return False
        return False

    def freshSubscribes(self) -> None:
        if self.internetOk():
            if self.listWidget_3.count() > 0:
                self.fresh_button.setGif(':/gif/5-121204194113-50.gif')
                infos = self.updatedSubmitInfos()
                self.subscribe_obj.updateSubscribeLinks(infos)

    @pyqtSlot(InfoObj)
    def failUpdateByInfo(self, info: InfoObj) -> None:
        subscribe_widget = self.getSubscribeWidget(info.novel_subs_index)
        subscribe_widget.setSubscirbeLinkState(SubState.update_fail)
        self.titleMsgInfo(f'{info.novel_name}--更新失败', True, color='darkgreen')

    @pyqtSlot(InfoObj)
    def updateSubscribeByInfo(self, info: InfoObj) -> None:
        subscribe_widget = self.getSubscribeWidget(info.novel_subs_index)
        if info.chapter_count() != subscribe_widget.info.chapter_count():
            subscribe_widget.setSubscirbeLinkState(SubState.update_latest)
            self.titleMsgInfo(
                f'{info.novel_name}--已更新: {info.latest_chapter()}',
                True,
                color='darkgreen')
        else:
            if info.novel_fresh_state != 3:
                subscribe_widget.setSubscirbeLinkState(SubState.update_no)
                self.titleMsgInfo(f'{info.novel_name}--无更新内容',
                                  True,
                                  color='darkgreen')
            else:
                subscribe_widget.setSubscirbeLinkState(SubState.update_fail)
        subscribe_widget.info = info
        task_widget = self.getCurrentTaskWidget()
        if task_widget:
            if info == task_widget.info:
                task_widget.info = info
                task_widget.updateSubmitPage(info)

    def _removeSubsInfo(self, info: InfoObj) -> bool:
        if info.novel_subs_url in self.subscribe_urls:
            info.novel_subs_state = False
            remove_flag = False
            if self.listWidget_3.removeSubscribeWidgetByInfo(info):
                self.subscribe_urls.remove(info.novel_subs_url)
                info.remove_subscribe()
                root_index = info.novel_temp_data.get('root_index')
                if root_index is not None:
                    icon_widget = self.getIconWidget(root_index - 1)
                    search_widget = self.getSearchWidget(root_index - 1)
                    if icon_widget:
                        icon_info = icon_widget.inf
                        if icon_info == info:  # 从临时数据中查找
                            icon_widget.removeSubscribeState()
                            search_widget.removeSubscribeState()
                            remove_flag = True
                        if remove_flag == False:  # 从缓存中查找
                            for index, inf in enumerate(self.active_result):
                                if inf == info:
                                    search = self.getSearchWidget(index)
                                    if search:
                                        if search.info == info:
                                            icon = self.getIconWidget(index)
                                            icon.removeSubscribeState()
                                            search.removeSubscribeState()
                                            remove_flag = True
                                            break
                        if remove_flag == False:  # 从列表视图中查找
                            for i in range(self.getResultsCount()):
                                search = self.getSearchWidget(i)
                                inf = search.info
                                if inf == info:
                                    icon_widget = self.getIconWidget(i)
                                    icon_widget.removeSubscribeState()
                                    search.removeSubscribeState()
                                    remove_flag = True
                return True
        return False

    @pyqtSlot(InfoObj)
    def _bindFocus(self, inf: InfoObj) -> None:
        self.titleMsgInfo(
            f'<b>{inf.novel_site}</b>: {inf.novel_name}-{inf.novel_size}')
        self.getSearchWidget(inf.novel_index - 1).setFocus(True)

    @pyqtSlot(int)
    def getIconWidget(self, index: int) -> IconWidget:
        return self.listWidget_2.getItemWidget(index)

    @pyqtSlot(int)
    def getSubscribeWidget(self, index: int) -> SubscribeWidget:
        return self.listWidget_3.getItemWidget(index)

    @pyqtSlot(int)
    def getSearchWidget(self, index: int) -> SearchInfoWidget:
        return self.listWidget.getItemWidget(index)

    def getResultsCount(self) -> int:  # 返回搜索结果数量
        return self.listWidget.count()

    def beforePageToTaskWidget(self) -> int:
        # 0 listpage, 1 img_page, 2 subscribe_page 3 home_page
        return self.page_state

    @pyqtSlot(InfoObj)  # 更新搜索结果
    def updateSearchMessage(self, info: InfoObj, *, add: bool = True) -> None:
        if add:
            self.active_result.append(info)
        count = self.listWidget.count()
        self._addSearchInfo(count, info)
        message_txt = info.novel_site + \
            f'查找到:<font color="#4f5555" bold="true">{info.novel_name}</font>'
        self.message_label.setText(message_txt)

    @property
    def search_count(self) -> int:
        return self.listWidget_2.count()

    def isInSubmitPage(self) -> bool:
        flag = self.filter_frame.isHidden()
        return flag

    @pyqtSlot()
    def _switch(self) -> None:  # 搜索完毕返回搜索结果页面
        self.search_line.state = 2
        self.message_label.setText('')
        self.search_movie.stop()
        self.stackedWidget.setCurrentIndex(0)
        self.listWidget_2.verticalScrollBar().setSliderPosition(0)
        self.listWidget_2.crawlImagesFlagsReset()
        if self.getResultsCount() > 0:
            self.listWidget_2.refreshNovelImages()
        self.titleMsgInfo(
            f'当前搜索模式: {self._parent.search_mode}; 共查找到: {self.search_count}本相关小说'
        )
        if self.isInSubmitPage():
            self.gotoImgPage(False)
        if self.search_count == 0:
            self.gotoHello()
            self._setNotFound()
        else:
            self._helloReset()
        self.computeImagesCacheSize()
        self.computeSearchCacheSize()
        self.image_list_policy()

    @pyqtSlot(str)
    def updateScrapyLogs(self, message: str) -> None:
        QApplication.processEvents()
        self.pop_dialog.updateScrapyMessage(message)

    def getCurrentTaskWidget(self) -> TaskWidget:
        return self.infs_widget

    def isInTaskWidget(self) -> bool:
        return self.stackedWidget.count() == 4

    @property
    def cust_font(self) -> QFont:
        return QFont(self._parent.font_family, 12)

    @property
    def cust_familys(self) -> List[str]:
        return self._parent.font_familys

    @pyqtSlot(InfoObj)
    def gotoIntroutced(self, inf: InfoObj) -> None:  # 进入详情页面
        if self.isInTaskWidget():
            self.closeIntroutced()  # 先关闭旧页面
        inf.novel_app = self  # 传递参数
        self.infs_widget = TaskWidget(inf)
        if inf.novel_meta.get('submit_widget', False) == False:
            self.infs_widget.autoProcessFlags()

        self.infs_widget.showFullMessage(inf)
        self.stackedWidget.addWidget(self.infs_widget)
        self.stackedWidget.setCurrentIndex(3)
        self.setSearchBarVisable(False)

        self.infs_widget.remove_signal.connect(self.closeIntroutced)
        self.infs_widget.down_signal.connect(self.taskWidgetDownLoadStart)

        if self.infs_widget._isSubmitWidget():
            self.infs_widget._setUpdateTitleMsg(inf.novel_fresh_state)
        if self.page_state != PageState.subscribe_page:
            self.infs_widget.fresh_button.hide()

    def showChapters(self) -> None:
        self._parent.showSelected(self.infs_widget._inf)

    @pyqtSlot()
    def closeIntroutced(self) -> None:  # 推出详情页面
        task_widget = self.stackedWidget.widget(3)
        flag = task_widget.info.novel_subs_state
        if flag:
            subscribe_widget = self.getSubscribeWidget(
                task_widget.info.novel_subs_index)
            # subscribe_widget.haslatestChapterState(False)
            subscribe_widget.setSubscirbeLinkState(SubState.update_no)
        self.stackedWidget.removeWidget(task_widget)
        task_widget.close()
        task_widget.deleteLater()
        self.infs_widget = None
        self.stackedWidget.setCurrentIndex(0)
        self.setSearchBarVisable(True)

    @pyqtSlot(InfoObj)
    def taskWidgetDownLoadStart(self,
                                inf: InfoObj) -> None:  # taskwidget 下载开启函数
        if not inf.novel_subs_state:
            search = self.getSearchWidget(inf.novel_index - 1)
            search.downLoad()
        else:
            subscribe_widget = self.getSubscribeWidget(inf.novel_subs_index)
            subscribe_widget.subscribeDownload()

    def closeEvent(self, closeEvent) -> None:
        self.beforeClose()
        super().closeEvent(closeEvent)

    def beforeClose(self) -> None:
        self.stopAll()
        self.bkg_thread.stop()
        self._saveSettings()
        self.search_log.dump()
        if self.infs_widget:
            self.infs_widget.save_read_infos()

    def stopAll(self) -> None:  # 停止所有的下载任务
        for search in self.listWidget.itemWidgets():
            search.cancelDownload()

    def stopTask(self, task_index: int) -> None:  # 停止下载某一任务
        search = self.listWidget.getItemWidget(task_index)
        search.cancelDownload()

    @pyqtSlot()  # 开启下载所有任务
    def downAll(self) -> None:
        if self.page_state != PageState.subscribe_page:
            for search in self.listWidget.itemWidgets():
                if search.checkBox.isChecked():
                    search.downLoad()

    @pyqtSlot(InfoObj, bool)
    def addDownRecord(self, inf: InfoObj, first=False) -> None:
        self.pop_dialog.addDownRecord(inf, first)
        search_info = self.getSearchWidget(inf.novel_index - 1)

    def addSearchRecord(self) -> None:
        pass

    @pyqtSlot(InfoObj)
    def prepareRestartDownLoad(self, inf: InfoObj) -> None:
        if inf.novel_subs_state == False:
            search_info = self.getSearchWidget(inf.novel_index - 1)
            search_info.novel_name.setFont(QFont('微软雅黑', 9))
            search_info.novel_name.setStyleSheet('background: transparent')
            icon = self.getIconWidget(inf.novel_index - 1)
            icon._downCancelFlag()