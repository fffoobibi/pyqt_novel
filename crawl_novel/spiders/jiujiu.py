import scrapy

from .infoobj import InfoObj
from .filesspider import BasicFileSpider
from urllib.parse import urljoin

headers = {
    'Host': 'www.txt99.org',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language':
    'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.txt99.org/',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://www.txt99.org',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

img_headers = {
    'Host':
    'img.txt99.org',
    'accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding':
    'gzip, deflate, br',
    'accept-language':
    'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control':
    'no-cache',
    'upgrade-insecure-requests':
    '1',
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74'
}


class JiuJiuSpider(BasicFileSpider):

    name = '九九小说'

    use_plugin = True

    novel_name = ''

    def start_requests(self):
        url = r'https://www.txt99.org/search/'
        formdata = {
            'show': 'title,writer',
            'searchkey': f'{self.novel_name}',
            'Submit': ''
        }
        yield scrapy.FormRequest(url, headers=headers, formdata=formdata)

    def parse(self, response):
        first = r'https://www.txt99.org'
        selectors = response.css('div.listbg')
        header = headers.copy()
        header.pop('Content-Type')
        index = -1
        for div_selector in selectors:
            index += 1
            title = div_selector.css('a::attr(title)').get().strip()
            url = first + div_selector.css('a::attr(href)').get()
            img_url = div_selector.css('a > img::attr(src)').get()
            _introutce = div_selector.css('div:nth-child(5)::text').get('')

            _others1 = [
                v.strip() for v in div_selector.css(
                    'div:nth-child(6) small::text').getall()
            ]
            _others2 = [
                v.strip() for v in div_selector.css(
                    'div:nth-child(6) span::text').getall() if v.strip()
            ]
            introutce = _introutce + '<br>' + \
                ' '.join([info + value for info,
                          value in zip(_others1, _others2)])

            inf = InfoObj()
            inf.novel_name = title
            inf.novel_site = self.name
            inf.novel_introutced = introutce.replace('\n', '<br>')
            inf.novel_img_url = img_url
            inf.novel_img_headers = img_headers
            inf.novel_info_url = url
            yield scrapy.Request(url,
                                 headers=header,
                                 callback=self.getDownLoadUrl,
                                 meta={'inf': inf})

    def getDownLoadUrl(self, response):
        inf = response.request.meta['inf']
        download_url = response.css(
            'li.downAddress_li:nth-child(1) > a:nth-child(1)::attr(href)').get(
                '')
        # inf.novel_url = download_url
        inf.novel_size = response.css(
            '.downInfoRowL > li:nth-child(4)::text').get('--').strip()
        inf.novel_file_type = 'txt'

        next_headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            # "referer": "https://www.txt99.org/",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.48"
        }

        yield scrapy.Request(download_url, self.get_url, headers=next_headers, meta={'info': inf })
     
        # self.finalStep(inf)

    def get_url(self, response):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            # "referer": "https://www.caimoge.cc/txt/64158.html",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.48"
        }
        inf = response.meta['info']
        next_url = response.css('div.motion2 a:nth-child(2)::attr(href)').get('')
        next_url = urljoin(response.url, next_url)
        yield scrapy.Request(next_url, self.get_url2, headers=headers, meta={'info': inf})
        # self.finalStep(inf)
    
    def get_url2(self, response):
        info = response.meta['info']
        down_a = response.css('#pdu1::attr(href)').get('')
        info.novel_url = urljoin(response.url, down_a)
        self.finalStep(info)

