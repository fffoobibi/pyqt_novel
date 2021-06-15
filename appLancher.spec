# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['appLancher.py'],
             pathex=['C:\\Users\\fqk12\\Desktop\\pyqt_novel'],
             binaries=[],
             datas=[('fonts', 'fonts'), ('scrapy.cfg', '.'), ('tpls', 'tpls')],
             hiddenimports=['scrapy', 'urllib.robotparser', 'scrapy.spiderloader', 'scrapy.statscollectors', 'scrapy.logformatter', 'scrapy.dupefilters', 'scrapy.squeues', 'scrapy.extensions.spiderstate', 'scrapy.extensions.corestats', 'scrapy.extensions.telnet', 'scrapy.extensions.logstats', 'scrapy.extensions.memusage', 'scrapy.extensions.memdebug', 'scrapy.extensions.feedexport', 'scrapy.extensions.closespider', 'scrapy.extensions.debug', 'scrapy.extensions.httpcache', 'scrapy.extensions.statsmailer', 'scrapy.extensions.throttle', 'scrapy.core.engine', 'scrapy.core.scraper', 'scrapy.core.spidermw', 'scrapy.core.scheduler', 'scrapy.core.downloader', 'scrapy.core.downloader.handlers.http', 'scrapy.core.downloader.contextfactory', 'scrapy.utils.misc', 'scrapy.utils.defer', 'scrapy.utils.reactor', 'scrapy.downloadermiddlewares.retry', 'scrapy.downloadermiddlewares.stats', 'scrapy.downloadermiddlewares.cookies', 'scrapy.downloadermiddlewares.httpauth', 'scrapy.downloadermiddlewares.redirect', 'scrapy.downloadermiddlewares.httpcache', 'scrapy.downloadermiddlewares.useragent', 'scrapy.downloadermiddlewares.httpproxy', 'scrapy.downloadermiddlewares.ajaxcrawl', 'scrapy.downloadermiddlewares.robotstxt', 'scrapy.downloadermiddlewares.decompression', 'scrapy.downloadermiddlewares.defaultheaders', 'scrapy.downloadermiddlewares.downloadtimeout', 'scrapy.downloadermiddlewares.httpcompression', 'scrapy.spidermiddlewares.depth', 'scrapy.spidermiddlewares.offsite', 'scrapy.spidermiddlewares.referer', 'scrapy.spidermiddlewares.urllength', 'scrapy.spidermiddlewares.httperror', 'scrapy.pipelines', 'crawl_novel.items', 'crawl_novel.settings', 'crawl_novel.pipelines', 'crawl_novel.middlewares', 'crawl_novel.spiders.filesspider', 'crawl_novel.spiders.downtasks', 'crawl_novel.spiders.infoobj', 'crawl_novel.spiders.jiujiu', 'crawl_novel.spiders.zhainan', 'crawl_novel.spiders.zhixuan', 'crawl_novel.spiders.bailin'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['ipython', 'ipdb', 'baidu-aip', 'ipython'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='appLancher',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='search_72px_1296244_easyicon.net.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='appLancher')
