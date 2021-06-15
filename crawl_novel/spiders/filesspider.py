import os
import scrapy
import weakref

from scrapy.http.cookies import CookieJar
from scrapy.http import HtmlResponse
from scrapy.settings import Settings
from scrapy.selector import SelectorList, Selector
from os.path import abspath, join
from typing import Callable, Sequence, List, Iterable, Any, Union, Type
from crawl_novel import InfoObj

__all__ = ('BasicFileSpider', 'BasicChapterSpider', 'get_cached_spiders', 'get_spider_byname')

JoinStriped = Union[Iterable[str], SelectorList, Selector]

def get_cached_spiders() -> List[Type['BasicFileSpider']]:
    return list(RegisterSpiderMeta._weakclasses.values())

def get_spider_byname(name) -> Type['BasicFileSpider']:
    return RegisterSpiderMeta.getSPiderByName(name)

class PluginDes():

    def __init__(self, value: bool = False):
        self.use_plugin = value

    def __get__(self, instance, owner):
        if instance is not None:
            instance.__dict__['use_plugin'] = self.use_plugin
        return self.use_plugin

    def __set__(self, instance, value):
        self.use_plugin = value
        if instance is not None:
            instance.__dict__['use_plugin'] = value
        if value == False:
            try:
                RegisterSpiderMeta._weakclasses.pop(instance.name)
            except KeyError:
                ...


class RegisterSpiderMeta(type):

    _weakclasses = weakref.WeakValueDictionary()

    @classmethod
    def getSPiderByName(cls, name):
        return cls._weakclasses.get(name)

    def __new__(metacls, name, base, dicts):
        if name not in ('BasicFileSpider', 'BasicChapterSpider'):
            ignores = {'RETRY_HTTP_CODES': [
                500, 502, 503, 504, 400, 403, 404, 408], 'RETRY_ENABLED': True}
            dicts.setdefault('custom_settings', {})
            dicts.setdefault('novel_name', '')
            dicts.setdefault('save_path', '')
            flag = dicts.get('use_plugin', False)
            dicts['use_plugin'] = PluginDes(flag)
            dicts['custom_settings'].update(
                LOG_FORMAT=f'[%(name)s--{dicts.get("name", name)}] [%(asctime)s] %(levelname)s: %(message)s')
            dicts['custom_settings'].update(LOG_LEVEL='DEBUG')
            dicts['custom_settings'].update(IMAGES_STORE='')
            dicts['custom_settings'].update(ignores)
        spider_cls = super().__new__(metacls, name, base, dicts)
        if name not in ('BasicFileSpider', 'BasicChapterSpider'):
            weaks = metacls._weakclasses
            use_plugin = spider_cls.use_plugin
            if use_plugin == True:
                weaks[spider_cls.name] = spider_cls
            else:
                if spider_cls.name in weaks.keys():
                    pop_class = weaks.pop(spider_cls.name)
                    del pop_class
        return spider_cls

    def __repr__(self):
        return f'{self.__name__}<{self.name}, {self.use_plugin}>'

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> int:
        return self.name == other.name


