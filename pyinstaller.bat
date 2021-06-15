pyinstaller.exe --noconfirm ^
--onedir --console --clean ^
--add-data="fonts;fonts" ^
--add-data="scrapy.cfg;." ^
--add-data="tpls;tpls" ^
--hidden-import="scrapy" ^
--hidden-import="urllib.robotparser" ^
--hidden-import="scrapy.spiderloader" ^
--hidden-import="scrapy.statscollectors" ^
--hidden-import="scrapy.logformatter" ^
--hidden-import="scrapy.dupefilters" ^
--hidden-import="scrapy.squeues" ^
--hidden-import="scrapy.extensions.spiderstate" ^
--hidden-import="scrapy.extensions.corestats" ^
--hidden-import="scrapy.extensions.telnet" ^
--hidden-import="scrapy.extensions.logstats" ^
--hidden-import="scrapy.extensions.memusage" ^
--hidden-import="scrapy.extensions.memdebug" ^
--hidden-import="scrapy.extensions.feedexport" ^
--hidden-import="scrapy.extensions.closespider" ^
--hidden-import="scrapy.extensions.debug" ^
--hidden-import="scrapy.extensions.httpcache" ^
--hidden-import="scrapy.extensions.statsmailer" ^
--hidden-import="scrapy.extensions.throttle" ^
--hidden-import="scrapy.core.engine" ^
--hidden-import="scrapy.core.scraper" ^
--hidden-import="scrapy.core.spidermw" ^
--hidden-import="scrapy.core.scheduler" ^
--hidden-import="scrapy.core.downloader" ^
--hidden-import="scrapy.core.downloader.handlers.http" ^
--hidden-import="scrapy.core.downloader.contextfactory" ^
--hidden-import="scrapy.utils.misc" ^
--hidden-import="scrapy.utils.defer" ^
--hidden-import="scrapy.utils.reactor" ^
--hidden-import="scrapy.downloadermiddlewares.retry" ^
--hidden-import="scrapy.downloadermiddlewares.stats" ^
--hidden-import="scrapy.downloadermiddlewares.cookies" ^
--hidden-import="scrapy.downloadermiddlewares.httpauth" ^
--hidden-import="scrapy.downloadermiddlewares.redirect" ^
--hidden-import="scrapy.downloadermiddlewares.httpcache" ^
--hidden-import="scrapy.downloadermiddlewares.useragent" ^
--hidden-import="scrapy.downloadermiddlewares.httpproxy" ^
--hidden-import="scrapy.downloadermiddlewares.ajaxcrawl" ^
--hidden-import="scrapy.downloadermiddlewares.robotstxt" ^
--hidden-import="scrapy.downloadermiddlewares.decompression" ^
--hidden-import="scrapy.downloadermiddlewares.defaultheaders" ^
--hidden-import="scrapy.downloadermiddlewares.downloadtimeout" ^
--hidden-import="scrapy.downloadermiddlewares.httpcompression" ^
--hidden-import="scrapy.spidermiddlewares.depth" ^
--hidden-import="scrapy.spidermiddlewares.offsite" ^
--hidden-import="scrapy.spidermiddlewares.referer" ^
--hidden-import="scrapy.spidermiddlewares.urllength" ^
--hidden-import="scrapy.spidermiddlewares.httperror" ^
--hidden-import="scrapy.pipelines" ^
--hidden-import="crawl_novel.items" ^
--hidden-import="crawl_novel.settings" ^
--hidden-import="crawl_novel.pipelines" ^
--hidden-import="crawl_novel.middlewares" ^
--hidden-import="crawl_novel.spiders.filesspider" ^
--hidden-import="crawl_novel.spiders.downtasks" ^
--hidden-import="crawl_novel.spiders.infoobj" ^
--hidden-import="crawl_novel.spiders.jiujiu" ^
--hidden-import="crawl_novel.spiders.zhainan" ^
--hidden-import="crawl_novel.spiders.zhixuan" ^
--hidden-import="crawl_novel.spiders.bailin" ^
--exclude-module="ipython" ^
--exclude-module="ipdb" ^
--exclude-module="baidu-aip" ^
--exclude-module="ipython" ^
--icon=.\fonts\search_72px_1296244_easyicon.net.ico appLancher.py 