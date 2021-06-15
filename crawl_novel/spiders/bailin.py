import scrapy
import requests
import re
from scrapy.http import Response
Response.url
from urllib.parse import urlparse

from .infoobj import InfoObj
from .filesspider import BasicFileSpider


headers = {
    "Host": "www.txt80.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "http://www.txt80.com",
    "Connection": "keep-alive",
    "Referer": "http://www.txt80.com",
    "Upgrade-Insecure-Requests": "1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}

image_headers = {
    "Host": "img.txt8080.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Accept": "image/webp,*/*",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.txt80.com/danmei/txt14018.html",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache"
}


class EightSpider(BasicFileSpider):

    name = '八零小说'

    use_plugin = True
    
    novel_name = '诛仙'

    def start_requests(self):
        url = r'http://www.txt80.com/e/search/index.php'
        formdata = {
            "tbname": "download",
            "tempid": "1",
            "keyboard": self.novel_name,
            "show": "title,softsay,softwriter",
            "Submit22": "搜索"
        }
        resp = requests.post(url, headers=headers, data=formdata, allow_redirects=False)
        header = headers.copy()
        header.pop('Content-Type')
        header.pop('Origin')
        new_url = r'http://www.txt80.com/e/search/' + resp.headers['location']
        yield scrapy.Request(new_url, headers=header)

    def parse(self, response):
        next_headers = headers.copy()
        next_headers.pop('Origin')
        next_headers.pop('Content-Type')
        response.meta['page'] = 0

        yield from self.parseSingleResults(response)

        next_pages = response.css(
            '.searchlist_l_box tr:nth-child(2) a::attr(href)').getall()
        if next_pages:
            f, end_url_num, e = re.findall(
                r'(.*page=)(\d+)(&searchid=.*)', next_pages[-1])[-1]
            for i in range(1, int(end_url_num) + 1):
                next_url = f'http://www.txt80.com/' + f + str(i) + e
                yield scrapy.Request(next_url, callback=self.parseSingleResults, headers=next_headers)

    def parseSingleResults(self, response):
        header = headers.copy()
        header.pop('Origin')
        header.pop('Content-Type')
        header.pop('Referer')
        tables = response.css('div.slist')
        i = 0
        for sele in tables:
            i += 1
            url = 'http://www.txt80.com' + \
                sele.css('div.info h4 a:nth-child(1)::attr(href)').get().strip()
            novel_name = sele.css(
                'div.info h4 a:nth-child(1)::text').get().strip()
            infos = sele.css('div.info p.xm')
            v = []
            v1 = ''.join(infos[0].css('*::text').getall())
            v2 = ''.join([line.strip() for line in sele.css(
                'div.info  p:nth-child(4) *::text').getall() if line.strip()])

            inf = InfoObj()
            inf.novel_name = novel_name
            inf.novel_url = url
            inf.novel_introutced = v1, v2
            yield scrapy.Request(url, headers=header, callback=self.getDownLoadPage, meta={'inf': inf})

    def getDownLoadPage(self, response):
        header = headers.copy()
        header.pop('Origin')
        header.pop('Content-Type')
        header.pop('Referer')

        introutce = ''.join([line.strip() for line in response.css(
            '.cont *::text').getall() if line.strip()])
        down_url = r'http://www.txt80.com/' + \
            response.css(
                '.downlinks li:nth-child(1) a:nth-child(1)::attr(href)').get('').strip()
        image_url = response.css('.pics3::attr(src)').get('').strip()

        inf = response.meta['inf']
        v1, v2 = inf.novel_introutced

        inf.novel_introutced = v1 + '<br>' + introutce + '<br>' + v2

        inf.novel_size = response.css(
            'dd.db:nth-child(8) span::text').get('').strip()

        image_header = image_headers.copy()
        image_header.update(Host=urlparse(image_url).netloc)
        image_header.update(Referer=response.request.url)

        inf.novel_img_headers = image_header
        inf.novel_img_url = image_url
        inf.novel_info_url = response.request.url
        inf.novel_img_not_found = self.img_not_found

        inf.novel_meta = {'IMG_Referer': response.request.url}

        return scrapy.Request(down_url, self.getDownLoadUrl, headers=header, meta={'inf': inf})

    def getDownLoadUrl(self, response):
        inf = response.meta['inf']
        down_url = response.css(
            '.downlist a:nth-child(1)::attr(href)').get('').strip()
        down_url = down_url.replace('https:', 'http:')
        inf.novel_url = down_url
        inf.novel_file_type = down_url.split('/')[-1].split('.')[-1].strip()
        inf.novel_site = self.name
        inf.novel_file_type = inf.novel_url.split(
            '/')[-1].split('.')[-1].strip()

        self.finalStep(inf)
