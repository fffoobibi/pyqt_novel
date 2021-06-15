import scrapy
import os

from os.path import abspath
from urllib.parse import urlparse
from scrapy.linkextractors import LinkExtractor
from scrapy.link import Link
from scrapy.exceptions import DropItem
from ..items import CrawlZhiXuanItem, CrawlZhiXuanImgItem

from PyQt5.QtCore import QObject, pyqtSignal
from .infoobj import InfoObj
from .filesspider import BasicFileSpider

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'http://www.zxcs.me/',
    'Host': 'www.zxcs.me',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'
}

img_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'host',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}


class TianTang():

    name = '小说天堂'
    # allowed_domains = ['www.zxcs.me']
    custom_settings = {'ITEM_PIPELINES': {'crawl_novel.pipelines.ZhiXuanImgPipeline': 1},
                       'DEFAULT_REQUEST_HEADERS': headers,
                       'LOG_FILE': BasicFileSpider.default_log_file,
                       'LOG_LEVEL': 'DEBUG',
                       'LOG_FORMAT': f'[%(name)s--{name}] [%(asctime)s] %(levelname)s: %(message)s',
                       'FILES_STORE': './save',
                       'IMAGES_STORE': f'./save/caches/{name}'}  # 7天内已抓取的不会重复抓取
    q = None  # Manage.Queue
    save_path = None  # 保存目录
    engine_index = 1
    novel_name = ''
    # start_urls = 'http://www.zxcs.me/index.php?keyword='

    @classmethod
    def getImgsPath(cls):
        return cls.custom_settings.get('IMAGES_STORE', '')

    @classmethod
    def getFilesPath(cls):
        return cls.custom_settings.get('FILES_STORE', '')

    @classmethod
    def setFilesPath(cls, path: str):
        cls.custom_settings['FILES_STORE'] = path

    def parse(self, response):
        extractor = LinkExtractor(restrict_xpaths=['//div[@id="pagenavi"]'])
        pagelinks = extractor.extract_links(response)
        if pagelinks:
            header = headers.copy()
            if pagelinks[-1].text == '»':
                last = int(pagelinks[-1].split('=')[-1])
            else:
                last = int(pagelinks[-1].text)
            response.request.meta['page'] = 1
            yield from self._parseSingleResults(response)
            for index in range(2, last + 1):
                url = self.start_urls[0] + '&page=%s' % index
                if index > 2:
                    header['Referer'] = self.start_urls[0] + \
                        '&page=%s' % (index - 1)
                else:
                    header['Referer'] = self.start_urls[0]
                yield scrapy.Request(url, headers=header, callback=self._parseSingleResults, meta={'page': index})
        else:
            response.request.meta['page'] = 1
            yield from self._parseSingleResults(response)

    def _parseSingleResults(self, response):
        extractor = LinkExtractor(restrict_xpaths=['//dl[@id="plist"]/dt'])
        links = extractor.extract_links(response)
        header = headers.copy()
        header['Referer'] = self.start_urls[0]
        page = response.request.meta['page']
        if links:
            i = (page - 1) * 15
            for link in links:
                i += 1
                yield scrapy.Request(url=link.url, headers=header, callback=self.getNovelInfo, meta={'index': i})
            return

    def getNovelInfo(self, response):  # 获取下载页面
        extractor = LinkExtractor(restrict_xpaths=['//p[@class="filetit"]'])
        links = extractor.extract_links(response)
        header = headers.copy()
        header.update(Connection='keep-alive')
        header.pop('Referer')

        index = response.request.meta['index']

        novel_name = response.css(
            '#content > h1:nth-child(1)::text').get(default='').strip()
        _introutced = response.css('#content > p:nth-child(8)::text').getall()
        introutced = '<br>'.join([line.strip() for line in _introutced])
        img_path = response.css('a[id*="ematt"] > img::attr(src)').get()
        save_path = os.path.abspath(self.custom_settings.get('FILES_STORE'))

        img_item = CrawlZhiXuanImgItem()
        img_item['image_urls'] = [img_path]
        img_item['image_name'] = novel_name + '.' + \
            img_path.split('/')[-1].split('.')[-1].strip()
        img_item['save_path'] = os.path.abspath(
            self.custom_settings.get('IMAGES_STORE'))

        infoobj = InfoObj(index, novel_name, '-1mb', self.name, introutced, save_path, novel_img_name=img_item['image_name'],
                          novel_img_save_path=img_item['save_path'])

        infoobj.novel_img_name = img_item['image_name']
        infoobj.novel_img_url = img_path
        infoobj.novel_img_not_found = self.img_not_found
        infoobj.novel_img_headers = img_item['save_path']
        infoobj.novel_info_url = response.request.url
        img_header = img_headers.copy()
        img_header.update(Host=urlparse(img_path).netloc)
        infoobj.novel_img_headers = img_header

        if links:
            yield scrapy.Request(url=links[0].url, headers=header, callback=self.getDownLoadUrl, meta={'title': links[0].text, 'info': infoobj})
        # yield img_item

    def getDownLoadUrl(self, response):  # 获取下载链接
        res = response.xpath('//span[@class="downfile"]//a/@href')
        url = res.get()  # extract_first, getall == extract
        info: InfoObj = response.request.meta['info']
        size = response.css(
            'div[class="plus_l"] > ul li:nth-child(3)::text').get(default='').strip('小说大小 ：')
        info.novel_size = size
        info.novel_url = url
        info.novel_file_type = url.split('/')[-1].split('.')[-1].strip()
        info.novel_img_not_found = self.img_not_found

        if self.save_path:
            info.novel_save_path = self.save_path
        if url:
            item = CrawlZhiXuanItem()
            item['file_urls'] = [url]
            item['file_name'] = response.request.meta['title']
            item['save_path'] = os.path.abspath(
                self.custom_settings.get('FILES_STORE'))
            self.q.put(info)
            # yield item
        return
