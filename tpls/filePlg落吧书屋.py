'''
说明

插件名称必须已plugin开头的py文件,比如plugin1.py, plugin2.py
插件必须定义两个类: BasicFileDownTask为下载小说的类, BasicFileSpider为搜索小说的scrapy.Spider子类

BasicFileSpider子类中必须定义InfoObj对象,根据爬取的网站规则定义好以下字段内容,自定义的插件才能成功使用

inf = InfoObj()
inf.novel_name = '诛仙'               # 必须定义,搜索结果的小说名称
inf.novel_site = '知轩藏书'           # 必须定义,且有且为spider.name
inf.novel_introutced = '...'         # 小说详情介绍,可以不定义
inf.novel_img_url = 'http://...'     # 可以不定义,小说封面url, 如果为'',则不下载小说封面
inf.novel_img_headers = {}           # 小说封面下载headers
inf.novel_info_url = 'http://...'    # 可以不定义,小说详情url,可以不定义

inf.novel_url = download_url         #必须定义,小说下载url,否则无法下载
inf.novel_file_type = 'txt'          # 必须定义,小说下载文件格式,比如txt,rar
inf.novel_size = '2MB'               # 小说大小,可以不定义,默认显示'--'
self.finalStep(inf)                 # 开始爬取,当定义好inf所需要的字段,必须调用,否则插件无法正常运行

'''

import scrapy
from urllib.parse import urlparse
from app_runtime import BasicFileSpider, BasicFileHandler, register, InfoObj

@register
class FileTask落吧书屋(BasicFileHandler):

    use_plugin = True  # 为True时使用插件, 默认不使用

    name = '落吧书屋'  # 必须定义:唯一名称,和BasicFileSpider子类名称相同

    header = {
    "Host": "www.luo8.com",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    }  # 小说下载headers

    def file_headers_hook(cls, inf):  # 设置下载header的钩子函数
        netloc = urlparse(inf.novel_url).netloc
        cls.header['Host'] = netloc
        return cls.header


class FileSpider落吧书屋(BasicFileSpider):

    headers = {
        "Host": "www.luo8.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://www.luo8.com",
        "Referer": "http://www.luo8.com/",
        "Upgrade-Insecure-Requests": "1"
    }

    img_headers = {

        "Host": "www.luo8.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "image/webp,*/*",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Referer": "http://www.luo8.com/dushi/79703/",
        "Cache-Control": "max-age=0"
    }  # 小说封面图片下载headrs

    name = '落吧书屋'  # 必须定义:唯一名称,和BasicFileDownTask子类名称相同

    novel_name = ''  # 待搜索的小说名称

    use_plugin = True  # 为True时使用插件, 默认不使用

    custom_settings = {'RETRY_HTTP_CODES': [500, 502, 503, 504, 400, 403, 404, 408],
                       'RETRY_ENABLED': True}

    def start_requests(self):  # scrapy搜索开始
        url = 'http://www.luo8.com/search.html'
        formdata = {'searchkey': self.novel_name}
        yield scrapy.FormRequest(url, headers=self.headers, formdata=formdata)

    def parse(self, response):  # 回调函数
        yield from self.parseSinglePage(response)
        total_pages = response.css('.mainNextPage .last::attr(href)').get()
        if total_pages:
            next_headers = {
                "Host": "www.luo8.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Accept-Encoding": "gzip, deflate",
                "Referer": "",
                "Upgrade-Insecure-Requests": "1"}
            last = total_pages.split('/')[-1]
            url_base = '/'.join(total_pages.split('/')[:-1])
            for i in range(2, int(last) + 1):
                url = url_base + f'/{i}'
                refer_url = url_base + f'/{i-1}'
                next_headers['Referer'] = refer_url
                yield scrapy.Request(url, self.parseSinglePage, headers=next_headers, cb_kwargs={'referer': refer_url})

    def parseSinglePage(self, response, referer='http://www.luo8.com/search.html'):
        next_url_headers = self.headers.copy()
        next_url_headers.pop('Origin')
        next_url_headers.pop('Content-Type')
        next_url_headers['Referer'] = referer
        next_url_headers['Cache-Control'] = "max-age=0"
        novel_names = response.css('div.searchTopic a::text').getall()
        next_urls = response.css('div.searchTopic a::attr(href)').getall()
        for novel_name, url in zip(novel_names, next_urls):
            yield scrapy.Request(url, self.parseInfosUrl, headers=next_url_headers, meta={'novel_name': novel_name})

    def parseInfosUrl(self, response):
        get_down_url_headers = self.headers.copy()
        get_down_url_headers.pop('Origin')
        get_down_url_headers.pop('Content-Type')
        get_down_url_headers['Referer'] = response.request.url
        get_down_url_headers['Cache-Control'] = "max-age=0"
        novel_name = response.meta['novel_name']
        i1 = [line.strip() for line in response.css(
            'dd.downInfoRowL *::text').getall() if line.strip()]
        i1 = self.split_sequence(i1, 2)
        file_size = i1[4][-1].replace('解压后',
                                      '').replace('（', '').replace('）', '')
        i1 = '<br>'.join([''.join(ls) for ls in i1])
        introucted = i1 + '<br>' + \
            '<br>'.join([line.strip() for line in response.css(
                '#mainSoftIntro *::text').getall()])
        image_url = response.css(
            'dd.downInfoRowL img::attr(src)').get().strip()
        get_down_url = response.css(
            'li.downAddress_li a::attr(href)').get().strip()

        img_header = self.img_headers.copy()
        img_header['Referer'] = response.request.url
        inf = InfoObj()
        inf.novel_name = response.meta['novel_name'].replace(
            '\\', '-').replace('/', '-')
        inf.novel_site = self.name
        inf.novel_size = file_size
        inf.novel_introutced = introucted
        inf.novel_img_url = image_url
        inf.novel_img_headers = img_header
        inf.novel_info_url = response.request.url
        yield scrapy.Request(get_down_url, self.getDownLoadUrl, headers=get_down_url_headers, meta={'inf': inf})

    def getDownLoadUrl(self, response):  # 回调函数
        inf = response.meta['inf']
        down_url = response.css(
            'a.strong:nth-child(5)::attr(href)').get().strip()
        inf.novel_file_type = 'rar'
        inf.novel_url = down_url
        self.finalStep(inf)
