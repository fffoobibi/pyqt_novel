import os
import json
import traceback
import pprint
import shutil

from dataclasses import dataclass, field, asdict
from hashlib import md5
from datetime import datetime
from threading import Lock
from typing import Callable, Optional
from enum import Enum
from copy import deepcopy

from PyQt5.QtCore import QDir

__all__ = ('DownStatus', 'Markup', 'TaskInfo', 'InfoObj', 'InfTools')


class DownStatus(str, Enum):
    down_before = '未处理'  # 未处理
    down_ing = '下载中'  # 下载中
    down_ok = '已下载'  # 已下载
    down_fail = '下载失败'  # 下载失败

    @classmethod
    def get_fromstr(cls, value: str) -> 'DownStatus':
        for member in cls:
            if member == value:
                return member

class _lasyproperty(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self.func(instance)
        instance.__dict__[self.func.__name__] = value
        return value


@dataclass
class Markup(object):
    index: int = -1
    chapter: str = ''
    percent: float = 0
    create_time: str = field(default_factory=lambda: str(datetime.now()))
    content: str = ''

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return False

    def __hash__(self) -> int:
        return hash(f'{self.index}{self.chapter}{self.create_time}')

    def as_dict(self) -> dict:
        return asdict(self)

    def copy(self) -> 'MarkUp':
        return Markup(self.index, self.chapter, self.percent, self.create_time,
                      self.content)

    def __deepcopy__(self, memo: dict) -> 'MarkUp':
        return self.copy()

    @classmethod
    def from_dict(cls, value: dict) -> 'MarkUp':
        self = cls()
        for key in value.keys():
            self.__dict__[key] = value[key]
        return self


@dataclass
class TaskInfo(object):
    down_index: int = -1
    down_site: str = ''
    down_chapter: str = ''
    down_url: str = ''
    valid: bool = True

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return hash(self) == hash(o)
        return False

    def __hash__(self) -> int:
        return hash('%s%s%s%s%s' %
                    (self.down_index, self.down_site, self.down_chapter,
                     self.down_url, self.valid))

    def copy(self) -> 'TaskInfo':
        return TaskInfo(self.down_index, self.down_site, self.down_chapter,
                        self.down_url, self.valid)

    def __deepcopy__(self, memo) -> 'TaskInfo':
        return self.copy()


@dataclass
class InfoObj(object):

    novel_index: int = -1  # 小说序号
    novel_name: str = ''  # 小说名                          **
    novel_size: str = '--'  # 小说大小                      **
    novel_site: str = ''  # 小说站点                        **

    novel_introutced: str = ''  # 小说介绍                **
    novel_save_path: str = ''  # 小说保存路径             **
    novel_url: str = ''  # 小说整本下载url                    **
    novel_headers: dict = field(default_factory=dict)  # 小说下载headers
    novel_file_type: str = ''  # 下载文件的格式            **

    novel_start_time: str = '--'  # 下载创建时间
    novel_end_time: str = '--'  # 下载完成时间
    novel_cost_time: float = 0  # 下载耗时
    novel_download: bool = False  # 文件是否下载        **
    novel_status: DownStatus = DownStatus.down_before  # 未处理, 已下载, 下载中,下载失败
    novel_percent: float = 0  # 下载进度
    novel_speed: str = '--'  # 实时下载速度
    novel_averge_speed: str = '--'  # 下载平均速度
    novel_flag: bool = False  # 下载标志
    novel_down_cancel: bool = False  # 下载任务是否暂停
    novel_file_size: str = '--'  # 下载文件大小

    novel_app: 'NovelWidget' = None  # 下载程序        **
    novel_meta: dict = field(
        default_factory=dict
    )  # 可以传递的数据, submit_widget, novel_colors, dump_file_path, submit_file_path, down_size, root_index

    novel_img_not_found: str = ''  # 未发现图片封面
    novel_img_url: str = ''  # 图片下载地址
    novel_img_headers: dict = field(default_factory=dict)  # 图片下载header
    novel_img_name: str = ''  # 小说封面名称和小说名相同，  **
    novel_img_save_path: str = ''  # 小说封面图片保存目录， **
    novel_img_save_flag: bool = False  # 小说封面是否下载

    _is_file: bool = True  #
    _mark_convert: bool = False  #
    novel_temp_data: dict = field(
        default_factory=dict)  # link_headers, root_index
    novel_info_url: str = ''  # 小说详情页面url **
    novel_subs_url: str = ''  # 订阅url
    novel_subs_headers: dict = field(default_factory=dict)  # 订阅url
    novel_subs_state: bool = False  # 订阅状态
    novel_subs_index: int = -1  # 订阅顺序
    novel_fresh_state: int = 0  # 更新状态 0,初始化, 1进行中, 2完成更新, 3更新失败
    novel_read_infos: dict = field(
        default_factory=dict
    )  # 个人阅读记录 # index, chapter_name, percent, book_marks
    novel_chapter_urls: list = field(
        default_factory=list
    )  # 小说章节下载urls [(url, chapter_name, select_state, cache_sate), ...]

    def __post_init__(self) -> None:
        if not isinstance(self, DownStatus):
            self.novel_status = DownStatus.get_fromstr(self.novel_status)
        if not self._mark_convert:
            res = []
            convert = self.novel_read_infos.get('book_marks', [])
            for dic in convert:
                if not isinstance(dic, Markup):
                    res.append(Markup.from_dict(dic))
            self.novel_read_infos['book_marks'] = res

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)
        return False

    def __hash__(self) -> int:
        return hash(self.novel_name + self.novel_site + self.novel_subs_url)

    def __getstate__(self) -> dict:
        return self.__dict__

    def __setstate__(self, state) -> None:
        self.__dict__ = state

    @_lasyproperty
    def hexdigest(self) -> str:
        _ = (self.novel_name + self.novel_site +
             self.novel_subs_url).encode('utf8')
        return md5(_).hexdigest()

    @classmethod
    def fromJson(cls, json_dict: dict = None, *, fp=None) -> 'InfoObj':
        inf = cls(_mark_convert=True)
        json_dict = json.load(fp) if fp else json_dict
        if json_dict:
            for key in json_dict.keys():
                setattr(inf, key, json_dict[key])
        inf.novel_status = DownStatus.get_fromstr(inf.novel_status)
        res = []
        convert = inf.novel_read_infos.get('book_marks', [])
        for dic in convert:
            if not isinstance(dic, Markup):
                res.append(Markup.from_dict(dic))
        inf.novel_read_infos['book_marks'] = res
        return inf

    @classmethod
    def fromPath(cls, file_path: str) -> 'InfoObj':
        inf = cls(_mark_convert=True)
        fp = open(file_path, 'r', encoding='utf8')
        json_dict = json.load(fp)
        for key in json_dict.keys():
            value = json_dict[key]
            if isinstance(value, (dict, list)):
                setattr(inf, key, deepcopy(value))
            else:
                setattr(inf, key, json_dict[key])
        inf.novel_status = DownStatus.get_fromstr(inf.novel_status)
        res = []
        convert = inf.novel_read_infos.get('book_marks', [])
        for dic in convert:
            res.append(Markup.from_dict(dic))
        inf.novel_read_infos['book_marks'] = res
        return inf

    def copy(self) -> 'InfoObj':
        info = InfoObj()
        info.update_from_other(self, [
            'novel_meta', 'novel_temp_data', 'novel_chapter_urls',
            'novel_read_infos'
        ])
        info.novel_headers = self.novel_headers.copy()
        info.novel_img_headers = self.novel_img_headers.copy()
        info.novel_subs_headers = self.novel_subs_headers.copy()
        info.novel_meta = deepcopy(self.novel_meta)
        info.novel_temp_data = deepcopy(self.novel_temp_data)
        info.novel_chapter_urls = deepcopy(self.novel_chapter_urls)
        # info.novel_read_infos = deepcopy(self.novel_read_infos) #  bug
        dic = {}
        book_marks = [
            mark.copy() for mark in self.novel_read_infos.get('book_marks')
        ]
        dic['book_marks'] = book_marks
        
        index = self.novel_read_infos.get('index')
        chapter = self.novel_read_infos.get('chapter_name')
        percent = self.novel_read_infos.get('percent')
        if index is not None:
            dic['index'] = index
        if chapter is not None:
            dic['chapter_name'] = chapter
        if percent is not None:
            dic['percent'] = percent

        info.novel_read_infos = dic
        return info

    def __deepcopy__(self, memo) -> 'InfoObj':
        return self.copy()

    def update(self, state: dict) -> None:
        self.__dict__.update(state)

    def update_from_other(self,
                          info: 'InfoObj',
                          noupdate_keys: list = None,
                          filter: Callable = None) -> None:
        for key in info.__dict__.keys():
            update_value = info.__dict__[key]
            update_value = filter(update_value) if filter else update_value
            if noupdate_keys is not None:
                if key not in noupdate_keys:
                    self.__dict__[key] = update_value
            else:
                self.__dict__[key] = update_value

    def print(self, **kwargs) -> None:
        if kwargs:
            for key in kwargs.keys():
                pprint.pprint(self.__dict__[key])
        else:
            pprint.pprint(self.__dict__)

    def dump(self) -> None:
        novel_app = self.novel_app
        qdir = novel_app.getDownCachesDir()
        dum_file_path = qdir.absoluteFilePath(self.novel_name +
                                              f'[{self.novel_site}].json')
        copyed = self.copy()
        copyed.novel_app = None
        copyed.novel_meta['dump_file_path'] = dum_file_path
        copyed.novel_meta['submit_widget'] = False
        copyed.novel_introutced = ''
        copyed.novel_info_url = ''
        copyed.novel_url = ''
        copyed.novel_img_url = ''
        copyed.novel_index = -1
        copyed.novel_chapter_urls = []
        copyed.novel_headers = {}
        copyed.novel_img_headers = {}
        copyed.novel_fresh_state = 0
        # copyed.novel_status = self.novel_status
        copyed.novel_temp_data.clear()
        temp = []
        for bookmark in copyed.novel_read_infos.get('book_marks', []):
            temp.append(bookmark.as_dict())
        copyed.novel_read_infos['book_marks'] = temp
        if copyed.__dict__.get('_lock'):
            copyed.__dict__.pop('_lock')
        f = open(dum_file_path, 'w', encoding='utf8')
        json.dump(copyed.__dict__, f, ensure_ascii=False, indent=1)

    def dump_subscribe(self, dump_path: str = None) -> None:
        novel_app = self.novel_app
        qdir = novel_app.getSubscribeDir()
        dum_file_path = qdir.absoluteFilePath(
            self.novel_name +
            f'[{self.novel_site}].json') if dump_path is None else dump_path
        copyed = self.copy()
        copyed.novel_temp_data.clear()
        copyed.novel_meta['submit_file_path'] = dum_file_path
        copyed.novel_meta['submit_widget'] = True
        copyed.novel_meta['down_size'] = ''
        copyed.novel_app = None
        copyed.novel_url = ''
        copyed.novel_img_url = ''
        copyed.novel_index = self.novel_subs_index + 1
        copyed.novel_headers = {}
        copyed.novel_img_headers = {}
        copyed.novel_start_time = '--'  # 下载创建时间
        copyed.novel_end_time = '--'  # 下载完成时间
        copyed.novel_cost_time = 0  # 下载耗时
        copyed.novel_download = False  # 文件是否下载        **
        copyed.novel_status = DownStatus.down_before  #'未处理'  # 未处理,已下载, 下载中,下载失败
        copyed.novel_percent = 0  # 下载进度
        copyed.novel_speed = '--'  # 实时下载速度
        copyed.novel_averge_speed = '--'  # 下载平均速度
        copyed.novel_flag = False  # 下载标志
        copyed.novel_down_cancel = False  # 下载任务是否暂停
        copyed.novel_file_size = f'共{len(self.novel_chapter_urls)}章'
        copyed.novel_fresh_state = 0
        temp = []
        for bookmark in copyed.novel_read_infos.get('book_marks', []):
            temp.append(bookmark.as_dict())
        copyed.novel_read_infos['book_marks'] = temp
        if copyed.__dict__.get('_lock'):
            copyed.__dict__.pop('_lock')
        f = open(dum_file_path, 'w', encoding='utf8')
        json.dump(copyed.__dict__, f, ensure_ascii=False, indent=1)

    def remove_subscribe(self) -> bool:
        result = False
        file_path = self.novel_meta.get('submit_file_path', None)
        if file_path is None:
            novel_app = self.novel_app
            qdir = novel_app.getSubscribeDir()
            submit_file_path = qdir.absoluteFilePath(
                self.novel_name + f'[{self.novel_site}].json')
            file_path = submit_file_path
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                self._remove_caches()
                result = True
            except:
                result = False
        return result

    def remove(self) -> bool:
        result = False
        file_path = self.novel_meta.get('dump_file_path', None)
        if file_path is None:
            novel_app = self.novel_app
            qdir = novel_app.getDownCachesDir()
            dump_file_path = qdir.absoluteFilePath(self.novel_name +
                                                   f'[{self.novel_site}].json')
            file_path = dump_file_path
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                result = True
            except:
                traceback.print_exc()
                result = False
        return result

    def prepare_restart(self) -> None:
        self.novel_averge_speed = '--'
        self.novel_status = DownStatus.down_before
        self.novel_start_time = '--'
        self.novel_end_time = '--'
        self.novel_cost_time = 0
        self.novel_percent = 0
        self.novel_flag = False
        self.novel_down_cancel = False
        self.novel_download = False
        self.novel_meta['down_size'] = ''
        self.novel_app.prepareRestartDownLoad(self)

    def selected_count(self) -> int:
        if self.novel_chapter_urls:
            v = (True for u, c, s in self.novel_chapter_urls if s)
            return len(list(v))
        return 0

    def chapter_count(self) -> int:
        if self._is_file:
            return 0
        else:
            return len(self.novel_chapter_urls)

    def latest_chapter(self) -> str:
        if self._is_file:
            return ''
        if self.novel_chapter_urls:
            return self.novel_chapter_urls[-1][1]
        return ''
    
    def first_chapter(self) -> str:
        if self._is_file:
            return ''
        if self.novel_chapter_urls:
            return self.novel_chapter_urls[0][1]
        return ''

    def bookmark_exists(self, index: int, chapter: str) -> Optional[Markup]:
        if self._is_file == True:
            return
        flag = self.novel_read_infos.get('book_marks', [])
        for markup in flag:
            if index == markup.index and chapter == markup.chapter:
                return markup
        return

    def remove_bookmark(self, index, chapter: str, time_str: str) -> bool:
        if self._is_file == True:
            return False
        flag = self.novel_read_infos.get('book_marks', [])
        flag_mark = Markup(index, chapter, 0, time_str)
        if flag:
            j = -1
            for markup in flag:
                j += 1
                if markup == flag_mark:
                    break
            if j > -1:
                self.novel_read_infos['book_marks'].pop(j)
                return True
        return False

    def _remove_caches(self) -> None:  # 删除阅读缓存目录
        cache_path = self.read_qdir().absoluteFilePath(self.cached_dir())
        shutil.rmtree(cache_path, True)

    @_lasyproperty
    def _lock(self) -> Lock:
        return Lock()

    def locked(self) -> 'InfoObj':
        return self

    def __enter__(self) -> None:
        self._lock.acquire()

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        self._lock.release()

    def getTaskInfo(self, url_index: int) -> TaskInfo:
        task = TaskInfo()
        if self._is_file == True:
            task.valid = False
        else:
            task.valid = True
            task.down_index = url_index
            task.down_chapter = self.novel_chapter_urls[url_index][1]
            task.down_url = self.novel_chapter_urls[url_index][0]
        return task

    def cached_dir(self) -> str:  # 返回缓存目录
        return self.novel_name + self.hexdigest

    def read_qdir(self) -> Optional[QDir]:  # 返回读取目录qdir
        if self.novel_app:
            return self.novel_app.getReadCachesDir()
        return


class InfTools(object):
    @staticmethod
    def addColor(color: str,
                 content: str,
                 inf: InfoObj = None,
                 *,
                 name: str = None) -> str:
        if content == '':
            return name if name else inf.novel_name
        name = name if name else inf.novel_name
        res = name.split(content)
        color_name = f'<font color={color}>{content}</font>'.join(res)
        return color_name


# class WeaKRefContainer():
#     def __init__(self):
#         self.res = []

#     def append(self, obj):
#         self.res.append(weakref.ref(obj, self._del))

#     def _del(self, ref_obj):
#         index = self.res.index(ref_obj)
#         self.res.pop(index)

#     def __len__(self):
#         return len(self.res)

#     def __iter__(self):
#         for weak_ref in self.res:
#             yield weak_ref()

#     if sys.version_info >= (3, 7):
#         def __class_getitem__(cls, type) -> str:
#             return f'{cls.__name__}[{type.__name__}]'