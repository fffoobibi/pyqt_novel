import sys, os
from typing import Any, Iterable, List, Sequence

from PyQt5.QtWidgets import QFrame, QListWidget, QPlainTextEdit, QSizePolicy, QSpacerItem, QTextBrowser, QTextEdit, QWidget, QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QPoint, QSize, Qt, QStandardPaths, QFile, QFileInfo, QDir, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter, QPalette, QPixmap, QIcon, QTextBlock, QTextCursor, QTextLayout
from pyqt_app.styles import listwidget_v_scrollbar
file = r"C:/Users/fqk12/Desktop/v2-0009da0ab94c0bd0bcff4823e1fc0586_r.jpg"

class ReadWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line_spacing = 5
        self.indent = 20
        self.margin = 40
        self.letter_spacing = 0
        self.read_font = QFont('微软雅黑', 12)
        self.read_font.setLetterSpacing(QFont.AbsoluteSpacing, self.letter_spacing)
        self.title_font = QFont(self.read_font)
        self.title_font.setPointSize(16)
        self.bkg_color = Qt.white
        self.text_color = Qt.black
        self.current_page = 0
        self._p_lines = []
        self.read_layout = QVBoxLayout(self)
        self.read_layout.setSpacing(self.line_spacing)
        self.read_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setReadStyle(bkg_image=file)

        mesage = self._get_message_from_caches(0)
        content = mesage['content']
        content.insert(0, mesage['chapter'])
        self.chapter_content = content

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.read_width = self.width() - 10
        self.read_height = self.height()
        self._clearReadLines()
        self.computePages(self.chapter_content)

    def paintEvent(self, event) -> None:
        if self.bkg_image:
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), QPixmap(self.bkg_image))
        super().paintEvent(event)

    def computePages(self, lines: list, index: int = 0):  # 计算章节所需页数
        height = self._textHeight() 
        title_height = self._titleHeight() 
        self._addLines(lines)

        label_counts = int((self.read_height + height - title_height) / (self.line_spacing + height)) # title,分页
        p1 = self._split_sequence(self._p_lines, label_counts)[0]

        label_counts = int((self.read_height) / (self.line_spacing + height)) # content 分页
        p2 = self._split_sequence(self._p_lines[len(p1):], label_counts) 
        p2.insert(0, p1)
        self._p_lines = p2

        self.current_page = index
        self.read_layout.addSpacing(self.line_spacing)
        for line, p_first_flag, p_title in self._p_lines[index]:
            self._setReadLine(line, height, p_first_flag, p_title)
        self.read_layout.addStretch()
    
    def setReadStyle(self, bkg_color=None, text_color=None, bkg_image=None):
        self.bkg_color =  QColor(self.bkg_color) if bkg_color is None else QColor(bkg_color)
        self.text_color = QColor(self.text_color) if text_color is None else QColor(text_color)
        self.bkg_image = bkg_image
        sytles = 'QLabel{color: %s} QFrame{background:transparent}' % self.text_color.name()
        self.setStyleSheet(sytles)

    def setTextColor(self, color):
        self.text_color = QColor(color)
        self.update()

    def setBkgColor(self, color):
        self.bkg_color = QColor(color)
        self.update()

    def setBkgImage(self, image: str):
        self.bkg_image = image
        self.update()



    def pageCount(self) -> int:  # 章节页数
        if self._p_lines:
            return len(self._p_lines)
        return 0

    def next_page(self):
        print(self.read_layout.count())
        height = self._textHeight() 
        next = (self.current_page + 1) % self.pageCount()
        if next > 0:
            self.current_page = next
            self._clearReadLines()
            self.read_layout.addSpacing(self.line_spacing)
            for line, p_first_flag, p_title in self._p_lines[self.current_page]:
                self._setReadLine(line, height, p_first_flag, p_title)
            self.read_layout.addStretch()

    def previous_page(self):
        height = self._textHeight() 
        previous = (self.current_page - 1) % self.pageCount()

        if previous < self.pageCount() - 1:
            self.current_page = previous
            self._clearReadLines()
            self.read_layout.addSpacing(self.line_spacing)
            for line, p_first_flag, p_title in self._p_lines[self.current_page]:
                self._setReadLine(line, height, p_first_flag, p_title)
            self.read_layout.addStretch()

    def _split_sequence(self, dst: Sequence, split_num: int) -> List:
        return [dst[i:i + split_num] for i in range(0, len(dst), split_num)]

    def _textHeight(self): # 常规
        return QFontMetrics(self.read_font).height()

    def _titleHeight(self): # 标题
        return QFontMetrics(self.title_font).height()

    def _setReadLine(self, line: str, height: int,
                     p_first_flag: bool, p_title: bool):  # 天降阅读行
        frame = QFrame()
        frame.setAutoFillBackground(True)
        frame.setFrameShape(QFrame.NoFrame)
        frame.setFixedHeight(height)
        frame_h = QHBoxLayout(frame)
        frame_h.setContentsMargins(0, 0, 0, 0)
        frame_h.setSpacing(0)

        label = QLabel(frame)
        label.setStyleSheet('border:0px solid black')
        if p_title:
            label.setFont(self.title_font)
        else:
            label.setFont(self.read_font)
        label.setText(line)
        if p_first_flag:
            label.setIndent(self.indent)
        frame_h.addSpacing(self.margin)
        frame_h.addWidget(label)
        frame_h.addStretch()
        self.read_layout.addWidget(frame)

    def _clearReadLines(self):  # 清空阅读行
        layout = self.read_layout
        child = layout.takeAt(0)
        while (child is not None):
            if child.widget():
                child.widget().setParent(None)
            child = layout.takeAt(0)

    def _addLine(self, line: str, fm: QFontMetrics) -> str:
        lines = self._text_compute(line, fm, self.read_width)
        i = -1
        for line in lines:
            i += 1
            p_first_line = True if i == 0 else False
            self._p_lines.append([line, p_first_line, False])
        
    def _addLines(self, lines: list): # 分行处理
        self._p_lines.clear()
        fm = QFontMetrics(self.read_font)
        i = 0
        for line in lines:
            i += 1
            fms = QFontMetrics(self.title_font) if i ==1 else fm
            self._addLine(line, fm)
        self._p_lines[0][-1] = True

    def _text_compute(self, text: str, fm: QFontMetrics, width: int) -> list:
        if fm.width(text) <= width - self.indent - self.margin * 2:
            return [text]
        else:
            res = []
            lines = []
            row = 1
            for alpha in text:
                res.append(alpha.strip())
                if row == 1:
                    flag = width - self.indent - self.margin * 2
                if fm.width(''.join(res)) >= flag:
                    lines.append(''.join(res).strip())
                    flag = width - self.margin * 2
                    row += 1
                    # last = res[-1].strip()
                    res.clear()
                    # res.append(last)
            lines.append(''.join(res).strip())
            return lines

    def _get_message_from_caches(self, index: int) -> dict:  # 从缓存章节中重新渲染
        res = {'content': [], 'chapter': ''}
        s_path = r'C:\Users\fqk12\.qt_novel_search_app\read_caches\《水浒之王者天下》作者：异次元之门b6b2567c24f002ef8830d27909b8c41a'
        s_dir = QDir(s_path)
        temp = list(os.listdir(s_path))
        flags = [int(v.split('___')[0]) for v in temp]
        finded_index = flags.index(index)
        if finded_index >= 0:
            cache_name = temp[finded_index]
            with open(s_dir.absoluteFilePath(cache_name), 'r',
                      encoding='utf8') as file:
                for index, line in enumerate(file):
                    if index == 0:
                        res['chapter'] = line.strip()
                    else:
                        res['content'].append(line.strip())
        return res

