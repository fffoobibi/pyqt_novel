import logging
import json

from queue import Queue
from datetime import datetime
from os.path import join, exists
from collections import OrderedDict
from typing import Iterable


__all__ = ['SearchLog', '_logMessage', '_MessageStream', '_MessageHandler', 'getSearchLog']

class _SearchLog():

    __instance = None

    DUMP_NAME = 'search.json'

    max_length = 500

    dft_key_type = '%Y%m%d'
    
    @classmethod
    def getSearchLog(cls, save_path=''):
        if cls.__instance is None:
            if save_path:
                pickled_path = join(save_path, cls.DUMP_NAME)
                if exists(pickled_path):
                    cls.__instance = cls.fromPath(save_path)
                else:
                    ins = cls(save_path)
                    cls.__instance = ins
            else:
                ins = cls(save_path)
                cls.__instance = ins
        return cls.__instance

    @classmethod
    def fromPath(cls, save_path: str) -> '_SearchLog':
        js_path = join(save_path, cls.DUMP_NAME)
        fp = open(js_path, 'r', encoding='utf8')
        json_dict = json.load(fp)
        log = cls(save_path)
        log._logs = OrderedDict(json_dict)
        return log

    def __init__(self, save_path):
        self.save_path = save_path
        self.length = 0
        self._logs = OrderedDict()
        
    def clear(self) -> None:
        self.length = 0
        self._logs.clear()

    def removeLog(self, time: datetime, index: int=-1) -> None: 
        key = datetime.now().strftime(self.dft_key_type)
        logs = self._logs.get(key, None)
        if logs:
            logs.pop(index)
            self.length -= 1

    def removeLogByMsg(self, date_time: datetime, msg: str) -> None:
        key = date_time.strftime(self.dft_key_type)
        logs = self._logs.get(key, None)
        if logs:
            index = logs.index(msg)
            logs.pop(index)
            self.length -= 1

    def addLog(self, novel_name) -> None:
        if self.length >= self.max_length:
            self._popminvalue()
            self.length -= 1
        self.length += 1
        key = datetime.now().strftime(self.dft_key_type)
        novel = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._logs.setdefault(key, [])
        logs = self._logs.get(key)
        logs.append(novel+': ' + novel_name)

    def _minkey(self) -> str:
        ks = self._logs.keys()
        ks = [datetime.strptime(k, self.dft_key_type) for k in ks]
        return min(ks).strftime(self.dft_key_type)

    def _minvalue(self) -> str:
        msk = self._minkey()
        return self._logs[msk][0]

    def _popminvalue(self) -> str:
        msk = self._minkey()
        return self._logs[msk].pop(0)

    def getLogs(self, time: datetime) -> list:
        key = time.strftime(self.dft_key_type)
        return self._logs.get(key, None)

    def allLogs(self) -> Iterable[str]:
        keys = [datetime.strptime(ks, self.dft_key_type) for ks in self._logs.keys()]
        keys.sort(reverse=True)
        keys = [ks.strftime(self.dft_key_type) for ks in keys]
        for key in keys:
            temp_logs = self._logs[key].copy()
            temp_logs.reverse()
            yield from temp_logs

    def dump(self) -> None:
        if self.save_path:
            fp = open(join(self.save_path, self.DUMP_NAME), 'w', encoding='utf8')
            json.dump(self._logs, fp, ensure_ascii=False, indent=4)

    def __iter__(self) -> Iterable[str]:
        yield from self.allLogs()

    def __len__(self) -> int:
        return self.length

    def __repr__(self) -> str:
        return str(self._logs)


def getSearchLog(save_path=''):
    return _SearchLog.getSearchLog(save_path)

class _logMessage(str):
    def totalLines(self) -> int:
        return len(self.splitlines())

    def showLineNoHtml(self, start=1) -> str:
        res = self.splitlines()
        lines = []
        i = start - 1
        for line in res:
            i += 1
            index = f'{i}.'.rjust(5, ' ') + ' '
            _line = line.strip().replace('<', '&lt;').replace('>', '&gt;')
            new_line = f'<pre style="line-height:0.6">{index}{_line}</pre>' 
            lines.append(new_line)
        return _logMessage(''.join(lines))
            

class _MessageStream():
    def __init__(self):
        self.q = Queue()

    def write(self, value):
        self.q.put(value)

    def flush(self):
        pass

class _MessageHandler(logging.StreamHandler):
    terminator = ''
    def __init__(self, stream=None):
        logging.Handler.__init__(self)
        if stream is None:
            stream = _MessageStream()
        self.stream = stream

    def stream_get(self, block=True, timeout=None) -> str:
        return self.stream.q.get(block, timeout)
