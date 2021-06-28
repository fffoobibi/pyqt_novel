from typing import Union, List
from collections.abc import Sequence, MutableSequence


PageContents = Union[List['_AutoLine'], List['_AutoPage']]

class _AutoPages(MutableSequence):

    __slots__ = ('pages', )

    def __init__(self) -> None:
        self.pages: PageContents = []

    def _container_(self):
        return self.pages

    def __getitem__(self, index):
        return self._container_()[index]

    def __setitem__(self, index, value):
        self._container_()[index] = value

    def __delitem__(self, index):
        del self._container_()[index]

    def __len__(self):
        return len(self._container_())

    def insert(self, index, value):
        self._container_().insert(index, value)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{self._container_()}'

    def __add__(self, other):
        self._container_() + other._containter_()

    def split_page(self, page_count: int) -> '_AutoPages': # 分页, lines -> pages
        dst = self._container_()
        pages = [_AutoPage(dst[i:i + page_count]) for i in range(0, len(dst), page_count)]
        result = _AutoPages()
        result.pages = pages
        return result

class _AutoPage(_AutoPages):

    __slots__ = ('lines', )

    def __init__(self, lines: List['_AutoLine'] = None) -> None:
        self.lines = lines or []

    def _container_(self):
        return self.lines


class _AutoLine(_AutoPages):

    __slots__ = ('line', )

    def __init__(self, content: str='', has_indent: bool=False, is_title: bool=False) -> None:
        self.line = [content, has_indent, is_title]

    def _container_(self):
        return self.line

    @property
    def content(self):
        return self[0]

    @property
    def has_indent(self):
        return self[1]

    @property
    def is_title(self):
        return self[2]

line = _AutoLine()
a,b,c =line
print(a,b,c)