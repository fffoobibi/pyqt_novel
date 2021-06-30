from cgi import print_directory
import sys

from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QApplication, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtCore import QSize, QSizeF, Qt, QStandardPaths, QFile, QFileInfo, QDir, pyqtSignal, pyqtSlot, QRect, QRectF, QPoint, QPointF
from PyQt5.QtGui import (QBrush, QPageLayout, QPageSize, QPagedPaintDevice,
                         QPixmap, QIcon, QTextCharFormat, QTextDocument,
                         QTextBlock, QTextBlockFormat, QTextCursor, QTextFragment, QTextLine,
                         QTextLayout, QPainter, QFont, QFontMetrics,
                         QTextObject)
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewWidget


content = '''
天气有些冷。
瘦巴巴的沈安在艰难的跋涉着。
他的背上还背着一个同样瘦弱的女娃。
作为一个事业有成的老大叔，他觉得日子很不错，但是一觉醒来就变了……
他在半月前穿越到了一个失踪官员的儿子身上……
北宋嘉佑三年，此刻是正月，可沈安却背着妹妹在迁徙。
“哥，车车呢？”
背上的果果睡醒了，然后伸出小拳头揉揉眼睛。
“车车掉河里去了。”
上午因为车费耗尽，那个商队就以自己要转向去别处为由，把他们兄妹赶出了车队。
“哥，家呢？”
果果趴在他的背上，突然哭了起来。
“我要爹爹……”
沈安无语望天。
好容易哄好了妹妹，沈安看天色不早了，就抓紧时间赶路。
当前面出现一个小镇时，沈安整个人都差不多要虚脱了。
小镇就是一条街，夕阳下显得生机勃勃。
小镇上唯一的一家酒肆里座无虚席，沈安牵着妹妹走了进去。
一群食客看向他们兄妹，随后又各自用饭。
酒肉的香味传来，果果舔舔干燥的嘴唇，然后摸摸小肚子，却不肯说饿了。
得挣钱啊！
伙计过来了，看了他们兄妹一眼，有些嫌弃的问道：“客官要吃什么？”
'''

# QTextFragment
class Read(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = content

    def drawDocument(self,
                     painter: QPainter,
                     doc: QTextDocument,
                     r: QRectF,
                     brush=Qt.NoBrush):
        if doc.isEmpty():
            return
        painter.save()
        if r.isValid():
            painter.setClipRect(r, Qt.IntersectClip)
        size = doc.size()
        fmt = doc.rootFrame().frameFormat()
        size.setWidth(size.width() - fmt.leftMargin() - fmt.rightMargin())
        block = doc.begin()
        while True:
            if not block.isValid():
                break
            self.drawTextLayout(painter, block, size, brush)
            block = block.next()
        painter.restore()

    def drawTextLayout(self, p: QPainter, block: QTextBlock, size: QSizeF,
                       brush: QBrush):
        if not block.isValid():
            return
        layout = block.layout()
        if not layout:
            return
        if layout.lineCount() < 1:
            return

        # 基线,每绘制一行则y下移一行的位置,x不变
        baseLine = layout.position()
        baseLine.setY(baseLine.y() + layout.lineAt(0).ascent())
        outPos = baseLine
        block.begin()

    def drawText(self, painter: QPainter, p: QPointF, fmt: QTextCharFormat,
                 brush: QBrush):
        pass


class Widget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.document = QTextDocument()
        self.cursor: QTextCursor = QTextCursor(self.document)
        html = ''.join(['<p style="text-indent:10px">%s</p>'% line.strip() for line in content.splitlines()])
        # self.document.setPlainText(content)
        self.document.setHtml(html)
        self.resize(300, 200)
        print(self.document.lineCount())


    def visable(self):
        # self.cursor.setPosition(0)
        # # self.cursor.movePosition(QTextCursor.NoMove, QTextCursor.KeepAnchor, 20)
        # # self.cursor.select(QTextCursor.WordUnderCursor)
        # self.cursor.setPosition(20, QTextCursor.KeepAnchor)
        limit = self.height()
        bl = self.document.firstBlock()
        h = 0
        doclayout = self.document.documentLayout()
        while True:
            if bl.isValid():
                it = bl.begin()
                layout = bl.layout()
                print(doclayout.anchorAt(QPoint(4, 5)))
                h = doclayout.blockBoundingRect(bl).y() - 4
                print('h: %s, height: %s'%(h, limit), doclayout.blockBoundingRect(bl), bl.lineCount())

                fragment_count = 0
                while not it.atEnd():
                    fragment = it.fragment()
                    if fragment.isValid():
                        fragment_count += 1
                        # print('frag: %s, positon: %s, length: %s'% (fragment.text(), fragment.position(), fragment.length()))
                        # it = next(it)
                    it += 1
                if h >= limit:
                    print(doclayout.blockBoundingRect(before), before.text(), fragment_count) 
                    break
                else:
                    before = bl
                    bl = bl.next()
                    if not bl.isValid():
                        break


    def paintEvent(self, a0) -> None:
        painter = QPainter(self)
        w = self.width()
        h = self.height()
        # self.document.setTextWidth(w)
        self.document.setPageSize(QSizeF(w, h))
        self.document.drawContents(painter, QRectF(0, 0, w, h))
        self.visable()
        painter.drawRect(self.rect())
      

def main():
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()