class BasicFileSpider(scrapy.Spider, metaclass=RegisterSpiderMeta):

    _is_file = True

    name: str = 'basic_file_spider'

    use_plugin: bool = False

    q = None  # multiprocess Queue

    save_path = None  # 保存目录

    novel_name: str = ''

    img_not_found = ''

    default_log_file = abspath('./logs/log.txt')  # 默认log目录

    custom_settings = {'LOG_FILE': default_log_file,
                       'LOG_LEVEL': 'DEBUG'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # print(self.name, ' init')

    @classmethod
    def update_settings(cls, settings: Settings) -> None:
        images_caches = settings.get('app_images_caches', None)
        log_file = settings.get('app_log_file', None)
        if images_caches:
            img_path = abspath(join(images_caches, cls.name))
            if os.path.exists(img_path) == False:
                os.mkdir(img_path)
            cls.custom_settings['IMAGES_STORE'] = img_path
        if log_file:
            cls.custom_settings['LOG_FILE'] = log_file
        super().update_settings(settings)

    @classmethod
    def get_cached_spiders(cls) -> List[Type['BasicFileSpider']]:
        return list(cls._weakclasses.values())

    @classmethod
    def getSPiderByName(cls, name: str) -> Type['BasicFileSpider']:
        return RegisterSpiderMeta.getSPiderByName(name)

    def finalStep(self, inf: InfoObj) -> None:
        novel_name = inf.novel_name.strip()
        img_url = inf.novel_img_url
        inf.novel_name = novel_name
        inf.novel_site = self.name
        inf.novel_img_save_path = abspath(self.custom_settings.get('IMAGES_STORE'))
        inf.novel_img_name = novel_name + '.' + img_url.split('.')[-1].split('.')[-1].strip()
        inf._is_file = self._is_file
        if inf.novel_subs_url == '' and inf.novel_info_url:
            inf.novel_subs_url = inf.novel_info_url
        if not self._is_file:
            processed = []
            for tu in inf.novel_chapter_urls:
                if len(tu) == 2:
                    temp = list(tu)
                    temp.append(True) # select_state
                    processed.append(temp)
                elif len(tu) == 3:
                    temp = list(tu)
                    processed.append(temp)
            inf.novel_chapter_urls = processed
            inf.novel_file_type = 'txt'
            inf.novel_file_size = f'共{len(inf.novel_chapter_urls)}章'
            inf.novel_size = inf.novel_file_size
            inf.novel_url = '--'
        if self.save_path:
            inf.novel_save_path = self.save_path
        if self.q:
            self.q.put(inf)

    def get_cookies(self, response: HtmlResponse) -> dict:
        cookiejar = CookieJar()
        cookiejar.extract_cookies(response, response.request)
        cookies = {}
        for cookies_item in cookiejar:
            cookies[cookies_item.name] = cookies_item.value
        return cookies

    @staticmethod
    def split_sequence(dst: Sequence, split_num: int, deep=False) -> List:
        if deep:
            dst = list(BasicFileSpider.flat_sequence(dst))
        return [dst[i:i+split_num] for i in range(0, len(dst), split_num)]

    @staticmethod
    def flat_sequence(dst) -> Iterable[Any]:
        for v in dst:
            if isinstance(v, (list, tuple)) and not isinstance(v, (str, bytes)):
                yield from BasicFileSpider.flat_sequence(v)
            else:
                yield v

    @staticmethod
    def join_striped(sequence: JoinStriped, func: Callable=None, get_func=None, join_sep: str=' ') -> str:
        if isinstance(sequence, SelectorList):
            sequence = sequence.getall()
        elif isinstance(sequence, Selector):
            sequence = [sequence.get('')]
        filter_rule = lambda e: e.strip() if func is None else func
        f = filter(filter_rule, sequence)
        get_rule = lambda e: e.strip() if get_func is None else get_func
        return join_sep.join(map(get_rule, f))

from httpx._types import CookieTypes  

class BasicChapterSpider(BasicFileSpider):
    _is_file = False

    name = 'BasicChapterSpider'

    @classmethod
    def subscribe_cookies(cls) -> CookieTypes:
        return None

    @classmethod
    def subscribe_updateinfo(cls, response: HtmlResponse) -> InfoObj:
        return None

    @classmethod
    def process_subscribe_updateinfo(cls, old_inf: InfoObj, update_inf: InfoObj) -> InfoObj:
        if update_inf is not None:
            res = []
            for chapter_tuple in update_inf.novel_chapter_urls:
                temp = list(chapter_tuple)
                if len(temp) == 2:
                    temp.append(True)
                    res.append(temp)
            update_inf.novel_chapter_urls = res
            temp_introduce = update_inf.novel_introutced
            update_inf.update_from_other(old_inf, ['novel_chapter_urls', 'novel_introutced'])
            if temp_introduce.strip() == '':
                update_inf.novel_introutced = old_inf.novel_introutced
            if len(update_inf.novel_chapter_urls) == 0:
                update_inf.novel_fresh_state = 3 # 更新失败
                old_inf.novel_fresh_state = 3
                update_inf.novel_chapter_urls = old_inf.novel_chapter_urls
            else:
                update_inf.novel_fresh_state = 1 # 更新成功
                old_inf.novel_fresh_state = 1
            update_inf.dump_subscribe()
            return update_inf
        return 
        