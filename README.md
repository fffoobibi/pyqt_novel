# pyqt_novel

#### 介绍
pyqt5编写的集阅读,搜索,下载的小说软件

#### 软件说明

1. 支持小说阅读,订阅,搜索及下载功能
2. 支持插件系统,编写新的搜索插件
3. 支持wifi传输功能

#### 软件架构
    依赖的库: PyQt5, scrapy, httpx, requests, qrcode, multiprocessing, asyncio, jinja2
    运行环境: python 3.7

#### 使用说明

1.  cd pyqt_novel
2.  python ./appLancher.py

#### 插件系统

1.文本插件  
    插件名称必须已plugin开头的py文件,比如plugin1.py, plugin2.py
    插件必须定义两个类: BasicFileHandler为下载小说文件的类, BasicFileSpider为搜索小说的scrapy.Spider子类

    BasicFileSpider子类中必须定义InfoObj对象,根据爬取的网站规则定义好以下字段内容,自定义的插件才能成功使用

    '''
    inf = InfoObj()
    inf.novel_name = '诛仙'               # 必须定义,搜索结果的小说名称
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
    from scrapy.linkextractors import LinkExtractor
    from app_runtime import BasicFileSpider, BasicFileHandler, register, InfoObj


    @register
    class FileTaskCeshi(BasicFileHandler):

        use_plugin = False  # 为True时使用插件, 默认不使用

        name = '测试'  # 必须定义:唯一名称,和BasicFileSpider子类名称相同

        header = {}  #小说下载headers
        
        def file_headers_hook(self, inf): # 设置下载header的钩子函数
            return cls.header

    class FileSpider${plugin_name}(BasicFileSpider):

        name = '测试'  # 必须定义:唯一名称,和BasicFileHandler子类名称相同

        novel_name = '' # 待搜索的小说名称

        use_plugin = False  # 为True时使用插件, 默认不使用

        def start_requests(self): # scrapy搜索开始
            pass

        def parse(self, response): # 回调函数
            pass

            '''
            ...其他爬取过程
            '''

        def getDownLoadUrl(self, response): # 回调函数
            ...
            self.finalStep(inf)

2.章节插件

插件名称必须已chapter开头的py文件,比如chapter1.py, chapter2.py
插件必须定义两个类: BasicChapterHandler为爬取小说章节的类, BasicFileSpider为搜索小说的scrapy.Spider子类

BasicFileSpider子类中必须定义InfoObj对象,根据爬取的网站规则定义好以下字段内容, 自定义的插件才能成功使用

    inf = InfoObj()
    inf.novel_name = '诛仙'               # 必须定义,搜索结果的小说名称
    inf.novel_chapter_urls = [(chapter_url: str, chapter_name: str), ...]   #必须定义: (小说章节url, 小说章节名), ...
    self.finalStep(inf)                 # 必须调用,开始爬取,当定义好inf所需要的字段,否则插件无法正常运行

    inf.novel_introutced = '...'         # 小说详情介绍,可以不定义
    inf.novel_img_url = 'http://...'     # 可以不定义,小说封面url, 如果为'',则不下载小说封面
    inf.novel_img_headers = {}           # 小说封面下载headers
    inf.novel_info_url = 'http://...'    # 可以不定义,小说详情url;若不定义无法订阅



        import scrapy
        import httpx

        from scrapy.linkextractors import LinkExtractor
        from scrapy.http import HTMLResponse
        from httpx._types import CookieTypes
        from bs4 import BeautifulSoup

        from app_runtime import BasicChapterSpider, BasicChapterHandler, register, InfoObj


        @register
        class ChapterTaskCeshi(BasicChapterHandler):

            use_plugin = False  # 为True时使用插件, 默认不使用

            name = '测试'  # 必须定义:唯一名称,和BasicFileSpider子类名称相同

            header = {}  #当前小说章节的下载headers
            
            def chapter_headers_hook(cls, url_index: int, url: int, inf: InfoObj): # 设置下载小说章节header的钩子函数,默认返回{}
                return cls.header

            def parse_charpter(cls, url_index: int, response: 'httpx.Response', chapter: str):

                '''
                url_index: 当前的章节的初始请求顺序
                response: httpx.Response实例
                return: 返回值是一个2元元组, content_line, chapter_name
                    content_line: Iterable[str] 即小说章节文本内容,是一个可迭代的文本行的序列(推荐返回文本行的生成器, bs4 tag.stripped_strings属性即是个生成器) 
                    chapter_name: str 小说章节名

                示例:
                soup = BeautifulSoup(response.text, 'lxml')
                chapter, = soup.select('.txt_cont > h1:nth-child(1)')
                content_lines, = soup.select('#content1')
                return content_lines.stripped_strings, chapter.string

                '''
                
                return NotImplemented

        class ChapterSpiderCeshi(BasicChapterSpider):

            name = '测试' # 必须定义:唯一名称,和BasicChapterHandler子类名称相同

            novel_name = ''  # 待搜索的小说名称

            use_plugin = False  # 为True时使用插件, 默认不使用

            def start_requests(self):
                pass

            def parse(self, response):
                pass

                ...

            def getChapter(self, response):
                '''
                results = [(url, chapter_name), ...]
                inf.novel_chapter_urls = results
                self.finalStep(inf)

                '''
                pass

            @classmethod
            def subscribe_cookies(cls) -> CookieTypes:
                '''
                访问订阅页面的cookies, 默认为None
                '''
                return None

            @classmethod
            def subscribe_updateinfo(cls, response: HTMLResponse) -> InfoObj:
                '''
                response: scrapy.http.HTMLResponse
                return: 默认返回None,无法订阅; 返回 InfoObj实现订阅功能
                >>>

                introutecd = response.css('#intro::text').get()
                links = LinkExtractor(restrict_css=['#idlist']).extract_links(response)
                inf = InfoObj()
                inf.novel_chapter_urls = [(link.url, link.text) for link in links]
                # inf.novel_introutced = introutecd
                return inf

                '''
                return None


#### 展示

1.使用

![](docs\使用.gif)

2.阅读

<img src="https://images.gitee.com/uploads/images/2021/0615/144703_cf36d0bb_4925919.gif" alt="阅读.gif" style="zoom:50%;"/>

3.调试功能

<img src="https://images.gitee.com/uploads/images/2021/0615/143535_37e4899a_4925919.gif" alt="调试.gif" style="zoom:50%;"/>

4.命令

<img src="https://images.gitee.com/uploads/images/2021/0615/143810_f0ff9f90_4925919.gif" alt="命令.gif" style="zoom:50%;"/>

5.传输

<img src="https://images.gitee.com/uploads/images/2021/0615/142104_bd722487_4925919.gif" alt="传输.gif" style="zoom:50%;"/>