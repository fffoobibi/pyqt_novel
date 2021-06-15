# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlBaiduItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()


class CrawlDingdianItem(scrapy.Item):

    chapter = scrapy.Field()
    content = scrapy.Field()
    name = scrapy.Field()
    index = scrapy.Field()


class CrawlZhiXuanItem(scrapy.Item):
    
    files = scrapy.Field()
    file_urls = scrapy.Field()

    save_path = scrapy.Field()
    file_name = scrapy.Field()
    novel_info = scrapy.Field()


class CrawlZhiXuanImgItem(scrapy.Item):

    image_urls = scrapy.Field()
    images = scrapy.Field()

    image_name = scrapy.Field()
    save_path = scrapy.Field()
    info = scrapy.Field()

class ImageItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()

    image_name = scrapy.Field()
    save_path = scrapy.Field()
    info = scrapy.Field()

class CrawlIxiaItem(scrapy.Item):
    
    index = scrapy.Field()
    chapter = scrapy.Field()
    content = scrapy.Field()
    novel_name = scrapy.Field()