class Test(QTextBrowser):
    def __init__(self) -> None:
        super().__init__()
        htmls =[f'<p>{i}: sdfsdf\ngdg\n</p>' for i in range(30)]
        self.setHtml(''.join(htmls))
        

class Widget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        # self.read_widget = ReadWidget()
        self.resize(600, 400)
        self.read_widget = Test()
        self.read_widget.verticalScrollBar().setStyleSheet(listwidget_v_scrollbar)
        self.read_widget.verticalScrollBar().valueChanged.connect(self.testV)
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.addWidget(self.read_widget)
        v.addWidget(QPushButton('test', clicked=self.test))
        # v.addWidget(QPushButton('next', clicked=self.nn))
        # v.addWidget(QPushButton('previous', clicked=self.pp))
    def test(self):
        document = self.read_widget.document()
        bl = document.firstBlock()
        res = []
        blocks = []
        # print(document.blockCount())
        for i in range(document.blockCount()):
            block = document.findBlockByNumber(i)
            geo = block.layout().boundingRect()
            geo.setTopLeft(block.layout().position())
            res.append(geo.center().y())
            blocks.append(block)

        minmun = self.read_widget.verticalScrollBar().minimum()
        page_step = self.read_widget.verticalScrollBar().pageStep() 
        total = self.read_widget.document().size().height()
        current = self.read_widget.verticalScrollBar().value()

        s1 = current - minmun
        s2 = page_step
        s3 = total - s1- s2

        # y1 = total * s1 / (s1 + s2 + s3)
        y1 = (current - minmun) * total / page_step
        y2 = total * s2 / (s1 + s2 + s3)
        y3 = total * s3 / (s1 + s2 + s3)
        y3 = total - page_step - current + minmun
        
        print('current: ', current/total)
        distances = list(map(lambda e: abs(e - y1), res))

        rel: QTextBlock = blocks[distances.index(min(distances))]
        print(rel.blockNumber(), rel.text())
        print(self.read_widget.height())
      
        cursor = self.read_widget.cursorForPosition(QPoint(0, 0));
        bottom_right = QPoint(self.read_widget.viewport().width() - 1, self.read_widget.viewport().height() - 1)
        end_pos = self.read_widget.cursorForPosition(bottom_right).position()
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        print(repr(cursor.selectedText()))


    def testV(self, v):
        max = self.read_widget.verticalScrollBar().maximum()
        min = self.read_widget.verticalScrollBar().minimum()
        page_step = self.read_widget.verticalScrollBar().pageStep()

        print( v / page_step, (max - min +page_step)/ page_step)
        
        
    def nn(self):
        self.read_widget.next_page()
        self.sender().setText('next: %s' % (self.read_widget.current_page + 1))

    def pp(self):
        self.read_widget.previous_page()
        self.sender().setText('previous: %s' %
                              (self.read_widget.current_page + 1))


def main():
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()