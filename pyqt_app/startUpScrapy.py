import logging
import traceback

from contextlib import contextmanager
from crawl_novel import BasicFileSpider
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.settings import Settings
from multiprocessing import Process, Queue
from threading import Thread
from typing import Callable
from .log_supports import _MessageHandler

__all__ = ['startBothByOrder']

# def __searchtBoth(name, q, save_path):  # 并发执行爬虫
#     url = 'http://www.zxcs.me/index.php?keyword=%s' % name
#     process = CrawlerProcess(get_project_settings())
#     process.crawl(ZhiXuanSpider, start_urls=[url], q=q, save_path=save_path)
#     process.crawl(JiuJiuSpider, novel_name=name, q=q, save_path=save_path)
#     process.start()
#     q.put('search_done')


# def startBoth(name, q, save_path):
#     removeLog()
#     process = Process(target=__searchtBoth, args=(
#         name, q, save_path), name='Both')
#     process.daemon = True
#     process.start()


# 顺序执行爬虫, crawlrunner 需手动配置log
def __searchByOrder(name: str, q: Queue, save_path: str, engins: dict, global_settings: Settings, start_log: bool = False, call_handler: Callable[[], logging.Handler] = None) -> None:

    def get_scrapy_logs(handler: _MessageHandler, process_q: Queue) -> None:
        if handler:
            while True:
                value = handler.stream_get()
                process_q.put(value)

    def qt_log_filter(record):
        if record.name in ('scrapy.extensions.httpcache', 'scrapy.crawler'):
            return False
        if record.name.startswith('scrapy'):
            crawler = record.__dict__.get('crawler', None)
            spider = record.__dict__.get('spider', None)
            spider_name = crawler.spidercls.name if crawler else '--'
            spider_name = spider.name if spider else spider_name
            record.spidername = spider_name
        else:
            record.spidername = '--'
        return True

    @contextmanager
    def scrapy_qt_logging(qt_handler: _MessageHandler, filter: Callable):
        try:
            configure_logging()
            logger = logging.getLogger()
            for handler in logger.handlers:
                logger.removeHandler(handler)
            logger.setLevel(logging.NOTSET)
            if qt_handler:
                formater = logging.Formatter('[%(name)s] [%(asctime)s] [%(spidername)s] %(levelname)s: %(message)s')
                qt_handler.setFormatter(formater)
                qt_handler.addFilter(filter)
                logger.addHandler(qt_handler)
            yield
        except: 
            traceback.print_exc()
        finally:
            if qt_handler:
                logger.removeHandler(qt_handler)

    @defer.inlineCallbacks
    def crawl(name: str, q: Queue, save_path: str, engins: dict, global_settings: Settings) -> None:
        runner = CrawlerRunner(global_settings) 
        for spider_name, state in engins.items():
            if state:
                spider_cls = BasicFileSpider.getSPiderByName(spider_name)
                yield runner.crawl(spider_cls, novel_name=name, q=q, save_path=save_path)
        reactor.stop()
        q.put(True)

    handler = call_handler() if call_handler else None
    with scrapy_qt_logging(handler, qt_log_filter):
        if start_log:
            th = Thread(target=get_scrapy_logs, args=(handler, q), daemon=True)
            th.start()
        crawl(name, q, save_path, engins, global_settings)
        reactor.run()  # 阻塞的

def startBothByOrder(name: str, q: Queue, save_path: str, engins: dict, global_settings: Settings, start_log: bool = False, call_handler: Callable = None) -> None:
    process = Process(target=__searchByOrder, args=(
        name, q, save_path, engins, global_settings, start_log, call_handler), name='BothByOrder')
    process.daemon = True
    process.start()
