# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from urllib.parse import urlparse
import scrapy
import re
import os
import rarfile


class CrawlBaiduPipeline:
    def process_item(self, item, spider):
        print('done: ', item['name'])
        return item


class CrawlDingdianPipeline:
    # 顶点小说
    def _convert(self, chinese_digits, encoding="utf-8"):
        # if isinstance (chinese_digits, str):
        #     chinese_digits = chinese_digits.decode(encoding)

        chs_arabic_map = {u'零': 0, u'一': 1, u'二': 2, u'三': 3, u'四': 4,
                          u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9,
                          u'十': 10, u'百': 100, u'千': 10 ** 3, u'万': 10 ** 4,
                          u'〇': 0, u'壹': 1, u'贰': 2, u'叁': 3, u'肆': 4,
                          u'伍': 5, u'陆': 6, u'柒': 7, u'捌': 8, u'玖': 9,
                          u'拾': 10, u'佰': 100, u'仟': 10 ** 3, u'萬': 10 ** 4,
                          u'亿': 10 ** 8, u'億': 10 ** 8, u'幺': 1,
                          u'０': 0, u'１': 1, u'２': 2, u'３': 3, u'４': 4,
                          u'５': 5, u'６': 6, u'７': 7, u'８': 8, u'９': 9}
        if not chinese_digits:
            result = 0
            tmp = 0
            hnd_mln = 0
            for count in range(len(chinese_digits)):
                curr_char = chinese_digits[count]
                curr_digit = chs_arabic_map.get(curr_char, None)

                if curr_digit == 10 ** 8:
                    result = result + tmp
                    result = result * curr_digit
                    # get result before 「亿」 and store it into hnd_mln
                    # reset `result`
                    hnd_mln = hnd_mln * 10 ** 8 + result
                    result = 0
                    tmp = 0
                # meet 「万」 or 「萬」
                elif curr_digit == 10 ** 4:
                    result = result + tmp
                    result = result * curr_digit
                    tmp = 0
                # meet 「十」, 「百」, 「千」 or their traditional version
                elif curr_digit >= 10:
                    tmp = 1 if tmp == 0 else tmp
                    result = result + curr_digit * tmp
                    tmp = 0
                # meet single digit
                elif curr_digit is not None:
                    tmp = tmp * 10 + curr_digit
                else:
                    return result
            result = result + tmp
            result = result + hnd_mln
            return result
        return '0'

    def findNumber(self, msg):
        values = re.findall(r'第(.*?)(?:章|集)', msg)
        if values:
            number = values[0].strip()
            try:
                value = int(number)
            except:
                value = self._convert(number)
            return value
        return 0

    def __init__(self):
        self.item_list = []

    def process_item(self, item, spider):
        self.item_list.append(item)
        print('donwload: ', item['chapter'])
        return item

    def close_spider(self, spider):
        self.item_list.sort(key=lambda item: int(item['index']))
        novel = f'{self.item_list[0]["name"]}.txt'
        with open(novel, 'a+', encoding='gbk', errors='ignore') as file:
            for item in self.item_list:
                lines = item['content']
                chapter = item['chapter']
                file.write(chapter.strip())
                file.write('\n')
                file.writelines([line.strip() + '\n' for line in lines])
                print('write:', chapter)
        self.item_list.clear()


class ZhiXuanPipeline(FilesPipeline):  # 知轩藏书文件下载

    # 知轩藏书
    def get_media_requests(self, item, info):  # 发送下载请求
        url = item['file_urls'][0]
        host = re.findall(r'https?://(.*?)/', url)[0]
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
                  'Connection': 'keep-alive',
                  'Upgrade-Insecure-Requests': '1',
                  'Host': host}
        save_name = item['file_name'] + '.' + url.split('.')[-1]
        print('url: ', url, header)
        yield scrapy.Request(url, headers=header, meta={'save_name': save_name})

    def file_path(self, request, response=None, info=None, *, item=None):  # 保存的文件名
        name = request.meta['save_name']
        return name

    def item_completed(self, results, item, info):  # 下载后处理
        # print('item_completed', item)
        # print('results: ', results)
        # print('item: ', item)
        # print('info: ', info)
        files_paths = [os.path.join(item['save_path'], x['path'])
                       for ok, x in results if ok]
        if not files_paths:
            raise DropItem(f'{item["file_name"]}下载失败')
        else:
            pass
            # for file in files_paths:
            #     if file.lower().endswith('rar'):
            #         rar = rarfile.RarFile(file)
        return item


class CrawlIxiaPipeline:
    pass

############################################################################################################


class BasicFileSpiderImagsPipeline(ImagesPipeline):
    headers = {}

    def headersHook(self, item) -> dict:
        return self.headers

    def get_media_requests(self, item, info):
        url = item['image_urls'][0]
        save_name = item['image_name']
        header = self.headersHook(item)
        if os.path.exists(os.path.join(item['save_path'], save_name)):
            return
        else:
            yield scrapy.Request(url, headers=header, meta={'save_name': save_name})

    def file_path(self, request, response=None, info=None, *, item=None):
        name = request.meta['save_name']
        return name

    # def item_completed(self, results, item, info):  # 下载后处理
    #     files_paths = [os.path.join(item['save_path'], x['path'])
    #                    for ok, x in results if ok]
    #     inf = item['info']
    #     if not files_paths:
    #         # inf.novel_img_down_ok = False # 图片下载失败
    #         print('下载成功')
    #     else:
    #         print('下载失败')
    #         # inf.novel_img_down_ok = True # 图片下载成功
    #     return item


class ZhiXuanImgPipeline(BasicFileSpiderImagsPipeline):  # 知轩藏书图片下载
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'host',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

    def headersHook(self, item):
        url = item['image_urls'][0]
        host = urlparse(url).netloc  # 域名服务器
        self.headers['Host'] = host
        return self.headers


class JiuJiuImgPipeLine(BasicFileSpiderImagsPipeline):  # 九九小说封面图片下载
    headers = {
        'Host': 'img.txt99.org',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74'
    }


class ZNPipeline(BasicFileSpiderImagsPipeline):
    headers = {
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

    def headersHook(self, item):
        url = item['image_urls'][0]
        host = urlparse(url).netloc
        self.headers.update(Host=host)
        return self.headers


class EightPipeline(BasicFileSpiderImagsPipeline):
    headers = {
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

    def get_media_requests(self, item, info):
        url = item['image_urls'][0]
        host = urlparse(url).netloc
        header = self.headers.copy()
        header.update(Host=host)
        header.update(Referer=item['info'])
        save_name = item['image_name']
        if os.path.exists(os.path.join(item['save_path'], save_name)):
            return
        else:
            print('get pic ...', url)
            yield scrapy.Request(url, headers=header, meta={'save_name': save_name})
