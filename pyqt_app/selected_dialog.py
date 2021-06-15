import re
import qrcode

from math import sqrt
from contextlib import suppress

from PyQt5.QtWidgets import QDialog, QLabel, QListWidgetItem
from PyQt5.QtCore import QEvent, Qt, QSize, QUrl, pyqtProperty
from PyQt5.QtGui import QDesktopServices, QPainter, QPainterPath, QBrush, QColor

from .styles import listwidget_v_scrollbar
from .selectedui import Ui_Dialog
from .magic import qmixin
from .common_srcs import CommonPixmaps

from crawl_novel import InfoObj

__all__ = ('SelectDialog', )

listwidget_selected_style = '''
    QListWidget::Item:hover:active{
    background-color:lightgray;
    color:black}
    QListWidget::Item{
    border-bottom:1px solid rgb(212, 212, 212)}
    QListWidget::Item:selected{
    color:#CC295F}
    QListWidget{outline:0px; background-color: transparent;border:none}'''

@qmixin
class SelectDialog(Ui_Dialog, QDialog):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.is_show = False
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 透明窗口
        self.listWidget.setStyleSheet(listwidget_selected_style)
        self.listWidget.verticalScrollBar().setStyleSheet(
            listwidget_v_scrollbar)
        self.lineEdit.setStyleSheet(
            'border:1px solid black; border-radius:0px')
        self.listWidget.itemClicked.connect(self.select)
        self.checkBox.stateChanged.connect(self.selectPolicy)
        self.lineEdit.returnPressed.connect(self.returnPolicy)
        self.pushButton.clicked.connect(self.openUrl)
        self.selected_count = 0
        self.current_url = None
        self.inf: InfoObj = None
        self.setStrWidth(self.lineEdit, '20-100,1000-20000,1000-10,12-12')
        self.installEventFilter(self)
        self.checkBox.setCursor(Qt.PointingHandCursor)

    @property
    def currentTaskWidget(self):
        return self.root.novel_widget.getCurrentTaskWidget()

    def gotoSelectedPage(self):
        self.stackedWidget.setCurrentIndex(0)
        index = self.inf.novel_read_infos.get('index', None)
        if index is not None:
            item = self.listWidget.item(index)
            self.listWidget.setCurrentItem(item)

    def gotoTransferPage(self, ip_address: str, is_alive: bool):
        if is_alive:
            l1 = 'WIFI共享:扫描二维码或访问'
            l2 = f'http://{ip_address}'
            l3 = '进行文件传输'
            self.pushButton.setEnabled(True)
        else:
            l1 = ''
            l2 = '无线传输未开启'
            l3 = ''
            self.pushButton.setEnabled(False)
        qr_img = qrcode.make(f'http://{ip_address}').toqpixmap()
        self.current_url = f'http://{ip_address}'
        self.stackedWidget.setCurrentIndex(1)
        self.label_3.setPixmap(qr_img)
        self.label_4.setText(l1)
        self.label_4.setCursor(Qt.ArrowCursor)
        self.pushButton.setText(l2)
        self.label_5.setText(l3)

    def openUrl(self):
        with suppress(Exception):
            QDesktopServices.openUrl(QUrl(self.current_url))

    def returnPolicy(self):
        def _(a1, a2):
            j = 0
            for i in range(self.listWidget.count()):
                item = self.listWidget.item(i)
                if a1 - 1 <= i <= a2 - 1:
                    item.setCheckState(Qt.Checked)
                    self.inf.novel_chapter_urls[i][-1] = True
                    j += 1
                else:
                    item.setCheckState(Qt.Unchecked)
                    self.inf.novel_chapter_urls[i][-1] = False
            self.selected_count = j
            self.label_2.setText(f'已选中: {self.selected_count}个')
            self.currentTaskWidget.label_2.setText(
                f'已选中: {self.selected_count}个')

        total = self.listWidget.count()
        s = self.sender().text().strip()
        if s and re.findall(r'^\d+\-\d+$', s):
            res = s.split('-')
            a1, a2 = int(res[0]), int(res[1])
            if a1 > a2:
                a1, a2 = a2, a1
                a2 = total if a2 >= total else a2
            else:
                a2 = total if a2 >= total else a2
            _(a1, a2)
        elif s and re.findall(r'^\d+?\-$', s):
            a1 = int(s.split('-')[0])
            a2 = self.listWidget.count()
            _(a1, a2)
        elif s and re.findall(r'^\-\d+$', s):
            a1 = 0
            a2 = int(s.split('-')[1])
            a2 = total if a2 >= total else a2
            _(a1, a2)
        self.checkBox.blockSignals(True)
        self.checkBox.setChecked(
            True) if self.selected_count == self.listWidget.count(
            ) else self.checkBox.setChecked(False)
        self.checkBox.blockSignals(False)

    def selectPolicy(self, state):
        if state == Qt.Checked:
            for i in range(self.listWidget.count()):
                item = self.listWidget.item(i)
                item.setCheckState(Qt.Checked)
                self.inf.novel_chapter_urls[i][-1] = True
            self.selected_count = self.listWidget.count()
        else:
            for i in range(self.listWidget.count()):
                item = self.listWidget.item(i)
                item.setCheckState(Qt.Unchecked)
                self.inf.novel_chapter_urls[i][-1] = False
            self.selected_count = 0
        self.label_2.setText(f'已选中: {self.selected_count}个')
        self.currentTaskWidget.label_2.setText(f'已选中: {self.selected_count}个')

    def select(self, item: QListWidgetItem):
        total = self.listWidget.count()
        row = self.listWidget.row(item)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
            self.inf.novel_chapter_urls[row][-1] = False
            self.selected_count -= 1
        else:
            item.setCheckState(Qt.Checked)
            self.inf.novel_chapter_urls[row][-1] = True
            self.selected_count += 1
        self.label_2.setText(f'已选中: {self.selected_count}个')
        self.checkBox.blockSignals(True)
        if self.selected_count == total:
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)
        self.currentTaskWidget.label_2.setText(f'已选中: {self.selected_count}个')
        self.checkBox.blockSignals(False)

    def addChapter(self, inf: InfoObj):
        if inf != self.inf or inf.chapter_count() != self.inf.chapter_count():
            task_widget = self.root.novel_widget.infs_widget
            self.listWidget.clear()
            self.selected_count = 0
            self.inf = inf
            total = len(inf.novel_chapter_urls)
            width = len(str(total))
            for url, chapter, state in inf.novel_chapter_urls:
                self.add_item(chapter, state, width, task_widget)
            self.label_2.setText(f'已选中: {self.selected_count}个')
            self.checkBox.blockSignals(True)
            if self.selected_count == self.listWidget.count():
                self.checkBox.setChecked(True)
            else:
                self.checkBox.setChecked(False)
            self.checkBox.blockSignals(False)

    def add_item(self, name, state, width, task_widget):
        def _():
            self.close()
            task_widget.read_fromlatest(count, True)

        count = self.listWidget.count()
        item = QListWidgetItem()

        current = str(count + 1).rjust(width)
        item.setText(current + f': {name}')
        item.setCheckState(Qt.Checked) if state else item.setCheckState(
            Qt.Unchecked)
        item.setSizeHint(QSize(200, 45))
        self.listWidget.addItem(item)
        if state:
            self.selected_count += 1

    def eventFilter(self, obj, event):
        if event.type() == QEvent.WindowDeactivate:
            self.close()
            self.is_show = False
        return QDialog.eventFilter(self, obj, event)

    def paintEvent(self, event):
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRect(10, 10, self.width() - 20, self.height() - 20)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillPath(path, QBrush(Qt.white))

        color = QColor(0, 0, 0, 50)
        for i in range(10):
            path = QPainterPath()
            path.setFillRule(Qt.WindingFill)
            # path.addRoundedRect(10-i, 10-i, self.width()-(10-i) * 2, self.height()-(10-i)*2, 5, 5)
            path.addRect(10 - i, 10 - i,
                         self.width() - (10 - i) * 2,
                         self.height() - (10 - i) * 2)
            color.setAlpha(150 - sqrt(i) * 50)
            painter.setPen(color)
            painter.drawPath(path)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.is_show = True

class _StateLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = False
        self.setStyleSheet(
            '''_StateLabel[state=true]{color:#CC295F;font-family:微软雅黑} 
                _StateLabel[state=false]{color:black;font-family:微软雅黑}''')

    @pyqtProperty(bool)
    def state(self) -> bool:
        return self._state

    @state.setter
    def state(self, value: bool) -> None:
        self._state = value
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()