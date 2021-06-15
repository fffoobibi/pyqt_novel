import scrapy

from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse

from .infoobj import InfoObj
from .filesspider import BasicFileSpider


headers = {
    "Host": "www.zntxt.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "http://www.zntxt.com",
    "Connection": "keep-alive",
    "Referer": "http://www.zntxt.com/",
    "Upgrade-Insecure-Requests": "1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache"
}

img_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "img.xqishu.com",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74"
}


class ZnSpider(BasicFileSpider):

    name = '宅男小说'

    use_plugin = True

    # custom_settings = {'ITEM_PIPELINES': {'crawl_novel.pipelines.ZNPipeline': 1},
    #                    'DEFAULT_REQUEST_HEADERS': headers,
    #                    'LOG_FILE': BasicFileSpider.default_log_file,
    #                 #    'LOG_FORMAT': f'[%(name)s--{name}] [%(asctime)s] %(levelname)s: %(message)s',
    #                    'LOG_LEVEL': 'DEBUG',
    #                    'FILES_STORE': './save',
    #                    'IMAGES_STORE': f'./save/caches/{name}'}  # 7天内已抓取的不会重复抓取

    novel_name = '火影'


    def start_requests(self):
        url = r'http://www.zntxt.com/e/search/index.php'
        formdata = {"show": "title,softsay,softwriter",
                    "keyboard": self.novel_name,
                    "Submit22": "",
                    "tbname": "download",
                    "tempid": "1"}
        yield scrapy.FormRequest(url, formdata=formdata)

    def parse(self, response):
        next_headers = headers.copy()

        next_headers.pop('Origin')
        next_headers.pop('Content-Type')

        response.meta['page'] = 0

        yield from self.parseSingleResults(response)

        extrator = LinkExtractor(
            restrict_css=['.searchlist_l_box tr:nth-child(2)'])
        links = extrator.extract_links(response)
        if links:
            end_url_num, site = links[-1].url.split('/')[-1].split('-')[1:]
            for i in range(1, int(end_url_num) + 1):
                next_url = f'http://www.zntxt.com/search-{i}-{site}'
                yield scrapy.Request(next_url, headers=next_headers, callback=self.parseSingleResults, meta={'page': i})

    def parseSingleResults(self, response):
        refer_url = response.request.url
        header = headers.copy()
        header.update(Referer=refer_url)
        header.pop('Origin')
        header.pop('Content-Type')
        tables = response.css('table.xsinfo')
        for sele in tables:
            url = 'http://www.zntxt.com' + \
                sele.css(
                    'tr:nth-child(1) a:nth-child(1)::attr(href)').get().strip()
            novel_name = sele.css(
                'tr:nth-child(1) a:nth-child(1)::text').get().strip()
            yield scrapy.Request(url, headers=header, callback=self.getDownLoadPage, meta={'novel_name': novel_name})

    def getDownLoadPage(self, response):
        refer_url = response.request.url
        header = headers.copy()
        header.update(Referer=refer_url)
        header.pop('Origin')
        header.pop('Content-Type')

        titles = response.css('.nrlist dd.db *::text').getall()
        titles_ = '\n'.join([titles[0]+titles[1], titles[2]+titles[3], titles[4] +
                             titles[5], titles[6], titles[7]+titles[8], titles[9]+titles[10]])
        novels = response.css('.like_title_txt *::text').get().strip() + ':'
        introutced_ = ''.join([v for v in response.css('.cont *::text').getall() if v.strip()])
        introutce = titles_  + '<br>' + novels + introutced_
        image_url = response.css('.pics3::attr(src)').get().strip()
        novel_name = response.meta['novel_name']
        img_header = img_headers.copy()
        img_header.update(Host=urlparse(image_url).netloc)
        inf = InfoObj()
        inf.novel_size = response.css(
            'dd.db:nth-child(7) > span:nth-child(1)::text').get().strip()
        inf.novel_name = novel_name
        inf.novel_site = self.name
        inf.novel_introutced = introutce
        inf.novel_img_url = image_url
        inf.novel_img_headers = img_header
        inf.novel_info_url = response.request.url
        page = 'http://www.zntxt.com' + \
            response.css(
                '.downlinks  li:nth-child(1) a::attr(href)').get().strip()
        return scrapy.Request(page, headers=header, callback=self.getDownLoadUrl, meta={'inf': inf})

    def getDownLoadUrl(self, response):
        inf = response.meta['inf']
        down_url = response.css(
            '.downlist li:nth-child(1) a::attr(href)').get()
        inf.novel_url = down_url
        inf.novel_file_type = inf.novel_url.split(
            '/')[-1].split('.')[-1].strip()
        inf.novel_img_not_found = self.img_not_found
        self.finalStep(inf)
