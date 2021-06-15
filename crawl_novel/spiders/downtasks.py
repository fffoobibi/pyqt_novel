import asyncio
import weakref
import re
import httpx
import requests
import os
import time
import traceback
import logging

from random import random
from datetime import datetime
from urllib.parse import urlparse
from contextlib import suppress
from typing import Iterable, List, Optional, Type
from PIL import Image
from requests.exceptions import RequestException

from PyQt5.QtCore import QRunnable, QDir, QMetaObject, Qt, QFile, QFileInfo, QSemaphore, QThread, QObject, pyqtSignal
from PyQt5.Qt import Q_ARG

from .infoobj import InfoObj, DownStatus

__all__ = ('register', 'get_handle_cls', 'ChapterDownloader', 'FileDownloader')

__handler_caches = weakref.WeakValueDictionary()


class Handler():

    use_plugin: bool = True  # 为True时使用插件, 默认不使用

    name: str = 'BasicChapterHanlder'  # 必须定义:唯一名称,和BasicFileSpider子类名称相同

    header: dict = {}

    def __init_subclass__(cls, type: str = '', **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if type.startswith('c'):
            if not isinstance(cls.chapter_headers_hook, classmethod):
                cls.chapter_headers_hook = classmethod(
                    cls.chapter_headers_hook)
            if not isinstance(cls.parse_charpter, classmethod):
                cls.parse_charpter = classmethod(cls.parse_charpter)
        elif type.startswith('f'):
            if not isinstance(cls.file_headers_hook, classmethod):
                cls.file_headers_hook = classmethod(cls.file_headers_hook)
            if not isinstance(cls.save_path_hook, classmethod):
                cls.save_path_hook = classmethod(cls.save_path_hook)

    def chapter_headers_hook(cls, url_index: int, url: int, inf: InfoObj):
        return cls.header

    def parse_charpter(cls, url_index: int, response: 'httpx.Response',
                       chapter: str):
        raise NotImplementedError

    def file_headers_hook(cls, inf: InfoObj) -> dict:
        return cls.header

    def save_path_hook(cls, response, inf: InfoObj) -> str:
        raise NotImplementedError


def register(cls: Type[Handler]):
    if getattr(cls, 'use_plugin', False):
        __handler_caches[cls.name] = cls
    return cls


def get_handle_cls(novel_site: str) -> Type[Handler]:
    return __handler_caches.get(novel_site)


class BasicFileHandler(Handler):
    def __init_subclass__(cls, type='f', **kwargs) -> None:
        return super().__init_subclass__(type=type, **kwargs)

    def file_headers_hook(cls, inf: InfoObj) -> dict:
        return cls.header

    def save_path_hook(cls, response, inf: InfoObj) -> str:
        qdir = QDir(inf.novel_save_path)
        save_path = qdir.absoluteFilePath(inf.novel_name +
                                          f'[{inf.novel_site}].' +
                                          inf.novel_file_type) + '.download'
        return save_path


class BasicChapterHandler(Handler):
    def __init_subclass__(cls, type='c', **kwargs) -> None:
        return super().__init_subclass__(type=type, **kwargs)

    def chapter_headers_hook(cls, url_index: int, url: int, inf: InfoObj):
        return cls.header

    def parse_charpter(cls, url_index: int, response: 'httpx.Response',
                       chapter: str):
        raise NotImplementedError


class BasicDownloader(QObject):

    flag_signal = pyqtSignal(InfoObj)

    update_signal = pyqtSignal(InfoObj)

    def __iter__(self):
        yield from self.info.novel_temp_data.get('log_msgs', [])

    def __len__(self):
        return len(self.info.novel_temp_data['log_msgs'])

    def __enter__(self):
        self.thread_seam.acquire()

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.thread_seam.release()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<{self.info.novel_name}-{self.info.novel_site}>'

    def __init__(self, thread_seam: QSemaphore, info: InfoObj):
        super().__init__()
        self.thread_seam = thread_seam
        self.info = info
        self.log_msgs = []
        self.down_status = 0  # 0 未开始,1进行中,2结束
        self.down_thread = self._create_downthread()  # QThread

    def download(self, info: InfoObj):
        if self.down_status in (0, 2):
            self.log_msgs.clear()
            if self.down_thread.isFinished():  # asyncio支持
                self.down_thread.start()
            self._start_download(info)

    def quit_download(self):
        return NotImplemented

    def _create_downthread(self) -> QThread:
        raise NotImplementedError

    def _start_download(self, info):
        return NotImplemented

    def _size_hum_read(self, value: int) -> str:
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = 1024.0
        for i in range(len(units)):
            if (value / size) < 1:
                return "%.2f%s" % (value, units[i])
            value = value / size

    def interval(self):
        return random() / 10

    def msg_time(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


class FileDownloader(BasicDownloader):
    def __init__(self, thread_seam: QSemaphore, info: InfoObj):
        super().__init__(thread_seam, info)

    def _create_downthread(self):
        info = self.info
        site = info.novel_site
        return BasicFileDownTask(info, self)

    def _start_download(self, info):
        self.down_thread.start()


class ChapterDownloader(BasicDownloader):

    name: str = 'ChapterDownloader'

    use_plugin: bool = False

    header: dict = {}

    indent: int = 4

    debug_signal = pyqtSignal(str, int)

    nourls_signal = pyqtSignal(InfoObj)

    single_signal = pyqtSignal(dict)

    single_fail_signal = pyqtSignal(dict)

    def __init__(self, thread_seam: QSemaphore, inf: InfoObj, loop: asyncio.AbstractEventLoop):
        self.asyc_loop = loop  # 事件循环
        self.asyn_sem = asyncio.Semaphore(30, loop=self.asyc_loop)  # 控制协程并发量
        self.results = []  # [(content, chapter_name, url_index), ...]
        super().__init__(thread_seam, inf)
        self.down_thread.start()
        self.pre_count = 50  # 预下载数量
        self.read_pools = set()  # 任务池,排除同时下载

    def _create_downthread(self) -> QThread:
        return _AsyncThread(self, self.asyc_loop)

    def _start_download(self, inf: InfoObj) -> None:
        asyncio.run_coroutine_threadsafe(self._download(inf), self.asyc_loop)

    def quit_download(self) -> None:
        self.asyc_loop.stop()

    def _updateInf(self, inf: InfoObj) -> None:
        inf.novel_flag = True  # download下载标志位
        inf.novel_start_time = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')  # 下载创建时间
        inf.novel_status = DownStatus.down_ing  # '下载中'
        inf.novel_file_size = f'共{len(inf.novel_chapter_urls)}章'
        inf.novel_averge_speed = '--'
        inf.novel_size = f'共{len(inf.novel_chapter_urls)}章'
        self.update_signal.emit(inf)

    def _dynamicUpdateInf(self, i: int, total: int, chapter_name: str,
                          url_index: int, inf: InfoObj) -> None:
        inf.novel_meta['down_size'] = f'已下载:{i}章/共{total}章'
        inf.novel_percent = (i / total) * 100
        inf.novel_url = '--'
        inf.novel_file_type = 'txt'
        self.update_signal.emit(inf)

    def _finalUpdateInf(self, inf: InfoObj) -> None:
        inf.novel_flag = True
        inf.novel_down_cancel = True
        inf.novel_download = True
        inf.novel_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        inf.novel_percent = 100
        inf.novel_status = DownStatus.down_ok  # '已下载'
        inf.novel_url = '--'
        inf.novel_file_type = 'txt'
        self.update_signal.emit(inf)
        self.flag_signal.emit(inf)

    def _downFailUpdateInf(self, inf: InfoObj) -> None:
        inf.novel_flag = True
        inf.novel_down_cancel = True
        inf.novel_download = True
        inf.novel_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        inf.novel_percent = 0
        inf.novel_status = DownStatus.down_fail  # '下载失败'
        inf.novel_url = '--'
        inf.novel_file_type = 'txt'
        self.down_status = 2
        msg = f'{inf.novel_name}[{inf.novel_site}] -- 下载失败'
        self.log_msgs.append((msg, logging.ERROR, self.msg_time()))
        self.update_signal.emit(inf)
        self.flag_signal.emit(inf)

    def _merge_chapter(self, inf: InfoObj, count: int) -> None:
        if count == 0:
            self._downFailUpdateInf(inf)
        else:
            self.results.sort(key=lambda e: e[-1])
            save_path = inf.novel_app.getSavePath()
            save_path = os.path.join(
                save_path, inf.novel_name + f'[{inf.novel_site}].txt')
            with open(save_path, 'w', encoding='utf8') as file:
                file.write(inf.novel_introutced + '\n')
                j = 0
                for content, chapter_name, index in self.results:
                    j += 1
                    title = chapter_name + '\n'
                    file.write(title)
                    msg = f'合并中: {chapter_name}'
                    self.log_msgs.append((f'合并中 -- {chapter_name}',
                                          logging.INFO, self.msg_time()))
                    for line in content:
                        write_line = ' ' * self.indent + line + '\n'
                        file.write(write_line)
            file_size = self._size_hum_read(os.path.getsize(save_path))
            inf.novel_file_size = file_size
            msg = f'{inf.novel_name}[{inf.novel_site}].txt -- 已保存:{file_size},共{j}章'
            self.log_msgs.append((msg, logging.INFO, self.msg_time()))
            self.results.clear()
            self._finalUpdateInf(inf)
            inf.dump()
            self.down_status = 2

    async def _download(self, inf: InfoObj) -> None:
        total = len(inf.novel_chapter_urls)
        read_dir = inf.novel_app.getReadCachesDir()
        exists_chapters = self.exits_chapters(read_dir, inf)
        async with httpx.AsyncClient() as client:
            tasks = []
            handler = get_handle_cls(inf.novel_site)
            for url_index, tupled in enumerate(inf.novel_chapter_urls, 0):
                url, chapter_name, select_state = tupled
                if select_state:
                    header = handler.chapter_headers_hook(url_index, url, inf)
                    task = asyncio.create_task(
                        self._down_chapter(url_index, url, chapter_name,
                                           header, client, inf,
                                           exists_chapters, read_dir))
                    tasks.append(task)
            if tasks:
                i = 0
                self.down_status = 1
                self._updateInf(inf)
                msg = f'{inf.novel_name}[{inf.novel_site}] -- 开始抓取'
                self.log_msgs.append((msg, logging.INFO, self.msg_time()))
                for future in asyncio.as_completed(tasks):
                    try:
                        content, chapter_name, url_index, url = await future
                        i += 1
                        msg = f'已抓取: {url} {chapter_name} '
                        self.log_msgs.append(
                            (f'已抓取 -- {chapter_name} {url}', logging.INFO,
                             self.msg_time()))
                        self.results.append((content, chapter_name, url_index))
                        self._dynamicUpdateInf(i, total, chapter_name,
                                               url_index, inf)
                    except (httpx.HTTPStatusError, httpx.HTTPError,
                            httpx.InvalidURL, httpx.StreamError) as e:
                        self.log_msgs.append(
                            (f'抓取失败 -- {e.chapter_name} {e.chapter_url} {e}',
                             logging.ERROR, self.msg_time()))
                    except Exception as e:
                        self.log_msgs.append(
                            (f'解析失败 -- {e}', logging.ERROR, self.msg_time()))
                else:
                    self._merge_chapter(inf, i)
            else:
                msg = f'{inf.novel_name}[{inf.novel_site}] -- 下载失败'
                self.log_msgs.append((msg, logging.INFO, self.msg_time()))
                self.nourls_signal.emit(inf)
        inf.novel_temp_data['log_msgs'] = self.log_msgs.copy()
        self.log_msgs.clear()
        self.quit_download()

    async def _down_chapter(self,
                            url_index: int,
                            url: str,
                            chaper_name: str,
                            header: dict,
                            client: httpx.AsyncClient,
                            info: InfoObj,
                            exists_chapter: List[int] = None,
                            read_dir: QDir = None) -> Optional[tuple]:
        task_info = info.getTaskInfo(url_index)
        handler = get_handle_cls(info.novel_site)
        if read_dir is not None:  # 优先从缓存中获取
            if url_index in exists_chapter:
                message = self._get_message_from_caches(
                    url_index, read_dir, info)
                content = message['content']
                chapter = message['chapter'] if message[
                    'chapter'] else chaper_name
                return content, chapter, url_index, url
        try:
            async with self.asyn_sem:
                await asyncio.sleep(self.interval())
                resp = await client.get(url, headers=header)
                resp.raise_for_status()
                content, chapter_name = handler.parse_charpter(
                    url_index, resp, chaper_name)
                return content, chapter_name, url_index, url
        # except (httpx.HTTPStatusError, httpx.HTTPError, httpx.InvalidURL, httpx.StreamError) as e:
        except Exception as e:
            e.task_info = task_info
            e.url_index = url_index
            e.chapter_url = url
            e.chapter_name = chaper_name
            raise e

    def readChapter(self, url_index: int, chaper_name: str,
                    info: InfoObj) -> None:  # 在线阅读请求
        novel_app = info.novel_app
        read_dir = novel_app.getReadCachesDir()
        task_info = info.getTaskInfo(url_index)
        if task_info not in self.read_pools:  # 排除重复请求
            if self.chapter_exists(url_index, read_dir, info):  # 已缓存
                res = self._get_message_from_caches(url_index, read_dir, info)
                self.single_signal.emit(res)
                pre_heat_cor = None
                if (url_index + 1 <= self.pre_count):  # 0,1,2,3, 4
                    pre_heat_cor = self._run_pre_heat(url_index + 1, read_dir,
                                                      info)
                elif ((url_index + 1) % self.pre_count == self.pre_count -
                      1) and (url_index + 1 > self.pre_count):
                    pre_heat_cor = self._run_pre_heat(url_index + 1, read_dir,
                                                      info)
                if pre_heat_cor:
                    if self.down_thread.isFinished():
                        self.down_thread.start()
                    asyncio.run_coroutine_threadsafe(pre_heat_cor,
                                                     self.asyc_loop)
            else:  # 未缓存
                if self.down_thread.isFinished():
                    self.down_thread.start()
                asyncio.run_coroutine_threadsafe(
                    self._get_chapter(url_index, chaper_name, info),
                    self.asyc_loop)

    def cache_chapter(self, index: int, chapter_name: str,
                      content: Iterable[str], read_dir: QDir,
                      info: InfoObj) -> None:  # 缓存阅读章节
        save_dir = info.novel_name + info.hexdigest
        if read_dir.exists(save_dir) == False:
            read_dir.mkdir(save_dir)
        s_dir = QDir(read_dir.absoluteFilePath(save_dir))
        cache_name = f'{index}___' + chapter_name.strip().strip('___') + '.txt'
        cache_name = re.sub(r'[\\\/\:\>\<\?\*]', '', cache_name)
        native = QDir.toNativeSeparators(s_dir.absoluteFilePath(cache_name))
        with open(native, 'w+', encoding='utf8') as file:
            file.write(chapter_name.strip() + '\n')
            for line in content:
                file.write(line.strip() + '\n')

    def chapter_exists(self, index: int, read_dir: QDir,
                       info: InfoObj) -> bool:  # 检测缓存中章节是否存在
        save_dir = info.novel_name + info.hexdigest
        if read_dir.exists(save_dir) == False:
            read_dir.mkdir(save_dir)
        s_path = read_dir.absoluteFilePath(save_dir)
        flags = [int(v.split('___')[0]) for v in os.listdir(s_path)]
        if index in flags:
            return True
        return False

    def exits_chapters(self, read_dir: QDir,
                       info: InfoObj) -> List[int]:  # 已缓存的章节index
        save_dir = info.novel_name + info.hexdigest
        if read_dir.exists(save_dir):
            s_path = read_dir.absoluteFilePath(save_dir)
            flags = [int(v.split('___')[0]) for v in os.listdir(s_path)]
            flags.sort()
            return flags
        return []

    def _get_message_from_caches(self, index: int, read_dir: QDir,
                                 info: InfoObj) -> dict:  # 从缓存章节中重新渲染
        res = {'content': [], 'chapter': ''}
        save_dir = info.novel_name + info.hexdigest
        s_path = read_dir.absoluteFilePath(save_dir)
        s_dir = QDir(s_path)
        temp = list(os.listdir(s_path))
        flags = [int(v.split('___')[0]) for v in temp]
        finded_index = flags.index(index)
        if finded_index >= 0:
            cache_name = temp[finded_index]
            with open(s_dir.absoluteFilePath(cache_name), 'r',
                      encoding='utf8') as file:
                for index, line in enumerate(file):
                    if index == 0:
                        res['chapter'] = line.strip()
                    else:
                        res['content'].append(line.strip())
        return res

    def pre_heat_tasks(self,
                       start_index: int,
                       count: int,
                       read_dir: QDir,
                       info: InfoObj,
                       client: httpx.AsyncClient,
                       handler: Handler,
                       all: bool = False) -> List[asyncio.Task]:  # 预下载
        total = info.chapter_count()
        exists_chapters = self.exits_chapters(read_dir, info)
        res = []
        for i in range(start_index, start_index + count):
            next_index = i
            if next_index + 1 <= total:
                if next_index not in exists_chapters:
                    task_info = info.getTaskInfo(next_index)
                    if task_info not in self.read_pools:
                        self.read_pools.add(task_info)
                        next_chapter = info.novel_chapter_urls[i][1]
                        next_url = info.novel_chapter_urls[i][0]
                        next_header = handler.chapter_headers_hook(
                            i, next_url, info)
                        next_task = asyncio.create_task(
                            self._down_chapter(i, next_url, next_chapter,
                                               next_header, client, info))
                        res.append(next_task)
        return res

    async def _run_pre_heat(self, start_index: int, read_dir: QDir,
                            info: InfoObj) -> asyncio.Task:  # 预下载缓存函数
        handler = get_handle_cls(info.novel_site)
        async with httpx.AsyncClient() as client:
            tasks = self.pre_heat_tasks(start_index, self.pre_count, read_dir,
                                        info, client, handler)
            for result in asyncio.as_completed(tasks):
                try:
                    content, chapter_name, res_index, url = await result
                    content = list(content)
                    self.cache_chapter(res_index, chapter_name, content,
                                       read_dir, info)
                    task_info = info.getTaskInfo(res_index)
                    self.read_pools.remove(task_info)
                except Exception as e:
                    task_info = e.task_info
                    self.read_pools.remove(task_info)

    async def _get_chapter(self,
                           url_index: int,
                           chapter_name: str,
                           info: InfoObj,
                           all: bool = False) -> None:  # 请求章节内容
        novel_app = info.novel_app
        read_dir = novel_app.getReadCachesDir()
        handler = get_handle_cls(info.novel_site)
        async with httpx.AsyncClient() as client:
            tasks = []
            task_info = info.getTaskInfo(url_index)
            if self.chapter_exists(url_index, read_dir, info) == False:
                if task_info not in self.read_pools:
                    self.read_pools.add(task_info)
                    url = info.novel_chapter_urls[url_index][0]
                    header = handler.chapter_headers_hook(url_index, url, info)
                    task = asyncio.create_task(
                        self._down_chapter(url_index, url, chapter_name,
                                           header, client, info))
                    tasks.append(task)
                pre_heats = self.pre_heat_tasks(url_index + 1, self.pre_count,
                                                read_dir, info, client,
                                                handler)
                tasks.extend(pre_heats)
                for result in asyncio.as_completed(tasks):
                    try:
                        content, chapter_name, res_index, url = await result
                        content = list(content)
                        self.cache_chapter(res_index, chapter_name, content,
                                           read_dir, info)
                        task_info = info.getTaskInfo(res_index)
                        self.read_pools.remove(task_info)
                        if res_index == url_index:
                            emit_value = {
                                'chapter': chapter_name,
                                'content': content
                            }
                            self.single_signal.emit(emit_value)
                    except Exception as e:
                        task_info = e.task_info
                        if e.url_index == url_index:
                            self.single_fail_signal.emit({
                                'content':
                                str(e),
                                'chapter':
                                e.chapter_name
                            })
                        self.read_pools.remove(task_info)
            else:
                res = self._get_message_from_caches(url_index, read_dir, info)
                self.single_signal.emit(res)


class _AsyncThread(QThread):
    def __init__(self, master: ChapterDownloader,
                 loop: asyncio.AbstractEventLoop):
        super().__init__()
        self._master = master
        self._loop = loop

    def run(self):
        with self._master:
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()


class BasicChapterDownTask(ChapterDownloader):

    name = 'BasicChapterDownTask'


class BasicFileDownTask(QThread):

    header = {}

    use_plugin: bool = True

    name: str = None

    def __init__(self, inf: InfoObj, loader: FileDownloader):
        super().__init__()
        self.inf = inf
        self.loader = loader
        self._master = inf.novel_app

    def _size_hum_read(self, value: int) -> str:
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = 1024.0
        for i in range(len(units)):
            if (value / size) < 1:
                return "%.2f%s" % (value, units[i])
            value = value / size

    def run(self):
        with self.loader, self.inf.locked():
            try:
                self.download()
            except RequestException as e:
                self.loader.log_msgs.append(
                    (str(e), logging.ERROR, self.loader.msg_time()))
                self.loader.down_status = 2
                self.inf.novel_status = DownStatus.down_fail  # '下载失败'
                self.loader.update_signal.emit(self.inf)
                self.loader.flag_signal.emit(self.inf)
                with suppress(Exception):
                    os.remove(self.save_path)
            except Exception as e:
                self.loader.log_msgs.append(
                    (str(e), logging.ERROR, self.loader.msg_time()))
                self.loader.down_status = 2
                self.inf.novel_status = DownStatus.down_fail  # '下载失败'
                self.loader.update_signal.emit(self.inf)
                self.loader.flag_signal.emit(self.inf)
                with suppress(Exception):
                    os.remove(self.save_path)

    def downHeaderHook(self, inf) -> dict:
        return get_handle_cls(inf.novel_site).file_headers_hook(inf)

    def savePathHook(self, response, inf: InfoObj) -> str:
        return get_handle_cls(inf.novel_site).save_path_hook(response, inf)

    def download(self):
        inf = self.inf
        inf.novel_flag = True  # download下载标志位
        inf.novel_start_time = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')  # 下载创建时间
        inf.novel_status = DownStatus.down_ing  # '下载中'

        task_widget = inf.novel_app.getCurrentTaskWidget(
        ) if inf.novel_app else None  # 更新
        if task_widget and inf.novel_index == task_widget._inf.novel_index:  # 更新信息
            self.loader.update_signal.emit(inf)
        qdir = QDir(inf.novel_save_path)
        if qdir.exists() == False:
            qdir.mkdir(inf.novel_save_path)

        down_header = self.downHeaderHook(inf)
        time_ = time.time()

        r = requests.get(inf.novel_url, headers=down_header, stream=True)
        if r.headers.get('content-length', None) is None:
            total_cache = r.content
            total_size = len(total_cache)
        else:
            total_size = int(r.headers['content-length'])  # 请求文件的大小, 单位字节B
            total_cache = False
        content_size = 0  # 以下载的字节大小
        plan = 0  # 进度下载完成的百分比
        start_time = time.time()  # 请求开始的时间
        temp_size = 0  # 上秒的下载大小
        total_size_humen = self._size_hum_read(total_size)
        inf.novel_file_size = total_size_humen

        save_path = self.savePathHook(r, inf)
        log_msgs = self.loader.log_msgs
        msg_time = self.loader.msg_time
        update_signal = self.loader.update_signal
        self.save_path = save_path
        self.loader.down_status = 1
        with open(save_path, 'wb') as file:
            if total_cache:
                file.write(total_cache)
                content_size = total_size
            else:
                log_msgs.append(
                    (f'{inf.novel_name}[{inf.novel_site}] 开始下载', logging.INFO,
                     msg_time()))
                for content in r.iter_content(
                        chunk_size=1024):  # 开始下载每次请求1024字节
                    if inf.novel_down_cancel:
                        # print(inf.novel_name, ':停止下载')
                        log_msgs.append(f'下载已取消 -- {save_path}', logging.INFO,
                                        msg_time())
                        break
                    task_widget = inf.novel_app.getCurrentTaskWidget(
                    ) if inf.novel_app else None
                    if task_widget and inf.novel_index == task_widget._inf.novel_index:  # 更新信息
                        inf.novel_file_size = self._size_hum_read(total_size)
                        update_signal.emit(inf)
                    if content:
                        file.write(content)
                    content_size += len(content)  # 统计以下载大小
                    plan = (content_size / total_size) * 100  # 计算下载进度
                    if time.time() - start_time >= 1:  # 每一秒统计一次下载量
                        start_time = time.time()  # 重置开始时间
                        speed = self._size_hum_read(content_size -
                                                    temp_size) + '/s'  # 每秒的下载量
                        temp_size = content_size  # 重置以下载大小
                        status = DownStatus.down_ing
                        inf.novel_averge_speed = self._size_hum_read(
                            content_size /
                            (time.time() - time_)) + '/s'  # 平均速度
                        inf.novel_speed = speed
                        inf.novel_percent = float('%.1f' % plan)
                        inf.novel_status = status
                        inf.novel_meta[
                            'down_size'] = f'已下载：{self._size_hum_read(content_size)}/{total_size_humen}'
                        log_msgs.append((
                            f'下载进度--{inf.novel_percent}; 已下载--{inf.novel_meta["down_size"]}; 速度--{inf.novel_speed}',
                            logging.INFO, msg_time()))
                        if task_widget and inf.novel_index == task_widget._inf.novel_index:
                            update_signal.emit(inf)
        # with inf.locked():
        if inf.novel_down_cancel == False:  # 下载完成
            cost_time = time.time() - time_
            inf.novel_averge_speed = self._size_hum_read(
                content_size / (time.time() - time_)) + '/s'  # 平均速度
            inf.novel_percent = 100
            inf.novel_status = DownStatus.down_ok
            inf.novel_end_time = datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S')  # 下载结束时间
            inf.novel_speed = '--'
            inf.novel_meta[
                'down_size'] = f'已下载：{total_size_humen}/{total_size_humen}'
            inf.novel_download = True
            inf.novel_flag = True
            log_msgs.append((
                f'{inf.novel_name}[{inf.novel_site}].{inf.novel_file_type} -- 已保存:{inf.novel_file_size}',
                logging.INFO, msg_time()))
            self.loader.down_status = 2
            self.loader.flag_signal.emit(inf)
            if task_widget and inf.novel_index == task_widget._inf.novel_index:
                update_signal.emit(inf)

            if r.ok:
                rename_path = qdir.absoluteFilePath(inf.novel_name +
                                                    f'[{inf.novel_site}].' +
                                                    inf.novel_file_type)
                renamed = QFile.rename(save_path, rename_path)
                inf.novel_file_size = self._size_hum_read(
                    QFileInfo(rename_path).size())

                inf.dump()
            else:  # 死链接,空链接则下载失败,移除文件
                try:
                    os.remove(save_path)
                except:
                    traceback.print_exc()
        else:  # 终止下载任务
            inf.novel_status = DownStatus.down_before
            inf.novel_percent = 0
            inf.novel_start_time = '--'
            inf.novel_end_time = '--'
            inf.novel_speed = '--'
            inf.novel_meta['down_size'] = ''
            inf.novel_download = False
            inf.novel_flag = False
            self.loader.down_status = 2
        self.loader.flag_signal.emit(inf)


@register
class _ZhiXuanDownTask(BasicFileHandler):
    use_plugin = True
    name = '知轩藏书'
    header = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    def file_headers_hook(cls, inf: InfoObj):
        down_header = cls.header.copy()
        down_header.update(Host=urlparse(inf.novel_url).netloc)
        return down_header


@register
class _JiuJiuDownTask(BasicFileHandler):
    use_plugin = True
    name = "九九小说"
    header = {
        'Host': 'down.txt99.org',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language':
        'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.txt99.org/',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1'
    }

    def save_path_hook(self, response, inf):
        inf.novel_file_type = 'txt'
        qdir = QDir(inf.novel_save_path)
        if qdir.exists() == False:
            qdir.mkdir(inf.novel_save_path)
        save_path = qdir.absoluteFilePath(inf.novel_name + '.' +
                                          inf.novel_file_type) + '.download'
        return save_path

    def file_headers_hook(cls, inf):
        return cls.header


@register
class _ZNDownTask(BasicFileHandler):
    use_plugin = True
    name = "宅男小说"
    header = {
        "accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding":
        "gzip, deflate, br",
        "accept-language":
        "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control":
        "no-cache",
        "pragma":
        "no-cache",
        "sec-fetch-dest":
        "document",
        "sec-fetch-mode":
        "navigate",
        "sec-fetch-site":
        "none",
        "sec-fetch-user":
        "?1",
        "upgrade-insecure-requests":
        "1",
        "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74",
    }


@register
class _EightDownTask(BasicFileHandler):
    use_plugin = True
    header = {
        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding":
        "gzip, deflate",
        "Accept-Language":
        "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control":
        "no-cache",
        "Connection":
        "keep-alive",
        "Host":
        "down.txt8080.com",
        "Pragma":
        "no-cache",
        "Upgrade-Insecure-Requests":
        "1",
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74"
    }
    name = '八零小说'

    def file_headers_hook(cls, inf: InfoObj):
        down_url = inf.novel_url
        netloc = urlparse(down_url).netloc
        cls.header.update(Host=netloc)
        return cls.header


class ImgDownTask(QRunnable):
    def __init__(self, inf: InfoObj):
        super().__init__()
        self.inf = inf

    def run(self):
        try:
            inf = self.inf
            qdir = QDir(inf.novel_img_save_path)
            img_save_path = QDir.toNativeSeparators(
                qdir.absoluteFilePath(inf.novel_img_name))
            if inf.novel_img_url:
                icon_widget = inf.novel_app.getIconWidget(
                    inf.novel_index - 1) if inf.novel_app else None
                resp = requests.get(inf.novel_img_url,
                                    headers=inf.novel_img_headers)
                resp.raise_for_status()
                if inf.novel_img_save_flag == False:
                    icon_widget.retry_counts += 1
                    with open(img_save_path, 'wb') as image:
                        image.write(resp.content)
                if icon_widget:
                    QMetaObject.invokeMethod(icon_widget, 'setNovelImage',
                                             Qt.AutoConnection,
                                             Q_ARG(str, img_save_path))
        except RequestException:
            try:
                if os.path.exists(img_save_path):
                    os.remove(img_save_path)
                inf.novel_img_save_flag = False
                self.retry(icon_widget)
            except:
                ...
        except FileNotFoundError:
            ...  # 宅男小说\绝色房东爱上我\最强医道.jpg
        except:
            ...
        finally:
            inf.novel_img_save_flag = True

    def retry(self, widget):  # tenacity
        inf = self.inf
        qdir = QDir(inf.novel_img_save_path)
        img_save_path = QDir.toNativeSeparators(
            qdir.absoluteFilePath(inf.novel_img_name))
        image = open(img_save_path, 'wb')
        while True:
            widget.retry_counts += 1
            # print('第%s次下载' % widget.retry_counts, ':', inf.novel_img_name)
            resp = requests.get(inf.novel_img_url,
                                headers=inf.novel_img_headers)
            if resp.ok:
                image.write(resp.content)
                image.close()
                inf.novel_img_save_flag = True
                break
            if widget.retry_counts == widget.MAX_RETRY_COUNTS:
                if resp.ok == False:
                    image.close()
                    os.remove(img_save_path)
                    inf.novel_img_save_flag = True
                else:
                    image.write(resp.content)
                    image.close()
                    inf.novel_img_save_flag = True
                break
        QMetaObject.invokeMethod(widget, 'setNovelImage', Qt.AutoConnection,
                                 Q_ARG(str, widget.file_path))

    def validImage(self, file_path: str) -> bool:
        valid = True
        try:
            Image.open(file_path).verify()
        except:
            valid = False
        return valid
