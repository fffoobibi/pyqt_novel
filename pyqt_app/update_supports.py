import os
from typing import List

class AppUpdateManager(object):

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_tpls_update(self) -> bool: # 获取插件更新,待实现
        return False

    def get_main_update(self): # 获取程序更新,待实现
        return

    def list_tpls(self) -> List[str]: # 获取程序目录默认插件
        return list(filter(lambda v: v.endswith('py'), os.listdir('./tpls')))
