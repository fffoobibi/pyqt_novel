'''
说明

插件名称必须已chapter开头的py文件,比如chapter1.py, chapter2.py
插件必须定义两个类: BasicChapterDownTask为下载小说章节的类, BasicFileSpider为搜索小说的scrapy.Spider子类

BasicFileSpider子类中必须定义InfoObj对象,根据爬取的网站规则定义好以下字段内容, 自定义的插件才能成功使用

inf = InfoObj()
inf.novel_name = '诛仙'               # 必须定义,搜索结果的小说名称
inf.novel_chapter_urls = [(chapter_url: str, chapter_name: str), ...]   #必须定义: (小说章节url, 小说章节名), ...
self.finalStep(inf)                 # 必须调用,开始爬取,当定义好inf所需要的字段,否则插件无法正常运行

inf.novel_introutced = '...'         # 小说详情介绍,可以不定义
inf.novel_img_url = 'http://...'     # 可以不定义,小说封面url, 如果为'',则不下载小说封面
inf.novel_img_headers = {}           # 小说封面下载headers
inf.novel_info_url = 'http://...'    # 可以不定义,小说详情url,可以不定义

'''

import scrapy
import httpx
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse
from httpx._types import CookieTypes

from bs4 import BeautifulSoup
from app_runtime import BasicChapterSpider, BasicChapterHandler, register, InfoObj


@register
class ChapterTask新笔趣阁(BasicChapterHandler):

    use_plugin = True  # 为True时使用插件, 默认不使用

    name = '新笔趣阁'  # 必须定义:唯一名称,和BasicFileSpider子类名称相同

    header = {
        "Host": "www.xbiquge.la",
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language":
        "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "http://www.xbiquge.la/53/53951/",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }  # 当前小说章节的下载headers

    # 设置下载小说章节header的钩子函数,默认返回{}
    def chapter_headers_hook(cls, url_index: int, url: int, inf: InfoObj):
        if url_index == 0:
            cls.header['Referer'] = inf.novel_info_url
        else:
            cls.header['Referer'] = inf.novel_chapter_urls[url_index - 1][0]
        return cls.header

    def parse_charpter(cls, url_index: int, response: 'httpx.Response',
                       chapter: str):
        '''
        url_index: 当前的章节的初始请求顺序
        response: httpx.Response实例
        return: 返回值是一个2元元组, content_line, chapter_name
            content_line: Iterable[str] 即小说章节文本内容,是一个可迭代的文本行的序列(推荐返回文本行的生成器, bs4 tag.stripped_strings属性即是个生成器) 
            chapter_name: str 小说章节名

        示例:
        soup = BeautifulSoup(response.text, 'lxml')
        chapter, = soup.select('.txt_cont > h1:nth-child(1)')
        content_lines, = soup.select('#content1')
        return content_lines.stripped_strings, chapter.string

        '''
        soup = BeautifulSoup(response.text, 'lxml')
        chapter, = soup.select('.bookname h1')
        content_lines, = soup.select('#content')
        return content_lines.stripped_strings, chapter.string


class ChapterSpider新笔趣阁(BasicChapterSpider):

    name = '新笔趣阁'  # 必须定义:唯一名称,和BasicChapterDownTask子类名称相同

    novel_name = ''  # 待搜索的小说名称

    use_plugin = True  # 为True时使用插件, 默认不使用

    headers = {
        "Host": "www.xbiquge.la",
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language":
        "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://www.xbiquge.la",
        "Referer": "http://www.xbiquge.la/modules/article/waps.php",
        "Upgrade-Insecure-Requests": "1"
    }

    def start_requests(self):
        self.start_url = r'http://www.xbiquge.la/modules/article/waps.php'
        form_data = {'searchkey': self.novel_name}
        yield scrapy.FormRequest(self.start_url,
                                 headers=self.headers,
                                 formdata=form_data)

    def parse(self, response):
        extrator = LinkExtractor(restrict_css=['.grid td.even'])
        links = extrator.extract_links(response)
        chapter_headers = {
            "Host": "www.xbiquge.la",
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
            "Accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language":
            "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "http://www.xbiquge.la/modules/article/waps.php",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        for link in links:
            yield scrapy.Request(link.url,
                                 self.getChapter,
                                 headers=chapter_headers)

    def getChapter(self, response):
        '''
        ...
        results = [(url, chapter_name), ...]
        inf.novel_chapter_urls = results
        self.finalStep(inf)

        '''
        introutecd1 = ' '.join([
            value
            for value in response.css('#info p::text, #info a::text').getall()
            if value.strip()
        ])
        introutced2 = '\n'.join([
            value for value in response.css('#intro *::text').getall()
            if value.strip()
        ])
        introutced = introutecd1 + '\n' + introutced2
        novel_name = response.css('#info h1::text').get('')
        img_url = response.css('#fmimg img::attr(src)').get('')
        img_headers = {
            "Host": "www.xbiquge.la",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Accept": "image/webp,*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": response.url,
            # "Cookie": "bdshare_firstime=1621141439161; _abcde_qweasd=0",
            "Cache-Control": "max-age=0",
        }

        chapter_links_extrator = LinkExtractor(restrict_css=['#list dd'])
        links = chapter_links_extrator.extract_links(response)
        novel_chapter_urls = [(link.url, link.text) for link in links]
        novel_info_url = response.url
        info = InfoObj()
        info.novel_name = novel_name
        info.novel_introutced = introutced
        info.novel_info_url = novel_info_url
        info.novel_img_url = img_url
        info.novel_img_headers = img_headers
        info.novel_chapter_urls = novel_chapter_urls
        self.finalStep(info)

    @classmethod
    def subscribe_updateinfo(cls, response: HtmlResponse) -> InfoObj:
        introutecd1 = ' '.join([
            value
            for value in response.css('#info p::text, #info a::text').getall()
            if value.strip()
        ])
        introutced2 = '\n'.join([
            value for value in response.css('#intro *::text').getall()
            if value.strip()
        ])
        introutced = introutecd1 + '\n' + introutced2
        chapter_links_extrator = LinkExtractor(restrict_css=['#list dd'])
        links = chapter_links_extrator.extract_links(response)
        novel_chapter_urls = [(link.url, link.text) for link in links]
        novel_info_url = response.url
        info = InfoObj()

        info.novel_introutced = introutced
        info.novel_info_url = novel_info_url
        info.novel_chapter_urls = novel_chapter_urls
        return info
