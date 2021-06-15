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
class ChapterTask笔趣阁2(BasicChapterHandler):

    use_plugin = True  # 为True时使用插件, 默认不使用

    name = '笔趣阁2'  # 必须定义:唯一名称,和BasicFileSpider子类名称相同

    header = {
        "Host": "www.biquge.se",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "http://www.biquge.se/1117/",
        # "Cookie": "796ab53acf966fbacf8f078ecd10a9ce=a%3A1%3A%7Bi%3A7634%3Bs%3A27%3A%2234852057%7C%2A%7C%E7%AC%AC1198%E7%AB%A0%E9%A5%B2%E9%81%93%22%3B%7D; obj=1; PHPSESSID=vuqotmg3p7el6mviq77d6vvae0; f0e8da1bcc3ceda15eea7ba63aa10b01=1",
        "Upgrade-Insecure-Requests": "1"
    }  # 当前小说章节的下载headers

    # 设置下载小说章节header的钩子函数,默认返回{}
    def chapter_headers_hook(cls, url_index: int, url: int, inf: InfoObj):
        if url_index == 0:
            cls.header['Referer'] = inf.novel_info_url
        else:
            cls.header['Referer'] = inf.novel_chapter_urls[url_index - 1][0]
        return cls.header

    def parse_charpter(cls, url_index: int, response: 'httpx.Response', chapter: str):
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


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "max-age=0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "www.biquge.se",
    "Origin": "http://www.biquge.se",
    "Referer": "http://www.biquge.se/case.php?m=search",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.56"
}


class ChapterSpider笔趣阁2(BasicChapterSpider):

    name = '笔趣阁2'  # 必须定义:唯一名称,和BasicChapterDownTask子类名称相同

    novel_name = ''  # 待搜索的小说名称

    use_plugin = True  # 为True时使用插件, 默认不使用

    def start_requests(self):
        cookies_url = 'http://www.biquge.se/'
        yield scrapy.Request(cookies_url, self._search)

    def _search(self, response):
        self.cookies = self.get_cookies(response)
        search_url = 'http://www.biquge.se/case.php?m=search'
        form_data = {'key': self.novel_name}
        yield scrapy.FormRequest(search_url, headers=headers, formdata=form_data, cookies=self.cookies)

    def parse(self, response):
        '''
        ...
        results = [(url, chapter_name), ...]
        inf.novel_chapter_urls = results
        self.finalStep(inf)

        '''
        extrator = LinkExtractor(restrict_css=['.l span.s2'])
        links = extrator.extract_links(response)
        chapter_headers = {
            "Host": "www.biquge.se",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "http://www.biquge.se/case.php?m=search",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        for link in links:
            yield scrapy.Request(link.url, self.getChapter, headers=chapter_headers, cookies=self.cookies)

    def getChapter(self, response):
        introutecd1 = ' '.join([value.strip() for value in response.css(
            '#info p::text, #info a::text').getall() if value.strip()])
        introutced2 = response.css('#intro::text').get('')
        introutced = introutecd1 + '\n' + introutced2
        novel_name = response.css('#info h1::text').get()
        img_url = response.css('#fmimg img::attr(src)').get()
        img_headers = {
            "Host": "www.biquge.se",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
            "Accept": "image/webp,*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Referer": response.url,
            "Cache-Control": "max-age=0"}
        novel_info_url = response.url

        chapter_extrator = LinkExtractor(
            restrict_css=['#list dt:nth-of-type(2) ~ dd'])
        links = chapter_extrator.extract_links(response)
        novel_chapter_urls = [(link.url, link.text) for link in links]

        info = InfoObj()
        info.novel_name = novel_name
        info.novel_introutced = introutced
        info.novel_info_url = novel_info_url
        # info.novel_img_url = img_url
        # info.novel_img_headers = img_headers
        info.novel_chapter_urls = novel_chapter_urls
        self.finalStep(info)

    @classmethod
    def subscribe_updateinfo(cls, response: HtmlResponse) -> InfoObj:
        # print(response.text)
        introutecd1 = ' '.join([value.strip() for value in response.css('#info p::text, #info a::text').getall() if value.strip()])
        introutced2 = response.css('#intro::text').get('')
        introutced = introutecd1 + '\n' + introutced2
        chapter_extrator = LinkExtractor(restrict_css=['#list dt:nth-of-type(2) ~ dd'])
        links = chapter_extrator.extract_links(response)
        novel_chapter_urls = [(link.url, link.text) for link in links]
        info = InfoObj()
        info.novel_introutced = introutced
        info.novel_chapter_urls = novel_chapter_urls
        return info

    @classmethod
    def subscribe_cookies(cls) -> CookieTypes:
        cookies_headers = {
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
        }
        resp = httpx.get('http://www.biquge.se/', headers=cookies_headers)
        print(resp.status_code, resp.cookies)
        return resp.cookies