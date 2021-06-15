import scrapy

from urllib.parse import urlparse
from scrapy.linkextractors import LinkExtractor

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


class ZhiXuanSpider(BasicFileSpider):

    name = '知轩藏书'

    use_plugin = True 

    novel_name = ''

    def start_requests(self):
        url = 'http://www.zxcs.me/index.php?keyword=%s'% self.novel_name
        yield scrapy.Request(url, headers=headers)

    def parse(self, response):
        start_url = r'http://www.zxcs.me/index.php?keyword=%s' % self.novel_name
        extractor = scrapy.linkextractors.LinkExtractor(restrict_xpaths=['//div[@id="pagenavi"]'])
        pagelinks = extractor.extract_links(response)
        response.request.meta['page'] = 1
        yield from self._parseSingleResults(response)
        if pagelinks:
            header = headers.copy()
            if pagelinks[-1].text == '»':
                last = int(pagelinks[-1].split('=')[-1])
            else:
                last = int(pagelinks[-1].text)
            for index in range(2, last + 1):
                url = start_url + '&page=%s' % index
                if index > 2:
                    header['Referer'] = start_url + \
                        '&page=%s' % (index - 1)
                else:
                    header['Referer'] = start_url
                yield scrapy.Request(url, headers=header, callback=self._parseSingleResults, meta={'page': index})
    

    def _parseSingleResults(self, response):
        extractor = scrapy.linkextractors.LinkExtractor(restrict_xpaths=['//dl[@id="plist"]/dt'])
        links = extractor.extract_links(response)
        header = headers.copy()
        header['Referer'] = 'http://www.zxcs.me/index.php?keyword=%s'% self.novel_name
        page = response.request.meta['page']
        if links:
            i = (page - 1) * 15
            for link in links:
                i += 1
                yield scrapy.Request(link.url, headers=header, callback=self.getNovelInfo, meta={'index': i})

    def getNovelInfo(self, response):  # 获取下载页面
        extractor = scrapy.linkextractors.LinkExtractor(restrict_xpaths=['//p[@class="filetit"]'])
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

        img_header = img_headers.copy()
        img_header.update(Host=urlparse(img_path).netloc)

        infoobj = InfoObj()
        infoobj.novel_name = novel_name
        infoobj.novel_site = self.name
        infoobj.novel_introutced = introutced
        infoobj.novel_img_url = img_path
        infoobj.novel_img_headers = img_header
        infoobj.novel_info_url = response.request.url

        if links:
            return scrapy.Request(links[0].url, headers=header, callback=self.getDownLoadUrl, meta={'title': links[0].text, 'info': infoobj})

    def getDownLoadUrl(self, response):  # 获取下载链接
        res = response.xpath('//span[@class="downfile"]//a/@href')
        url = res.get()  # extract_first, getall == extract
        info: InfoObj = response.request.meta['info']
        size = response.css(
            'div[class="plus_l"] > ul li:nth-child(3)::text').get(default='').strip('小说大小 ：')
        info.novel_size = size
        info.novel_url = url # 必须定义
        info.novel_file_type = url.split('/')[-1].split('.')[-1].strip() # 必须定义
        info.novel_img_not_found = self.img_not_found
        self.finalStep(info)
