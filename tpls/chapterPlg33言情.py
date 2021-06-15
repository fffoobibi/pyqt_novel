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

# from filesspider import BasicChapterSpider
# from downtasks import BasicChapterDownTask, register
# from infoobj import InfoObj
from bs4 import BeautifulSoup
from app_runtime import BasicChapterSpider, BasicChapterHandler, register, InfoObj



@register
class ChapterTask33言情(BasicChapterHandler):

    use_plugin = True  # 为True时使用插件, 默认不使用

    name = '33言情'  # 必须定义:唯一名称,和BasicFileSpider子类名称相同

    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Host": "www.33yq.com",
        "Referer": "https://www.33yq.com/read/56877/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66"
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
        chapter, = soup.select('div.zhangjieming > h1')
        content_lines, = soup.select('#content')
        return content_lines.stripped_strings, chapter.string


class ChapterSpider33言情(BasicChapterSpider):

    name = '33言情'  # 必须定义:唯一名称,和BasicChapterDownTask子类名称相同

    novel_name = ''  # 待搜索的小说名称

    use_plugin = True  # 为True时使用插件, 默认不使用

    start_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "max-age=0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "www.33yq.com",
        "Origin": "https://www.33yq.com",
        "Referer": "https://www.33yq.com/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66"
    }

    link_headers = {
        "Host": "www.33yq.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }

    def start_requests(self):
        url = 'https://www.33yq.com/search.html'
        form_data = {
            "s": "articlename",
            "searchkey": self.novel_name,
            "Submit": ""}
        yield scrapy.FormRequest(url, headers=self.start_headers, formdata=form_data)

    def parse(self, response):
        next_page_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Host": "www.33yq.com",
            "Referer": "https://www.33yq.com/search/8056/1.html",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66"
        }
        yield from self._parseSinglePage(response)
        links = LinkExtractor(
            restrict_css=['#pagelink']).extract_links(response)

        for index, link in enumerate(links, 0):
            if index == 0:
                next_page_headers['Referer'] = response.url
            else:
                next_page_headers['Referer'] = links[index - 1].url
            yield scrapy.Request(link.url, self._parseSinglePage)

    def _parseSinglePage(self, response):
        next_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Host": "www.33yq.com",
            "Referer": response.url,
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66"
        }
        results = response.css('#alist #alistbox')
        for result in results:
            pic_url = result.css('div.pic a::attr(href)').get()
            novel_name = self.join_striped(result.css(
                'div.info > div.title *::text'), join_sep='')
            next_url = 'https://www.33yq.com' + \
                result.css('div.info > div.title a::attr(href)').get()
            latest_chapter = self.join_striped(
                result.css('div.info > div.sys *::text'))
            yield scrapy.Request(next_url, self.getChapter, headers=next_headers, meta={'latest_chapter': latest_chapter, 'novel_name': novel_name})

    def getChapter(self, response):
        '''
        ...
        results = [(url, chapter_name), ...]
        inf.novel_chapter_urls = results
        self.finalStep(inf)

        '''
        update_time = self.join_striped(
            response.css('#info > p:nth-child(5)::text'))
        latest_chapter = self.join_striped(
            response.css('#info > p:nth-child(6) *::text'))
        novel_introduce = response.css(
            '#intro > p.introtxt::text').get('').strip()
        introduce = update_time + '\n' + latest_chapter + '\n' + novel_introduce
        links = LinkExtractor(restrict_css=(
            '#list > dl > dd')).extract_links(response)
        info = InfoObj()
        info.novel_name = response.meta['novel_name']
        info.novel_chapter_urls = [(link.url, link.text) for link in links]
        info.novel_introutced = introduce
        info.novel_info_url = response.url
        info.novel_subs_headers = self.link_headers
        self.finalStep(info)

    @classmethod
    def subscribe_updateinfo(cls, response: HtmlResponse) -> InfoObj:
        '''
        response: scrapy.http.HTMLResponse
        return: 默认返回None,无法订阅; 返回 InfoObj实现订阅功能
        >>>

        introutecd = response.css('#intro::text').get()
        links = LinkExtractor(restrict_css=['#idlist']).extract_links(response)
        inf = InfoObj()
        inf.novel_chapter_urls = [(link.url, link.text) for link in links]
        inf.novel_introutced = introutecd
        return inf

        '''
        update_time = cls.join_striped(
            response.css('#info > p:nth-child(5)::text'))
        latest_chapter = cls.join_striped(
            response.css('#info > p:nth-child(6) *::text'))
        novel_introduce = response.css(
            '#intro > p.introtxt::text').get('').strip()
        introduce = update_time + '\n' + latest_chapter + '\n' + novel_introduce
        links = LinkExtractor(restrict_css=(
            '#list > dl > dd')).extract_links(response)
        info = InfoObj()
        info.novel_chapter_urls = [(link.url, link.text) for link in links]
        info.novel_introutced = introduce
        return info
