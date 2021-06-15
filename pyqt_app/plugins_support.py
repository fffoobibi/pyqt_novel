import sys
import os
import traceback
from PyQt5.QtCore import QDir, QStandardPaths
from string import Template
from contextlib import suppress
from .magic import ncalls


__all__ = ['load_plugin', 'generate_plugin', 'HumReadMixin']

home_dir = QDir(QStandardPaths.writableLocation(QStandardPaths.HomeLocation))

if not home_dir.exists('plugins'):
    home_dir.mkdir('plugins')

plugin_dir = QDir(home_dir.absoluteFilePath('plugins'))
plugin_path = plugin_dir.absolutePath()

sys.path.append(plugin_dir.absolutePath())

app_runtime = sys.modules['app_runtime'] = sys.modules['crawl_novel.spiders.filesspider'].__class__('app_runtime')

app_runtime.BasicFileSpider = sys.modules['crawl_novel.spiders.filesspider'].BasicFileSpider
app_runtime.BasicChapterSpider =  sys.modules['crawl_novel.spiders.filesspider'].BasicChapterSpider

app_runtime.BasicFileHandler = sys.modules['crawl_novel.spiders.downtasks'].BasicFileHandler
app_runtime.BasicChapterHandler = sys.modules['crawl_novel.spiders.downtasks'].BasicChapterHandler

app_runtime.register = sys.modules['crawl_novel.spiders.downtasks'].register
app_runtime.InfoObj = sys.modules['crawl_novel.spiders.infoobj'].InfoObj

def load_plugin() -> bool: # 导入默认插件
    _generate_default_plugins()
    flags = []
    plugin_dir.setFilter(QDir.Files | QDir.NoDotAndDotDot)
    files_infos = plugin_dir.entryInfoList()
    for f in files_infos:
        abs_file = QDir.toNativeSeparators(f.absoluteFilePath())
        base_name = f.fileName()
        if abs_file.lower().endswith('py') and (base_name.startswith('filePlg') or base_name.startswith('chapterPlg')):
            module_name = f.baseName()
            try:
                module = __import__(module_name)
                sys.modules[module_name] = module
                if module in sys.modules.values():
                    flags.append(True)
                else:
                    flags.append(False)
            except:
                flags.append(False)
                traceback.print_exc()
    if len(flags) == 0:
        return False
    if all(flags):
        return True
    return False


def generate_plugin(plugin_name: str, task_name: str, site_name: str, output_name: str, output_path: str, type=0) -> None:
    if type == 0:
        tpl_file = open('./tpls/filetpl.tmpl', encoding='utf8')
        op_name = os.path.join(output_path, f'filePlg{output_name}.py') 
    elif type == 1:
        tpl_file = open('./tpls/chaptertpl.tmpl', encoding='utf8')
        op_name = os.path.join(output_path, f'chapterPlg{output_name}.py') 
    tpl = Template(tpl_file.read())
    tpl_content = tpl.substitute(plugin_name=plugin_name, task_name=task_name, site_name=site_name)
    with open(op_name, 'w+', encoding='utf8') as file:
        file.write(tpl_content)

@ncalls
def _generate_default_plugins(): # 生成默认插件至plugins目录下
    if _generate_default_plugins.ncalls() == 1:
        values = os.listdir('./tpls')
        for value in values:
            if value.lower().endswith('py'):
                abs_file = os.path.abspath(os.path.join('./tpls', value))
                content = open(abs_file, 'r', encoding='utf8').read()
                write_file = os.path.join(plugin_path, value)
                with open(write_file, 'w', encoding='utf8') as file:
                    file.write(content)

class HumReadMixin:

    __slots__ = ()

    def size_hum_read(self, value: int) -> str:
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = 1024.0
        for i in range(len(units)):
            if (value / size) < 1:
                return "%.2f%s" % (value, units[i])
            value = value / size
