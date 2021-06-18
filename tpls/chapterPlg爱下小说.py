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
class ChapterTask爱下小说(BasicChapterHandler):

    name = '爱下小说'

    use_plugin = True

    header = {
        "Host": "www.ixiatxt.la",
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language":
        "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "http://www.ixiatxt.com/book/93330/21280072.html",
        "Upgrade-Insecure-Requests": "1"
    }

    def chapter_headers_hook(cls, url_index, url, inf) -> dict:
        if url_index == 0:
            cls.header.pop('Referer')
        else:
            cls.header['Referer'] = inf.novel_chapter_urls[url_index - 1][0]
        return cls.header

    def parse_charpter(cls, url_index, response, chapter) -> tuple:
        soup = BeautifulSoup(response.text, 'lxml')
        title, = soup.select('.txt_cont > h1:nth-child(1)')
        content, = soup.select('#content1')
        return content.stripped_strings, title.string


headers = {
    "Accept":
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding":
    "gzip, deflate",
    "Accept-Language":
    "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Host":
    "www.xiaxs.la",
    "Referer":
    "http://www.ixiatxt.la/",
    "Upgrade-Insecure-Requests":
    "1",
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57"
}


class ChapterSpider爱下小说(BasicChapterSpider):

    name = '爱下小说'

    use_plugin = True

    novel_name = ''

    def start_requests(self):
        url = r'https://www.xiaxs.la/search.php?s=&searchkey=%s' % self.novel_name
        yield scrapy.Request(url, headers=headers)

    def parse(self, response):
        extractor = LinkExtractor(restrict_xpaths=['//div[@class="listBox"]'])
        links = extractor.extract_links(response)
        for link in links:
            header = headers.copy()
            header.update(Referer=link.url)
            yield scrapy.Request(link.url,
                                 self.getReader,
                                 headers=header,
                                 meta={'novel_name': link.text})

    def getReader(self, response):
        extor = LinkExtractor(restrict_xpaths=['//div[@class="showDown"]'])
        links = extor.extract_links(response)
        
        for link in links:
            inf = InfoObj()
            introucted = response.css('div.showInfo *::text').getall()
            introucted = '\n'.join(
                [line.strip() for line in introucted if line.strip()])
            inf.novel_name = response.meta['novel_name']
            inf.novel_introutced = introucted
            inf.novel_info_url = link.url
            yield scrapy.Request(link.url,
                                 self.getChapter,
                                 headers=headers,
                                 meta={'inf': inf})

    def getChapter(self, response):
        inf = response.meta['inf']
        img_url = response.css('.tupian img::attr(src)').get('')
        img_headers = {
            "Host": "www.xiaxs.la",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Accept": "image/webp,*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": response.url,
            "Cache-Control": "max-age=0"
        }
        inf.novel_img_url = img_url
        inf.novel_img_headers = img_headers
        extractor = LinkExtractor(
            restrict_css=['#bodyabd > div:nth-child(9) div.pc_list'])
        links = extractor.extract_links(response)
        for link in links:
            inf.novel_chapter_urls.append([link.url, link.text])
        self.finalStep(inf)
