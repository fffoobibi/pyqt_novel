import os
import io
import sys
import html
import socket
import urllib
from os.path import isfile, isdir
from functools import partial
from http.server import test, SimpleHTTPRequestHandler
from http import HTTPStatus
from multiprocessing import Process

__all__ = ['startTransferSever', 'get_local_ip', 'TransferSeverState']


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        return ip
    finally:
        s.close()


class TransferSever(SimpleHTTPRequestHandler):
    
    def generate_li(self, href, base_name, *, is_file=None, is_dir=None, is_link=None):
        if is_file:
            type = base_name.split('.')[-1].lower()
            if type in ('png', 'jpg', 'jpeg', 'bmp', 'png', 'ico', 'svg'):  # 图片文件
                icon = 'fa-file-image-o'
            elif type in ('mp4', 'mpeg', 'avi', 'navi', 'asf', 'mov', '3gp', 'wmv', 'divx', 'xvid', 'rm', 'rmvb', 'flv'):
                icon = 'fa-file-video-o'
            elif type in ('txt', 'cfg', 'ini', 'tmpl', 'log'):
                icon = 'fa-file-text-o '
            elif type in ('xlsx', 'xlsm', 'xls', 'xlst', 'xlsb'):
                icon = 'fa-file-excel-o'
            elif type in ('doc', 'docx', 'dotx', 'dot', 'docm', 'dotm', 'xps', 'mht', 'mhtml', 'rtf', 'xml', 'odt'):
                icon == 'fa-file-word-o'
            elif type in ('bat', 'py', 'c', 'cpp', 'js', 'ts', 'dart', 'java', 'pyc', 'pyd', 'class', 'pyw', 'sh', 'pyi', 'vba', 'vbs', 'vb'):
                icon = 'fa-file-code-o'
            elif type in ('mp3', 'flac', 'cd', 'wave', 'aiff', 'mpeg-4', 'midi', 'wma', 'amr', 'ape', 'aac'):
                icon = 'fa-music'
            elif type in ('pdf', ):
                icon = 'fa-file-pdf-o'
            elif type in ('zip', 'rar', '7z'):
                icon = 'fa-file-archive-o'
            elif type in ('html', 'html5', 'htmlx'):
                icon = 'fa-html5'
            else:
                icon = 'fa-file-o'
        elif is_dir:
            icon = 'fa-folder-o'
        elif is_link:
            icon = 'fa-link'
        if is_file:
            li = '<li><a href="%s" download=""><i class="fa %s fa-fw" aria-hidden="true" style="color:gray"></i>%s</a></li>' % (
                href, icon, base_name)
        else:
            li = '<li><a href="%s"><i class="fa %s fa-fw" aria-hidden="true" style="color:gray"></i>%s</a></li>' % (
                href, icon, base_name)
        return li

    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(
                HTTPStatus.NOT_FOUND,
                'No permission to list directory')
            return None
        list.sort(key=lambda a: a.lower())
        r = []
        enc = sys.getfilesystemencoding()
        title = '当前目录 %s' % os.path.dirname(path).replace('\\', '/')

        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % enc)
        r.append(
            '<link rel="stylesheet" href="https://cdn.bootcss.com/font-awesome/4.7.0/css/font-awesome.css">')
        r.append('<title>文件传输</title>\n</head>')
        r.append('<body>\n<h2>%s</h2>' % title)
        r.append('<hr>\n<ol>')
        i = 0
        for name in list:
            i += 1
            fullname = os.path.join(path, name)
            displayname = linkname = name
            if os.path.isdir(fullname):
                displayname = name + '/'
                linkname = name + '/'
                href = urllib.parse.quote(linkname, errors='surrogatepass')
                base_name = html.escape(displayname, quote=False)
                r.append(self.generate_li(href, base_name, is_dir=True))
            if os.path.islink(fullname):
                displayname = name + '@'
                href = urllib.parse.quote(linkname, errors='surrogatepass')
                base_name = html.escape(displayname, quote=False)
                r.append(self.generate_li(href, base_name, is_link=True))
            if os.path.isfile(fullname):
                href = urllib.parse.quote(linkname, errors='surrogatepass')
                base_name = html.escape(displayname, quote=False)
                value = self.generate_li(href, base_name, is_file=True)
                r.append(value)
        r.append('</ol>\n<hr>\n</body>\n</html>\n')
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/html; charset=%s' % enc)
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        return f

    @staticmethod
    def run(directory):
        handler_class = partial(TransferSever, directory=directory)
        test(HandlerClass=handler_class, port=80)


class TransferSeverState(object):
    def __init__(self, process=None):
        self.process = process

    def set_process(self, p):
        self.process = p

    def is_alive(self):
        if self.process is None:
            return False
        return self.process.is_alive()

    def terminte_process(self):
        if self.process:
            self.process.terminate()
        self.process = None


def _run_server(directory: str):
    TransferSever.run(directory)


def startTransferSever(directory: str) -> Process:
    process = Process(target=_run_server, args=(directory, ))
    process.daemon = True
    process.start()
    return process
