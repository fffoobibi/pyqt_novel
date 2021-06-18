import wmi
import platform

from enum import Enum, IntEnum
from types import MethodType
from typing import Any, List, Union

from PyQt5.QtWidgets import (QButtonGroup, QListWidget, QListWidgetItem,
                             QPushButton, QWidget, QApplication, QMenu,
                             QStyledItemDelegate, QStyleOptionViewItem)
from PyQt5.QtCore import (QDir, QFileInfo, QSettings, pyqtSignal, pyqtSlot,
                          QSize, Qt, QModelIndex)
from PyQt5.QtGui import (QPixmap, QPainter, QPen, QCursor, QIcon,
                         QFont, QFontMetrics, QColor)

from crawl_novel import InfoObj, EightSpider, get_spider_byname, DownStatus, Markup

from .taskwidgetui import Ui_Form
from .common_srcs import CommonPixmaps
from .customwidgets import IconWidget, SubscribeWidget, get_subscribeLinkobj, TaskReadBrowser, FInValidator
from .styles import listwidget_v_scrollbar, menu_style, COLOR, read_v_style
from .magic import qmixin, lasyproperty
from .more_widgetui import Ui_Form as MoreUi
from .chapter_widgetui import Ui_Form as ChapterUi

__all__ = ('PageState', 'TaskWidget')

ColorTypes = Union[QColor, Qt.GlobalColor, str, int]

c_list_style = '''
    QListWidget::Item:hover:active{
    background-color: rgba(153, 149, 149, 80);
    color:#CCCCCC;
    border:none}
    QListWidget::Item{
    color:#CCCCCC;
    border:none;
    margin-left:10px}
    QListWidget::Item:selected{
    background-color: black;
    color: #CC295F}
    QListWidget{outline:0px; background-color: transparent; border:none}
'''

s_list_style = '''
    QScrollBar:vertical {
        background: black;
        padding: 0px;
        border-radius: 3px;
        max-width: 12px;
    }
    QScrollBar::handle:vertical {
        background: rgba(153, 149, 149, 80);
        min-height: 20px;
        border-radius: 3px;
    }
    QScrollBar::add-page:vertical {
        background: none;
    }
    QScrollBar::sub-page:vertical {
        background: none;
    }
    QScrollBar::add-line:vertical {
        background: none;
    }
    QScrollBar::sub-line:vertical {
        background: none;
    }
'''


class BrightManager:  # 改变屏幕亮度
    
    def __new__(cls) -> 'BrightManager':
        if not hasattr(cls, '_instance'):
            self = super().__new__(cls)
            self.w = wmi.WMI(namespace='root\WMI')
            self.is_windows = True if platform.system() == 'Windows' else False
            cls._instance = self
        return cls._instance

    @property
    def _monitor(self):
        for moniotr in self.w.WmiMonitorBrightnessMethods():
            if moniotr.Active:
                return moniotr

    @property
    def _bress(self):
        for bress in self.w.WmiMonitorBrightness():
            if bress.Active:
                return bress

    def setBrightness(self, value: int) -> None:
        if self.is_windows:
            if value < 0:
                value = 0
            elif value > 255:
                value = 255
            self._monitor.WmiSetBrightness(Brightness=value, Timeout=500)

    def currentBright(self) -> int:
        if self.is_windows:
            return self._bress.CurrentBrightness

    def BrightMinMax(self) -> tuple:
        if self.is_windows:
            level = self._bress.Level
            return level[0], level[-1]


class PageState(Enum):
    other = -1
    list_page = 0
    img_page = 1
    subscribe_page = 2
    home_page = 3


class settings_property(object):
    def __init__(self, dft):
        self.dft = dft
        self.type = type(dft)
        self.func = None

    def __set__(self, instance, value):
        instance.settings.setValue(f'Reading/{self.func.__name__}', value)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.settings.value(f'Reading/{self.func.__name__}',
                                       self.dft,
                                       type=self.type)

    def __call__(self, func) -> 'settings_property':
        self.func = func
        return self


class MoreWidget(QWidget, MoreUi):  # 阅读设置界面
    '''
    parent: main_gui
    '''
    @lasyproperty
    def settings(self) -> QSettings:
        return self.task_widget.novel_widget.settings

    @settings_property(False)
    def use_custom(self):
        ...

    @settings_property('white')
    def cust_f_color(self):
        ...

    @settings_property('black')
    def cust_b_color(self):
        ...

    @settings_property(100)
    def line_height(self):
        ...

    @settings_property('TsangerJinKai04 W03')
    def family(self):
        ...

    @settings_property('t_dark')
    def theme(self):
        ...

    @settings_property(20)
    def indent(self):
        ...

    @settings_property(15)
    def font_size(self):
        ...

    @settings_property(40)
    def margin(self):
        ...

    @settings_property(2)
    def letter_spacing(self):
        ...

    @pyqtSlot(str)
    def _change(self, color_name: str) -> None:
        if self.sender() == self.text_browser._text_color:
            self.pushButton_5.setStyleSheet(
                'background:%s; border:1px solid white;border-radius:3px' %
                color_name)
            self.cust_f_color = color_name
        elif self.sender() == self.text_browser._bkg_color:
            self.pushButton_4.setStyleSheet(
                'background:%s; border:1px solid white;border-radius:3px' %
                color_name)
            self.cust_b_color = color_name
        if self.checkBox_2.isChecked():
            self.task_widget.setReadStyle(self.cust_b_color, self.cust_f_color,
                                          None)

    @pyqtSlot(int)
    def _changeState(self, state: int) -> None:
        if state == Qt.Checked:
            self.task_widget.setReadStyle(self.cust_b_color, self.cust_f_color,
                                          None)
            self.use_custom = True
        else:
            self.use_custom = False

    def __init__(self, *args, **kwargs):
        self.task_widget: TaskWidget = kwargs.pop('task_widget', None)
        self.text_browser: TaskReadBrowser = kwargs.pop('text_browser', None)
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.updatePage()

        self.slider_groups = QButtonGroup()
        self.slider_groups.addButton(self.fz_plus)
        self.slider_groups.addButton(self.fz_subtract)
        self.slider_groups.addButton(self.ls_plus)
        self.slider_groups.addButton(self.ls_subtract)
        self.slider_groups.addButton(self.indent_plus)
        self.slider_groups.addButton(self.indent_subtract)
        self.slider_groups.addButton(self.margin_plus)
        self.slider_groups.addButton(self.margin_subtract)
        self.slider_groups.buttonClicked.connect(self.sliderGroup)

        self.checkBox_2.stateChanged.connect(self._changeState)
        f_width = self.label_10.fontMetrics().width('背景色') * 2
        f_height = self.label_10.fontMetrics().height() * 1.5
        self.pushButton_4.clicked.connect(
            lambda: self.text_browser.show_bkg_color(self.cust_b_color))
        self.pushButton_5.clicked.connect(
            lambda: self.text_browser.show_text_color(self.cust_f_color))
        self.pushButton_4.setFixedSize(f_width, f_height)
        self.pushButton_5.setFixedSize(f_width, f_height)
        self.text_browser._text_color.selected_color.connect(self._change)
        self.text_browser._bkg_color.selected_color.connect(self._change)

        fm = QFontMetrics(QFont('宋体', 15, QFont.Bold))
        self.frame.setFixedHeight(60)
        self.pushButton.setFixedHeight(60)
        self.pushButton_2.setFixedHeight(60)
        self.pushButton_3.setFixedHeight(60)
        self.pushButton_6.setFixedHeight(60)

        button_group = QButtonGroup()
        button_group.addButton(self.pushButton)
        button_group.addButton(self.pushButton_2)
        button_group.addButton(self.pushButton_3)
        button_group.addButton(self.pushButton_6)
        button_group.buttonClicked.connect(self.groupPolicy)
        self.button_group = button_group
        fm = self.lineEdit.fontMetrics()
        self.lineEdit.setFixedHeight(fm.height() * 2)
        self.up_letter.setFixedHeight(fm.height() * 2)
        self.down_letter.setFixedHeight(fm.height() * 2)
        self.horizontalSlider.valueChanged.connect(self.updateFontSize)
        self.horizontalSlider_2.valueChanged.connect(self.updateLineSpace)
        self.horizontalSlider_3.valueChanged.connect(self.updateIndentWidth)
        self.horizontalSlider_4.valueChanged.connect(self.updateMarginWidth)
        self.pushButton.setChecked(True)
        button_group_2 = QButtonGroup()
        button_group_2.addButton(self.t_1)
        button_group_2.addButton(self.t_2)
        button_group_2.addButton(self.t_3)
        button_group_2.addButton(self.t_4)
        button_group_2.addButton(self.t_5)
        button_group_2.addButton(self.t_6)
        button_group_2.addButton(self.t_dark)
        button_group_2.addButton(self.t_8)
        button_group_2.buttonClicked.connect(self._changeReadStyle)
        self.bg_2 = button_group_2
        theme_size = QSize(50, 50)
        for i in range(1, 9):
            if i != 7:
                getattr(self, 't_%s' % i).setFixedSize(theme_size)
            else:
                self.t_dark.setFixedSize(theme_size)
        b_3 = QButtonGroup()
        b_3.addButton(self.up_letter)
        b_3.addButton(self.down_letter)
        b_3.buttonClicked.connect(self._changeletterPolicy)
        self.b_3 = b_3

        self.lineEdit.setValidator(FInValidator(0, 100, self))
        self.lineEdit.setText(str(self.letter_spacing))
        self.lineEdit.returnPressed.connect(
            lambda: self._changeLetter(self.lineEdit.text()))
        self.scrollArea.verticalScrollBar().setStyleSheet(s_list_style)

        font_combo = self.font_combo
        fm = QFontMetrics(QFont('微软雅黑', 10))
        font_combo.addFontTag('苍耳今楷', self.task_widget.novel_widget.cust_font)
        font_combo.addFontTag('华文楷体')
        font_combo.addFontTag('华文细黑')
        font_combo.addFontTag('方正姚体')
        font_combo.addFontTag('方正颜宋', QFont(self.task_widget.novel_widget.cust_familys[1]))
        font_combo.addFontTag('方正悠宋', QFont(self.task_widget.novel_widget.cust_familys[-1]))
        font_combo.addFontTag('微软雅黑')
        font_combo.addFontTag('新宋体')
        font_combo.addFontTag('宋体')
        font_combo.addFontTag('仿宋')
        font_combo.addFontTag('黑体')
        font_combo.addFontTag('等线')
        font_combo.addFontTag('幼圆')
        font_combo.addFontTag('楷体')
        font_combo.setFixedHeight(fm.height() * 1.3)
        font_combo.setFixedWidth(fm.widthChar('微') * 10)
        font_combo.setCurrent(self.family)
        font_combo.list_widget.verticalScrollBar().setStyleSheet(s_list_style)
        self.font_combo.currentIndexChanged.connect(self.updateFont)

        self.label_4.hide() # bold
        self.checkBox.hide() # bold
        self.label_9.hide() # brightness
        self.frame_10.hide() # brightness

    @pyqtSlot(str)
    def _changeLetter(self, v: str) -> None:
        space = int(v) if v else 0
        message = self.text_browser.messages
        font_size = self.horizontalSlider.value()
        indent_size = self.horizontalSlider_3.value()
        margin_size = self.horizontalSlider_4.value()

        html = self.text_browser.renderOk(messages=message,
                                          line_height=self.line_height,
                                          indent_size=indent_size,
                                          margin_size=margin_size,
                                          font_size=font_size,
                                          letter_spacing=space,
                                          font_family=self.family)
        temp = self.task_widget._inf.novel_read_infos.get('percent', 0)
        self.text_browser.setHtml(html)
        self.text_browser.verticalScrollBar().setValue(
            temp * self.text_browser.total_length())
        self.letter_spacing = space

    @pyqtSlot()
    def _changeletterPolicy(self):
        valid = self.lineEdit.validator()
        top, bottom = valid.top(), valid.bottom()
        checked = self.b_3.checkedButton()
        value = int(self.lineEdit.text()) if self.lineEdit.text() else 0
        if checked == self.up_letter:
            if bottom <= value + 1 <= top:
                self.lineEdit.setText(str(value + 1))
                self._changeLetter(str(value + 1))
        elif checked == self.down_letter:
            if bottom <= value - 1 <= top:
                self.lineEdit.setText(str(value - 1))
                self._changeLetter(str(value - 1))

    @pyqtSlot()
    def _changeReadStyle(self) -> None:
        self.use_custom = False
        self.checkBox_2.setChecked(False)
        checked = self.bg_2.checkedButton()
        self.theme = checked.objectName()
        self.changeReadTheme(checked.objectName())

    def changeReadTheme(self, theme: str) -> None:
        checked = getattr(self, theme)
        if checked == self.t_dark:
            bkg_color = '#161819'
            text_color = '#666666'
        else:
            styled = checked.styleSheet()
            temp = styled.split(';')
            bkg_color = temp[0].split(':')[-1]
            text_color = temp[-1].split(':')[-1]
        self.task_widget.setReadStyle(bkg_color, text_color, theme)

    def updatePage(self) -> None:
        self.label.setText('字体大小: %s' % self.font_size)  # font_size
        self.label_2.setText('多倍行距: %.1f' %
                             (self.line_height / 100))  # line_spacing
        self.label_5.setText('首行缩进: %s' % self.indent)  # indent
        self.label_6.setText('边距大小: %s' % self.margin)  # margin_size
        self.horizontalSlider.setValue(self.font_size)
        self.horizontalSlider_2.setValue(self.line_height)
        self.horizontalSlider_3.setValue(self.indent)
        self.horizontalSlider_4.setValue(self.margin)
        self.pushButton_4.setStyleSheet(
            'background:%s; border:1px solid white;border-radius:3px' %
            self.cust_b_color)
        self.pushButton_5.setStyleSheet(
            'background:%s; border:1px solid white;border-radius:3px' %
            self.cust_f_color)
        getattr(self, self.theme).setChecked(True)
        self.lineEdit.setText(str(self.letter_spacing))
        self.font_combo.setCurrent(self.family)
        self.checkBox_2.setChecked(self.use_custom)

    @pyqtSlot(int)
    def updateFont(self, index: int) -> None:
        family = self.font_combo.getFontFamily(index)
        self.text_browser.font_family = family
        message = self.text_browser.messages
        margin_size = self.horizontalSlider_4.value()
        letter_spacing = self.letter_spacing
        html = self.text_browser.renderOk(line_height=self.line_height,
                                          messages=message,
                                          indent_size=self.indent,
                                          margin_size=margin_size,
                                          font_size=self.font_size,
                                          letter_spacing=letter_spacing,
                                          font_family=family)
        temp = self.task_widget._inf.novel_read_infos.get('percent', 0)
        self.text_browser.setHtml(html)
        self.text_browser.verticalScrollBar().setValue(
            temp * self.text_browser.total_length())
        self.family = family

    def updateFontSize(self, value: int) -> None:
        self.label.setText(f'字体大小: {value}')
        message = self.text_browser.messages
        indent = self.horizontalSlider_3.value()
        margin_size = self.horizontalSlider_4.value()
        letter_spacing = self.letter_spacing
        html = self.text_browser.renderOk(line_height=self.line_height,
                                          messages=message,
                                          indent_size=indent,
                                          margin_size=margin_size,
                                          font_size=value,
                                          letter_spacing=letter_spacing,
                                          font_family=self.family)
        temp = self.task_widget._inf.novel_read_infos.get('percent', 0)
        self.text_browser.setHtml(html)
        self.text_browser.verticalScrollBar().setValue(
            temp * self.text_browser.total_length())
        self.font_size = value

    def updateLineSpace(self, value: int) -> None:
        self.label_2.setText(f'多倍行距: {value/100:.1f}')
        line_height = value
        message = self.text_browser.messages
        indent = self.horizontalSlider_3.value()
        margin_size = self.horizontalSlider_4.value()
        letter_spacing = self.letter_spacing
        html = self.text_browser.renderOk(line_height=value,
                                          messages=message,
                                          indent_size=indent,
                                          margin_size=margin_size,
                                          font_size=self.font_size,
                                          letter_spacing=letter_spacing,
                                          font_family=self.family)
        temp = self.task_widget._inf.novel_read_infos.get('percent', 0)
        self.text_browser.setHtml(html)
        self.text_browser.verticalScrollBar().setValue(
            temp * self.text_browser.total_length())
        self.line_height = line_height

    def updateIndentWidth(self, value: int) -> None:
        self.label_5.setText(f'首行缩进: {value}')
        message = self.text_browser.messages
        margin_size = self.horizontalSlider_4.value()
        font_size = self.horizontalSlider.value()
        letter_spacing = self.letter_spacing
        html = self.text_browser.renderOk(line_height=self.line_height,
                                          messages=message,
                                          indent_size=value,
                                          margin_size=margin_size,
                                          font_size=font_size,
                                          letter_spacing=letter_spacing,
                                          font_family=self.family)
        temp = self.task_widget._inf.novel_read_infos.get('percent', 0)
        self.text_browser.setHtml(html)
        self.text_browser.verticalScrollBar().setValue(
            temp * self.text_browser.total_length())
        self.indent = value

    def updateMarginWidth(self, value: int) -> None:
        self.label_6.setText(f'边距大小: {value}')
        message = self.text_browser.messages
        indent = self.horizontalSlider_3.value()
        font_size = self.horizontalSlider.value()
        letter_spacing = self.letter_spacing
        html = self.text_browser.renderOk(line_height=self.line_height,
                                          messages=message,
                                          indent_size=indent,
                                          margin_size=value,
                                          font_size=font_size,
                                          letter_spacing=letter_spacing,
                                          font_family=self.family)
        temp = self.task_widget._inf.novel_read_infos.get('percent', 0)
        self.text_browser.setHtml(html)
        self.text_browser.verticalScrollBar().setValue(
            temp * self.text_browser.total_length())
        self.margin = value

    def groupPolicy(self) -> None:
        check = self.button_group.checkedButton()
        if check == self.pushButton:
            self.stackedWidget.setCurrentIndex(0)
        elif check == self.pushButton_2:
            self.stackedWidget.setCurrentIndex(1)
        elif check == self.pushButton_3:
            self.stackedWidget.setCurrentIndex(2)
        elif check == self.pushButton_6:
            self.close()

    def sliderGroup(self) -> None:
        checked = self.slider_groups.checkedButton()
        if checked == self.fz_plus:
            self.horizontalSlider.setValue(self.horizontalSlider.value() + 1)
        elif checked == self.fz_subtract:
            self.horizontalSlider.setValue(self.horizontalSlider.value() - 1)
        elif checked == self.ls_plus:
            self.horizontalSlider_2.setValue(self.horizontalSlider_2.value() +
                                             10)
        elif checked == self.ls_subtract:
            self.horizontalSlider_2.setValue(self.horizontalSlider_2.value() -
                                             10)
        elif checked == self.indent_plus:
            self.horizontalSlider_3.setValue(self.horizontalSlider_3.value() +
                                             1)
        elif checked == self.indent_subtract:
            self.horizontalSlider_3.setValue(self.horizontalSlider_3.value() -
                                             1)
        elif checked == self.margin_plus:
            self.horizontalSlider_4.setValue(self.horizontalSlider_4.value() +
                                             1)
        elif checked == self.margin_subtract:
            self.horizontalSlider_4.setValue(self.horizontalSlider_4.value() -
                                             1)


class ChapterItemDelegate(QStyledItemDelegate):
    def __init__(self, chapter_widget: 'ChapterWidget',
                 task_widget: 'TaskWidget',
                 text_browser: TaskReadBrowser) -> None:
        super().__init__()
        self.chapter_widget = chapter_widget
        self.task_widget = task_widget
        self.text_browser = text_browser
        self.read_q: QDir = self.task_widget._inf.read_qdir()
        self.inf = self.task_widget._inf

    def paint(self, painter: QPainter, option: QStyleOptionViewItem,
              index: QModelIndex) -> None:
        rect = option.rect  # 目标矩形
        w, h = rect.width(), rect.height()
        pix_size = 20
        spacing = 10
        margin = 10
        text_rect = rect.adjusted(margin, 0, -(pix_size + margin + spacing), 0)
        url_index = index.data(Qt.UserRole)
        pixmap = self.chapter_widget.cached_pix.scaled(
            pix_size, pix_size, transformMode=Qt.SmoothTransformation)
        # m+ t+ s+ p+ m = w
        x = margin + text_rect.width() + spacing
        y = (h - pix_size) / 2
        pix_rect = rect.adjusted(x, y, -(w - margin), -y)
        super().paint(painter, option, index)
        # option.state & QStyle.State_HasFocus: # checked
        flag = self.text_browser.read_loader.chapter_exists(
            url_index, self.read_q, self.inf)
        if flag:
            painter.drawPixmap(pix_rect, pixmap)


class ChapterWidget(QWidget, ChapterUi):  # 阅读详情页面
    '''
    parent: TaskWidget
    '''
    def __init__(self,
                 task_widget: 'TaskWidget',
                 text_browser: TaskReadBrowser,
                 info: InfoObj = None):
        super().__init__()
        self.setupUi(self)
        self.cached_pix = QPixmap(CommonPixmaps.chapter_cached_state).scaled(
            35, 35, transformMode=Qt.SmoothTransformation)
        self.pushButton.hide()
        self.task_widget = task_widget
        self.text_browser = text_browser
        self.info = info
        self.latest_book = info.novel_name + f'[{info.novel_site}]'
        button_group = QButtonGroup()
        button_group.addButton(self.pushButton_2)
        button_group.addButton(self.pushButton_3)
        button_group.addButton(self.pushButton_4)
        button_group.buttonClicked.connect(self.buttonsPolicy)
        self.pushButton.clicked.connect(
            lambda: self.task_widget.stackedWidget.setCurrentIndex(1))
        self.pushButton.setHoverLeave(CommonPixmaps.hl_leftarrow_svg, 'white',
                                      '#999999')
        self.pushButton_5.setHoverLeave(CommonPixmaps.hl_fresh_svg, 'white',
                                        '#999999')
        self.button_group = button_group
        self.frame.setFixedHeight(60)
        self.pushButton_2.setFixedHeight(56)
        self.pushButton_3.setFixedHeight(56)
        self.pushButton_4.setFixedHeight(56)
        self.listWidget.setStyleSheet(c_list_style)
        self.listWidget.verticalScrollBar().setStyleSheet(s_list_style)
        self.listWidget_2.setStyleSheet(c_list_style)
        self.listWidget_2.verticalScrollBar().setStyleSheet(s_list_style)
        self.textBrowser.verticalScrollBar().setStyleSheet(s_list_style)
        self.set2page()
        self.set3page()
        self.msg_label.setText(
            f'当前阅读: {self.text_browser.current_chapter} -- 共{self.task_widget._inf.chapter_count()}章'
        )
        self.listWidget.itemClicked.connect(self.gotoByChapter)
        self.listWidget_2.itemClicked.connect(self.gotoByBookMark)

    def buttonsPolicy(self) -> None:
        inf = self.task_widget._inf
        book_name = inf.novel_name + f'[{inf.novel_site}]'
        check = self.button_group.checkedButton()
        if check == self.pushButton_2:
            self.stackedWidget.setCurrentIndex(0)
            self.set1page()
        elif check == self.pushButton_3:
            self.stackedWidget.setCurrentIndex(1)
            self.listWidget.setFocus(True)
            if self.latest_book != self.text_browser.current_book:
                self.set2page()
        elif check == self.pushButton_4:
            self.stackedWidget.setCurrentIndex(2)
            self.listWidget_2.setFocus(True)
            if self.latest_book != self.text_browser.current_book:
                self.set3page()
                self.latest_book = book_name

    def set1page(self) -> None:
        try:
            info = self.task_widget._inf
            novel_name = info.novel_name + f'[{info.novel_site}]'
            self.label_2.setText(novel_name)
            self.label_2.setFont(QFont('微软雅黑', 14))
            self.label.setPixmap(self.task_widget.info_img.pixmap())
            cust_font = self.task_widget.novel_widget.cust_font
            cust_font.setPointSize(14)
            self.textBrowser.setFont(cust_font)
            html = f'<p style="text-indent: 20px; margin-left:10px;margin-right:10px">{info.novel_introutced}</p>'
            self.textBrowser.clear()
            self.textBrowser.setHtml(html)
        except Exception as e:
            print(e)

    def set2page(self) -> None:
        self.listWidget.clear()
        self.listWidget.setItemDelegate(
            ChapterItemDelegate(self, self.task_widget, self.text_browser))
        self.listWidget.setAttribute(Qt.WA_StyledBackground, True)
        info = self.task_widget.info
        read_qir = info.read_qdir()
        exists_chapters = self.text_browser.read_loader.exits_chapters(
            read_qir, info)
        self.listWidget.setFont(QFont('微软雅黑', 10))
        for index, tupled in enumerate(info.novel_chapter_urls):
            url, chapter, state = tupled
            add = True if index in exists_chapters else False
            self.add_chapter(chapter)

    def add_chapter(self, chapter_name: str) -> None:
        count = self.listWidget.count()
        item = QListWidgetItem()
        item.setText(chapter_name)
        item.setData(Qt.UserRole, count)  # index
        item.setData(Qt.UserRole + 1, chapter_name)  # chapter
        item.setSizeHint(QSize(10, 45))
        self.listWidget.addItem(item)

    def set3page(self) -> None:
        self.listWidget_2.clear()
        info = self.task_widget._inf
        self.listWidget_2.setFont(QFont('微软雅黑', 10))
        book_marks: List[Markup] = info.novel_read_infos.get('book_marks', [])
        for markup in book_marks:
            self.add_book_mark(markup)

    def add_book_mark(self, book_mark: Markup) -> None:
        item = QListWidgetItem()

        percent = book_mark.percent
        text = '(已阅读:%.2f%%)' % (percent * 100) if percent is not None else ''
        content = book_mark.content
        content = ': %s' % content if content else ''
        msg = book_mark.chapter + text + content
        fm = QFontMetrics(item.font())
        text = fm.elidedText(msg, Qt.ElideRight, self.width() - 60)

        item.setData(Qt.UserRole, book_mark)
        item.setData(Qt.UserRole + 1, msg)
        item.setSizeHint(QSize(10, 45))
        item.setText(text)
        self.listWidget_2.addItem(item)

    def resizeEvent(self, event) -> None:
        for i in range(self.listWidget_2.count()):
            item = self.listWidget_2.item(i)
            book_mark = item.data(Qt.UserRole)
            percent = book_mark.percent
            text = '(已阅读:%.2f%%)' % (percent *
                                     100) if percent is not None else ''
            content = book_mark.content
            content = ': %s' % content if content else ''
            msg = book_mark.chapter + text + content
            fm = QFontMetrics(item.font())
            text = fm.elidedText(msg, Qt.ElideRight, self.width() - 40)
            item.setText(text)
        if self.stackedWidget.currentIndex() == 1:
            self.listWidget.setFocus(True)
        elif self.stackedWidget.currentIndex() == 2:
            self.listWidget_2.setFocus(True)
        return super().resizeEvent(event)

    def remove_bookmark(self, book_mark: Markup) -> bool:
        flag = -1
        for index in range(self.listWidget_2.count()):
            item = self.listWidget_2.item(index)
            if book_mark == item.data(Qt.UserRole):
                flag = index
                break
        if flag >= 0:
            take_item = self.listWidget_2.item(flag)
            self.listWidget_2.removeItemWidget(take_item)
            self.listWidget_2.takeItem(flag)
            return True
        return False

    @pyqtSlot(QListWidgetItem)
    def gotoByBookMark(self, item: QListWidgetItem) -> None:
        book_mark: Markup = item.data(Qt.UserRole)
        self.pushButton.click()
        self.text_browser.jump_chapter(book_mark.index, book_mark.percent)
        self.msg_label.setText(
            f'当前阅读: {book_mark.chapter} -- 共{self.listWidget.count()}章')
        self.task_widget.stackedWidget_2.setCurrentIndex(0)
        # self.text_browser.textCursor().select()

    @pyqtSlot(QListWidgetItem)
    def gotoByChapter(self, item: QListWidgetItem) -> None:
        index = item.data(Qt.UserRole)
        chapter = item.data(Qt.UserRole + 1)
        self.pushButton.click()
        self.text_browser.jump_chapter(index)
        self.msg_label.setText(
            f'当前阅读: {chapter} -- 共{self.listWidget.count()}章')
        self.task_widget.stackedWidget_2.setCurrentIndex(0)


class IntroutcedHandle(object):
    def __init__(self, inf: InfoObj):
        self.inf = inf
        self.spider = get_spider_byname(self.inf.novel_site)

    def processIntroutced(self) -> str:
        if self.spider == EightSpider:
            introutced = self.inf.novel_introutced.replace('ad2502()', '')
            return introutced
        return self.inf.novel_introutced.replace('\n', '<br>')


class StyleHandler(object):  # 设置阅读主题

    # bar, bar_text
    bar_color = {
        't_1': ('#CCC7BC', Qt.black),
        't_2': ('#CCC199', Qt.black),
        't_3': ('#CAD9CA', Qt.black),
        't_4': ('#BEC9CC', Qt.black),
        't_5': ('#CCC1C0', Qt.black),
        't_6': ('#BFBFBF', Qt.black),
        't_dark': (Qt.black, Qt.white),
        't_8': ('#CCCCCC', Qt.black)
    }

    theme_image = {
        't_1': CommonPixmaps.theme_t_1,
        't_2': CommonPixmaps.theme_t_2,
        't_3': CommonPixmaps.theme_t_3,
        't_4': CommonPixmaps.theme_t_4,
        't_5': CommonPixmaps.theme_t_5,
        't_6': CommonPixmaps.theme_t_6,
        't_dark': CommonPixmaps.theme_t_dark,
        't_8': CommonPixmaps.theme_t_8
    }

    def getMsgColor(self, theme: str) -> Any:
        return self.bar_color.get(theme)[1]

    def __init__(self, textbrowser, task_wiget, novel_widget,
                 main_gui) -> None:
        self.textbrowser = textbrowser
        self.task_widget = task_wiget
        self.novel_widget = novel_widget
        self.main_gui = main_gui

    def _set_browser_style(self, bkg_color: ColorTypes, text_color: ColorTypes,
                           theme: str, hover_color: ColorTypes) -> str:
        scroll_style = '''
                QScrollBar:vertical {
                    background: %s;
                    padding: 0px;
                    border-radius: 3px;
                    max-width: 12px;
                    background-image: url(%s);
                    background-repeat: repeat-xy;
                }
                QScrollBar::handle:vertical {
                    background: %s;
                    min-height: 20px;
                    border-radius: 3px;
                }
                QScrollBar::add-page:vertical {
                    background: none;
                }
                QScrollBar::sub-page:vertical {
                    background: none;
                }
                QScrollBar::add-line:vertical {
                    background: none;
                }
                QScrollBar::sub-line:vertical {
                    background: none;
                }''' % (bkg_color, self.theme_image.get(theme, ''), text_color)
        text_style = '''QTextBrowser{border-left:none;
            border-bottom: none;
            border-right: none;
            border-top: none;
            background-color: %s;
            color: %s;
            selection-color: %s;
            selection-background-color: %s;
            background-image: url(%s);
            background-repeat: repeat-xy;
            }''' % (bkg_color, text_color, bkg_color, text_color,
                    self.theme_image.get(theme, ''))
        self.textbrowser.setStyleSheet(text_style)
        self.textbrowser.verticalScrollBar().setStyleSheet(scroll_style)

    def _set_taskwidget_style(self, bkg_color: ColorTypes,
                              text_color: ColorTypes, theme: str,
                              hover_color: ColorTypes) -> None:
        bar_frame_style = '''
            QPushButton{border:none; color: %s; background-color:transparent}
            QPushButton:hover{border:none; color:%s}
            QFrame{background-color: %s; color: %s}''' % (
            text_color, hover_color, bkg_color, text_color)
        self.task_widget.frame_11.setStyleSheet(bar_frame_style)
        v = self.bar_color.get(theme, None)
        v = v if v is not None else (bkg_color, text_color)
        if v:
            self.task_widget.readbar_widget.setBarColor(v[0])
            self.task_widget.readbar_widget.setTextColor(v[1])

    def _set_novelwiget_style(self, bkg_color: ColorTypes,
                              text_color: ColorTypes, theme: str,
                              hover_color: ColorTypes) -> None:
        self.novel_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.novel_widget.setContentsMargins(0, 0, 0, 0)

    def _set_maingui_style(self, bkg_color: ColorTypes, text_color: ColorTypes,
                           theme: str, hover_color: ColorTypes):
        self.main_gui.setStyleSheet('FramelessWindow{background-color: %s}' %
                                    bkg_color)

    def setReadStyle(self,
                     bkg_color: ColorTypes,
                     text_color: ColorTypes,
                     theme: str,
                     hover_color: ColorTypes = None) -> None:
        bkg_color = QColor(bkg_color)
        text_color = QColor(text_color)
        b_color = f'rgba({bkg_color.red()}, {bkg_color.green()}, {bkg_color.blue()}, {bkg_color.alpha()})' if bkg_color.alpha(
        ) < 255 else bkg_color.name()
        t_color = f'rgba({text_color.red()},{text_color.green()},{text_color.blue()},{ text_color.alpha()})' if text_color.alpha(
        ) < 255 else text_color.name()

        if hover_color is None:  # 默认增加50, 亮度增加
            h, s, v, a = text_color.getHsv()
            hsva = h, s, v + 50, a
            hover_color = QColor()
            hover_color.setHsv(*hsva)
            hover_to_rgb = hover_color.toRgb()
        else:
            hover_to_rgb = hover_color
        h_color = f'rgba({hover_to_rgb.red()}, {hover_to_rgb.green()}, {hover_to_rgb.blue()}, {hover_to_rgb.alpha()})' if hover_to_rgb.alpha(
        ) < 255 else hover_to_rgb.name()

        self._set_browser_style(b_color, t_color, theme, h_color)
        self._set_maingui_style(b_color, t_color, theme, h_color)
        self._set_novelwiget_style(b_color, t_color, theme, h_color)
        self._set_taskwidget_style(b_color, t_color, theme, h_color)



@qmixin
class TaskWidget(QWidget, Ui_Form):

    remove_signal = pyqtSignal()
    down_signal = pyqtSignal(InfoObj)

    def __init__(self, inf: InfoObj):
        super().__init__()
        self.setupUi(self)
        self.init(inf)

    def textMenu(self) -> None:
        clip = QApplication.clipboard()
        menu = QMenu(self.info_introduced)
        menu.setStyleSheet(menu_style)
        a1 = menu.addAction('复制')
        a2 = menu.addAction('选择全部')
        a1.setShortcut('ctrl+c')
        a2.setShortcut('ctrl+a')
        act = menu.exec_(QCursor.pos())
        if act == a1:
            txt = self.info_introduced.textCursor().selectedText()
            clip.setText(txt)
        elif act == a2:
            self.info_introduced.selectAll()

    def _setUpdateTitleMsg(self, novel_fresh_state: int) -> None:
        info = self._inf
        if novel_fresh_state == 0:  # 初始化
            msg = f'已订阅: {self.novel_widget.subscribeCount()}本小说'
            color = 'black'
        elif novel_fresh_state == 1:  # 更新成功
            msg = f'{info.novel_name}--已更新: {info.latest_chapter()}'
            color = 'darkgreen'
        elif novel_fresh_state == 2:  # 更新中
            msg = f'{info.novel_name}--更新中...'
            color = 'darkgreen'
        else:  # 更新失败
            msg = f'{info.novel_name}--更新失败'
            color = 'red'
        self.novel_widget.titleMsgInfo(msg, True, color)

    def _setFreshState(self, novel_fresh_state: int) -> None:
        try:
            self._setUpdateTitleMsg(novel_fresh_state)
            if novel_fresh_state == 0:  # 初始化
                self.fresh_button.setIcon(
                    QIcon(CommonPixmaps.novel_fresh_button))
                self.fresh_button.setToolTip('')
                self.info_title.setStyleSheet('color: black; font: bold 14pt')
            elif novel_fresh_state == 1:  # 更新成功
                self.fresh_button.setIcon(
                    QIcon(CommonPixmaps.novel_fresh_button))
                self.fresh_button.setToolTip('<b>更新成功</b>')
                self.info_title.setStyleSheet('color: black; font: bold 14pt')
            elif novel_fresh_state == 2:  # 更新中
                self.fresh_button.setGif(CommonPixmaps.gif_crawl_novel)
                self.fresh_button.setToolTip('<b>更新中...</b>')
                self.info_title.setStyleSheet('color: black; font: bold 14pt')
            else:  # 更新失败
                self.fresh_button.setIcon(QIcon(
                    CommonPixmaps.novel_fresh_fail))
                self.fresh_button.setToolTip('<b>更新失败</b>')
                self.info_title.setStyleSheet('color: red; font: bold 14pt')
        except Exception as e:
            print(e)

    @property
    def info(self):
        return self._inf

    @info.setter
    def info(self, new_inf: InfoObj):
        self._inf = new_inf

    def init(self, inf: InfoObj) -> None:
        self.blockSignals(True)
        self.in_read = None
        self._inf = inf
        self.label.setMinimumWidth(
            self.label.fontMetrics().width('300.98kb/s'))
        self.setStrWidth(self.label_2, '已选中: 100000个')
        self.info_introduced.setFont(self.novel_widget.cust_font)
        self.info_introduced.verticalScrollBar().setStyleSheet(
            listwidget_v_scrollbar)
        self.info_introduced.customContextMenuRequested.connect(self.textMenu)
        self.pushButton.clicked.connect(self.closeMessage)
        self.info_down.clicked.connect(self.download)
        self.info_title.setContextMenuPolicy(Qt.CustomContextMenu)
        self.label_17.setStyleSheet(f'color: {COLOR["undo"]}')
        self.pushButton_2.clicked.connect(self.previousInf)
        self.pushButton_3.clicked.connect(self.nextInf)
        self.pushButton_4.clicked.connect(self.restart)
        self.pushButton_5.clicked.connect(self.showChapters)
        self.pushButton_2.setShortcut('z')
        self.pushButton_3.setShortcut('c')
        self.msg_button.clicked.connect(self._showFailLogs)
        self.info_down.setFixedSize(QSize(30, 30))
        self.msg_button.setFixedSize(QSize(30, 30))
        if self._inf.novel_chapter_urls:
            self.frame_3.show()
        else:
            self.frame_3.hide()
        self.checkBox.stateChanged.connect(self.subscribePolicy)
        self.blockSignals(False)
        size = self.novel_widget.fresh_button.size()
        self.fresh_button.setFixedSize(size)
        self.read_button.setFixedSize(size.width() * 1.5, size.height())
        page_state = self.novel_widget.beforePageToTaskWidget()
        if page_state == PageState.subscribe_page:
            self.fresh_button.show()
        else:
            self.fresh_button.hide()
        self.fresh_button.clicked.connect(self.updateSubmit)
        get_subscribeLinkobj().fail_info_signal.connect(
            lambda info: self.subscribePageInitPolicy())
        self.read_button.clicked.connect(lambda: self.read_fromlatest())
        self.subscribePageInitPolicy()
        self.textbrowser_init()
        self.more_button.setHoverLeave(CommonPixmaps.hl_more_svg, ('white', ),
                                       ('#666666', ))
        self.chapters_button_2.setHoverLeave(CommonPixmaps.hl_menu_svg,
                                             ('white', ), ('#666666', ))
        self.markup_button.setHoverLeave(CommonPixmaps.hl_book_mark,
                                         ('white', ), ('#666666', ), 28)
        self.exit_button.setHoverLeave(CommonPixmaps.hl_exit_read,
                                       ('white', 'white'),
                                       ('#666666', '#666666'), (22, 22))
        self.next_button.setHoverLeave(CommonPixmaps.hl_next_chapter,
                                       ('white', ), ('#666666', ), (22, 30))
        self.prev_button.setHoverLeave(CommonPixmaps.hl_previous_chapter,
                                       ('white', ), ('#666666', ), (22, 30))
        self.skin_button.setHoverLeave(CommonPixmaps.hl_skin_svg, ('white'),
                                       ('#666666'), (30, 30))
        self.stackedWidget_2.addWidget(self.chapters_widget)
        self.stackedWidget.setCurrentIndex(0)
        self.exitButtonShowPolicy()
        self.sizedown_button.hide()
        self.sizeup_button.hide()
        self.exit_button.hide()
        self.style_handle = StyleHandler(self.textBrowser, self,
                                         self.novel_widget,
                                         self.novel_widget.main_gui)

    @lasyproperty
    def mark_button(self) -> QPushButton:
        button = QPushButton(self.textBrowser)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet('border: none; background:transparent')
        button.setIcon(
            QIcon(':/ico/Bookmark_tag_256px_1194046_easyicon.net.png'))
        button.hide()
        button.clicked.connect(self._remove)
        return button

    def save_read_infos(self) -> None:
        self._inf.dump_subscribe()

    def _remove(self) -> None:
        current_index = self.textBrowser.current_index
        current_chapter = self.textBrowser.current_chapter
        current_mark = self.textBrowser.current_markup
        theme = self.more_widget.theme
        msg_color = self.style_handle.getMsgColor(theme)
        if current_mark:
            if self.chapters_widget.remove_bookmark(current_mark):
                self._inf.remove_bookmark(current_mark.index,
                                          current_mark.chapter,
                                          current_mark.create_time)
                self.textBrowser.current_markup = None
                self.novel_widget.titleMsgInfo(
                    f'已移除书签: {current_mark.chapter}({current_mark.percent *100:.2f}%)',
                    True, msg_color)
        flag: Markup = self._inf.bookmark_exists(current_index,
                                                 current_chapter)
        if flag:
            self.textBrowser.current_markup = flag
            self.mark_button.setToolTip(
                f'当前书签: {flag.chapter}({flag.percent * 100:.2f}%)')
        else:
            self.mark_button.hide()

    def updateRequestState(self) -> None:  # 更新翻页相关状况
        index = self.textBrowser.current_index
        chapter_listwidget: QListWidget = self.chapters_widget.listWidget
        chapter_listwidget.setCurrentRow(index)

    @lasyproperty
    def more_widget(self) -> QWidget:
        widget = MoreWidget(self.novel_widget.main_gui,
                            task_widget=self,
                            text_browser=self.textBrowser)
        widget.hide()
        return widget

    @lasyproperty
    def chapters_widget(self) -> QWidget:
        widget = ChapterWidget(self, self.textBrowser, self._inf)
        widget.setContentsMargins(0, 0, 0, 0)
        return widget

    def exitButtonShowPolicy(self) -> None:
        if self._isSubmitWidget():
            self.read_button.show()
            index = self._inf.novel_read_infos.get('index', -1)
            if index > -1:
                msg = f'继续阅读:{self._inf.novel_chapter_urls[index][1]}'
                fm = self.read_button.fontMetrics()
                elid = fm.elidedText(msg, Qt.ElideRight,
                                     self.read_button.width() - 10)
                self.read_button.setText(elid)
                self.read_button.setToolTip(f'<b>{msg}</b>')
            else:
                self.read_button.setText('开始阅读')
                self.read_button.setToolTip('<b>开始阅读</b>')
        else:
            self.read_button.hide()

    def showChaptersWidget(self, state: bool) -> None:
        if state:
            self.update()
            self.stackedWidget.setCurrentIndex(1)
            self.stackedWidget_2.setCurrentIndex(1)
            self.chapters_widget.pushButton_2.click()
            exists__count = len(self.textBrowser.exists_chapters())
            self.chapters_widget.msg_label.setText(
                f'当前阅读: {self.textBrowser.current_chapter} -- 共{self._inf.chapter_count()}章 (已缓存{exists__count}章)'
            )

    def _show_more_widget(self) -> None:
        w, h = self.novel_widget.main_gui.width(
        ), self.novel_widget.main_gui.height()
        self.more_widget.setFixedWidth(w * 1 / 2)
        self.more_widget.setFixedHeight(h * 2 / 3)
        self.more_widget.move(w * .5, h / 3 - self.frame_11.height() +
                              1)  # border: 1px
        self.more_widget.show()

    def showMoreWidget(self, state: bool) -> None:
        if state:
            self.more_widget.updatePage()
            self._show_more_widget()
            self.more_widget.pushButton.click()
        else:
            self.more_widget.hide()

    def _show_mark_button(self) -> None:
        _w = self.textBrowser.width() - 40
        flag = self.textBrowser.current_markup
        if flag:
            self.mark_button.setToolTip(
                f'当前书签: {flag.chapter}({flag.percent * 100:.2f}%)')
        self.mark_button.setGeometry(_w, 0, 20, 20)
        self.mark_button.show()

    def addMarkUp(self) -> None:
        if self.mark_button.isHidden():
            self._show_mark_button()
            self.mark_button.show()
        current = self.textBrowser.current_index
        chapter = self.textBrowser.current_chapter
        percent = self._inf.novel_read_infos.get('percent', 0)
        markup = Markup(current,
                        chapter,
                        percent,
                        content=self.textBrowser.selectionText())
        theme = self.more_widget.theme
        msg_color = self.style_handle.getMsgColor(theme)
        self._inf.novel_read_infos.setdefault('book_marks', [])
        self._inf.novel_read_infos['book_marks'].append(markup)
        self.chapters_widget.add_book_mark(markup)
        self.mark_button.setToolTip(
            f'当前书签: {markup.chapter}({markup.percent * 100:.2f}%)')
        self.novel_widget.titleMsgInfo(
            f'已添加书签: {markup.chapter}({markup.percent * 100:.2f}%)', True,
            msg_color)

    @pyqtSlot(int)
    def updatePercent(self, value: int) -> None:
        percent = round(value / self.textBrowser.total_length(), 4)
        if percent >= 0.99:
            percent = 1
        self._inf.novel_read_infos['percent'] = percent
        msg = self.textBrowser.current_chapter + '(%.2f%%)' % (percent * 100)
        self.chapter_label.setText(msg)

    def read_fromlatest(self, target: int = None, jump: bool = False) -> None:
        self.in_read = True
        self.novel_widget.setSearchBarVisable(False)
        self.novel_widget.main_gui.titleBar.hide()
        self.stackedWidget.setCurrentIndex(1)
        self.textBrowser.task_widget = self
        self.chapter_label.setText('')
        chapter_name = self._inf.novel_read_infos.get('chapter', '')
        indent = self.more_widget.indent
        margin = self.more_widget.margin
        font_size = self.more_widget.font_size
        index = target if target is not None else self._inf.novel_read_infos.get(
            'index', 0)
        theme = self.more_widget.theme
        family = self.more_widget.family
        letter_spacing = self.more_widget.letter_spacing
        book_name = self._inf.novel_name + f'  [{self._inf.novel_site}]'
        line_height = self.more_widget.line_height
        self.readbar_widget.book_name = book_name
        if self.more_widget.use_custom:
            self.setReadStyle(self.more_widget.cust_b_color,
                              self.more_widget.cust_f_color, None)
        else:
            self.more_widget.changeReadTheme(theme)

        flag = 0 if jump == False else 2
        if jump:
            self.textBrowser.jump_percent = 0
        self.textBrowser.request_chapter(index, chapter_name, book_name,
                                         family, indent, margin, font_size,
                                         letter_spacing, line_height, flag)

    def _readbarClick(self) -> None:
        if self.stackedWidget_2.currentIndex() == 1:
            self.stackedWidget_2.setCurrentIndex(0)
        else:
            self.exit_button.click()

    def textbrowser_init(self) -> None:
        main_gui = self.novel_widget.main_gui
        self.readbar_widget.task_widget = self
        self.readbar_widget.exit_button.clicked.connect(self._readbarClick)
        self.readbar_widget.windowClosed.connect(main_gui.close)
        self.readbar_widget.windowMinimumed.connect(main_gui.showMinimized)
        self.readbar_widget.windowMaximumed.connect(main_gui.showMaximized)
        self.readbar_widget.windowNormaled.connect(main_gui.showNormal)
        self.readbar_widget.windowMoved.connect(main_gui.move)
        font = self.novel_widget.cust_font
        font.setPointSize(13)
        fm = QFontMetrics(font)
        width = fm.width('第一章 我草拟的么大手动阀示范点士大夫的')
        self.chapter_label.setFixedWidth(width)
        self.chapter_label.setFont(QFont('微软雅黑', 10, QFont.Bold))
        self.textBrowser.task_widget = self
        self.textBrowser.setFont(font)
        self.text_buttons = QButtonGroup(self)
        self.text_buttons.addButton(self.sizedown_button)
        self.text_buttons.addButton(self.sizeup_button)
        self.text_buttons.addButton(self.markup_button)
        self.text_buttons.addButton(self.more_button)
        self.text_buttons.addButton(self.next_button)
        self.text_buttons.addButton(self.prev_button)
        self.text_buttons.addButton(self.chapters_button_2)
        self.text_buttons.addButton(self.exit_button)
        self.text_buttons.addButton(self.skin_button)
        self.text_buttons.buttonClicked.connect(self.readButtonsPolicy)
        self.textBrowser.verticalScrollBar().valueChanged.connect(
            self.updatePercent)
        self.textBrowser.verticalScrollBar().setStyleSheet(read_v_style)

    def readButtonsPolicy(self) -> None:
        checked = self.text_buttons.checkedButton()
        if checked == self.sizeup_button:
            font = self.textBrowser.font()
            size = font.pointSize() + 1
            new_font = QFont(font)
            new_font.setPointSize(size)
            self.textBrowser.setFont(new_font)
        elif checked == self.sizedown_button:
            font = self.textBrowser.font()
            size = font.pointSize() - 1
            new_font = QFont(font)
            new_font.setPointSize(size)
            self.textBrowser.setFont(new_font)
        elif checked == self.more_button:
            self.chapters_widget.hide()
            self.showMoreWidget(True)
        elif checked == self.markup_button:
            self.addMarkUp()
        elif checked == self.prev_button:
            self.textBrowser.preview_chapter()
        elif checked == self.next_button:
            self.textBrowser.next_chapter()
        elif checked == self.chapters_button_2:
            self.showChaptersWidget(True)
            self.more_widget.hide()
        elif checked == self.exit_button:
            self.stackedWidget.setCurrentIndex(0)
            self.novel_widget.main_gui.styleRead()
            self.more_widget.hide()
            self.novel_widget.main_gui.titleBar.show()
            self.exitButtonShowPolicy()
            self._inf.dump_subscribe()
            self.in_read = False
        elif checked == self.skin_button:
            self.chapters_widget.hide()
            self.showMoreWidget(True)
            self.more_widget.pushButton_2.click()

    def load_chapter_init(self, chapter_name: str) -> None:
        self.chapter_label.setText(chapter_name)

    def _isSubmitWidget(self) -> bool:
        page_state: PageState = self.novel_widget.beforePageToTaskWidget()
        flag = self.info.novel_subs_url in self.novel_widget.subscribe_urls
        return all([
            page_state == PageState.subscribe_page,
            self.info._is_file == False, flag
        ])

    def subscribePageInitPolicy(self, fail_msg: bool = True) -> None:
        if self._isSubmitWidget():
            self._setFreshState(self._inf.novel_fresh_state)

    def updateSubmit(self) -> None:
        subscribe_obj = self.novel_widget.subscribe_obj
        if subscribe_obj.updateSubscribeLinks([self._inf]):
            self.novel_widget.titleMsgInfo(
                f'{self.info.novel_name}--抓取最新信息...', True, 'darkgreen')
            self.fresh_button.setGif(CommonPixmaps.gif_crawl_novel)

    def updateSubmitPage(self, info: InfoObj) -> None:
        if info.chapter_count() > self.info.chapter_count():
            self.info_title.setStyleSheet(
                'QLabel{font: bold 14pt; color: darkgreen}')
            self.info_img.setChaptersState(True)
        else:
            self.info_title.setStyleSheet(
                'QLabel{font: bold 14pt; color: black}')
            self.info_img.setChaptersState(False)
        if info.novel_subs_url == self.info.novel_subs_url:
            self.fresh_button.setIcon(
                QIcon(':/ico/refresh_173px_1188146_easyicon.net.png'))
        if info.novel_chapter_urls and not info._is_file:
            self.frame_3.show()
            self.label_2.setText(f'已选中: %s个' % info.selected_count())
        else:
            self.frame_3.hide()
        if info._is_file == False and len(info.novel_chapter_urls) == 0:
            self.fresh_button.show()
            self.fresh_button.setIcon(QIcon(CommonPixmaps.novel_fresh_fail))
            self.fresh_button.setToolTip('')
        self._setFreshState(info.novel_fresh_state)

    def _showFailLogs(self) -> None:
        inf = self._inf
        novel_widget = inf.novel_app
        novel_widget.pop_dialog.textBrowser.clearAllLines()  # 日志清除
        fail_edit = novel_widget.pop_dialog.fail_edit
        fail_edit.clearAllLines()
        messages = inf.novel_temp_data.get('log_msgs', None)
        if messages:
            for msg, level, msg_time in messages:
                fail_edit.forceLog(msg, level, extra={'mytime': msg_time})
            novel_widget.main_gui.showFail()

    def _downBeforeFlag(self) -> None:
        self.info_down.setIconSize(QSize(28, 28))
        self.info_down.setIcon(
            QIcon(':/ico/download_1229240_easyicon.net.svg'))
        self.info_down.setToolTip('<b>开始下载</b>')
        self.msg_button.hide()

    def _downFailFlag(self) -> None:
        self.info_down.setIconSize(QSize(28, 28))
        self.info_down.setIcon(
            QIcon(':/ico/cloud_fail_72px_1137820_easyicon.net.png'))
        self.info_down.setToolTip('<b>下载失败</b>')
        self.msg_button.show()

    def _downOkFlag(self) -> None:
        self.info_down.setIconSize(QSize(28, 28))
        self.info_down.setIcon(QIcon(':/ico/checked_1229231_easyicon.net.svg'))
        self.info_down.setToolTip('<b>已下载</b>')
        self.msg_button.show()

    def _downIngFlag(self) -> None:
        self.info_down.setIconSize(QSize(28, 28))
        self.info_down.setGif(CommonPixmaps.gif_crawl_novel)
        self.info_down.setToolTip('<b>下载中</b>')
        self.msg_button.hide()

    def autoProcessFlags(self) -> None:
        inf = self._inf
        search = inf.novel_app.getSearchWidget(inf.novel_index - 1)
        icon = inf.novel_app.getIconWidget(inf.novel_index - 1)
        if inf.novel_status == DownStatus.down_fail:  # '下载失败':
            self._downFailFlag()
            search._downFailFlag() if search else None
            icon._downFailFlag() if icon else None
        elif inf.novel_status == DownStatus.down_ok:  # '已下载'
            self._downOkFlag()
            search._downOkFlag() if search else None
            icon._downOkFlag() if icon else None
        elif inf.novel_status == DownStatus.down_ing:  # '下载中'
            self._downIngFlag()
            search._downIngFlag() if search else None
            icon._downIngFlag() if icon else None
        elif inf.novel_status == DownStatus.down_before:  # '未处理'
            self._downBeforeFlag()
            search._downBeforeFlag() if search else None
            icon._downBeforeFlag() if icon else None

    def autoProcessSubmitFlags(self) -> None:
        inf = self._inf
        if inf.novel_status == DownStatus.down_fail:  # '下载失败':
            self._downFailFlag()
        elif inf.novel_status == DownStatus.down_ok:  # '已下载':
            self._downOkFlag()
        elif inf.novel_status == DownStatus.down_ing:  # '下载中'
            self._downIngFlag()
        elif inf.novel_status == DownStatus.down_before:  # '未处理'
            self._downBeforeFlag()

    def download(self) -> None:
        if not self._inf._is_file:
            if self._inf.novel_chapter_urls:
                self.down_signal.emit(self._inf)
            else:
                self._downBeforeFlag()
        else:
            self.down_signal.emit(self._inf)

    def restart(self) -> None:
        if self._inf.novel_status != DownStatus.down_ing:  # '下载中':
            if self._inf.novel_subs_state == False:
                self._inf.novel_app.stopTask(self._inf.novel_index - 1)
            else:
                self._inf.novel_down_cancel = True
                self._inf.novel_flag = False
                self._downBeforeFlag()
            self._inf.prepare_restart()
            self.showFullMessage(self._inf)
            self.progressBar.setFormat('0.0%         ')
            self.label_17.setStyleSheet(f'color:{COLOR["undo"]}')
            if self._isSubmitWidget():
                self.subscribe_widget.prepare_restart()
            self.download()

    def setInfo(self, inf: InfoObj) -> None:
        self._inf = inf

    def _addRect(self, pixmap: QPixmap) -> None:
        pen = QPen()
        pen.setColor(Qt.lightGray)
        pen.setWidth(2)
        painter = QPainter()
        painter.begin(pixmap)
        painter.setPen(pen)
        painter.drawRect(pixmap.rect())
        painter.end()

    @property
    def icon_widget(self) -> IconWidget:
        return self._inf.novel_app.getIconWidget(self._inf.novel_index - 1)

    @property
    def subscribe_widget(self) -> SubscribeWidget:
        return self._inf.novel_app.getSubscribeWidget(self._inf.novel_index -
                                                      1)

    @property
    def search_widget(self):
        return self._inf.novel_app.getSearchWidget(self._inf.novel_index - 1)

    @property
    def select_dia(self):
        return self.novel_widget.main_gui.selectdialog

    @property
    def novel_widget(self) -> 'NovelWidget':
        return self._inf.novel_app

    @pyqtSlot(InfoObj)
    def showStatic(self, inf: InfoObj) -> None:
        self._inf = inf
        self.handle = IntroutcedHandle(inf)
        info_title = inf.novel_name + f'[{inf.novel_site}] [{inf.novel_index}]'
        elid_content = self.info_title.fontMetrics().elidedText(
            info_title, Qt.ElideMiddle,
            self._inf.novel_app.width() * .8)
        self.info_title.setText(elid_content)
        processed_introuce = self.handle.processIntroutced()
        self.info_introduced.setHtml(processed_introuce)
        file_info = QFileInfo(QDir(inf.novel_img_save_path),
                              inf.novel_img_name)
        size = IconWidget.getNovelSize()
        if file_info.exists() and self.validImage(
                file_info.absoluteFilePath()):
            pixmap = QPixmap(file_info.absoluteFilePath()).scaled(
                size, transformMode=Qt.SmoothTransformation)
        else:
            if self._inf.novel_subs_state == False:
                icon_widget = self.icon_widget
                pixmap = icon_widget.img_label.pixmap().scaled(
                    size, transformMode=Qt.SmoothTransformation)
            else:
                pixmap = self.subscribe_widget.novel_pix.scaled(
                    size, transformMode=Qt.SmoothTransformation)
        self._addRect(pixmap)
        self.info_img.setPixmap(pixmap)
        self.info_img.setFixedSize(pixmap.size())
        if self.info.novel_subs_url in self.novel_widget.subscribe_urls or self.info.novel_subs_state:
            self.info_img.setSubscribeState(True)

        self.label_13.setText(inf.novel_name + f'[{inf.novel_site}].' +
                              inf.novel_file_type)  # 文件名
        self.label_14.setText(inf.novel_save_path)  # 下载目录
        self.label_15.setText(inf.novel_url)  # 下载地址
        self.label_18.setText(inf.novel_file_size)  # 文件大小

        # 章节信息
        if inf.novel_chapter_urls and not inf._is_file:
            self.frame_3.show()
            count = [0 for u, c, state in inf.novel_chapter_urls if state]
            self.label_2.setText(f'已选中: {len(count)}个')
        else:
            self.frame_3.hide()

    @pyqtSlot(InfoObj)
    def updateFromInf(self, inf: InfoObj) -> None:
        self._inf = inf
        status = inf.novel_status
        if status == DownStatus.down_ing:  # '下载中':
            current_color = COLOR['doing']
        elif status == DownStatus.down_ok:  # '已下载':
            current_color = COLOR['down_ok']
        elif status == DownStatus.down_before:  # '未处理':
            current_color = COLOR['undo']
        elif status == DownStatus.down_fail:  # '下载失败':
            current_color = COLOR['down_fail']
        self.label_17.setStyleSheet(f'color: {current_color}')
        self.label_16.setText(inf.novel_averge_speed)  # 平均速度
        self.label_17.setText(inf.novel_status.value)  # 状态
        self.label_19.setText(inf.novel_start_time)  # 创建时间
        self.label_20.setText(inf.novel_end_time)  # 完成时间
        self.label_18.setText(inf.novel_file_size)  # 文件大小
        self.progressBar.setValue(inf.novel_percent)  # 进度条动画控制
        self.progressBar.setFormat(
            '%.1f%%  %s' %
            (inf.novel_percent, inf.novel_meta.get('down_size',
                                                   '       ')))  # 下载进度条
        self.label.setText(inf.novel_speed)  # 下载速度

    @pyqtSlot(InfoObj)
    def showFullMessage(self, inf: InfoObj) -> None:
        self.showStatic(inf)
        self.updateFromInf(inf)
        page_state = self.novel_widget.beforePageToTaskWidget()
        if self._inf.novel_subs_state and page_state == PageState.subscribe_page:
            self.autoProcessSubmitFlags()
            self.sub_button.setEnabled(False)
            self.checkBox.setChecked(True)
            self.sub_button.show()
            self.checkBox.show()
        else:
            if inf.novel_chapter_urls and inf._is_file == False:
                if self._inf.novel_subs_url not in self.novel_widget.subscribe_urls:
                    self.sub_button.setChecked(True)
                    self.checkBox.setChecked(False)
                    self.sub_button.setText('未订阅')
                else:
                    self.sub_button.setChecked(False)
                    self.checkBox.setChecked(True)
                    self.sub_button.setText('已订阅')
                self.sub_button.show()
                self.checkBox.show()
                self.sub_button.setEnabled(False)
            else:
                self.sub_button.hide()
                self.checkBox.hide()

    @pyqtSlot(int)
    def subscribePolicy(self, state) -> None:
        page_state = self.novel_widget.beforePageToTaskWidget()
        if page_state == PageState.subscribe_page:
            if state == Qt.Checked:
                if self.info._is_file == False and self.info.novel_chapter_urls:
                    flag = self.novel_widget._addSubsInfo(self.info)
                    if flag:
                        self.info.dump_subscribe()
                        self.info.novel_subs_state = True
                    self.sub_button.setText('已订阅')
                    self.sub_button.setChecked(False)
                    self.info_img.setSubscribeState(True)
            elif state == Qt.Unchecked:
                if self.info._is_file == False and self.info.novel_chapter_urls:
                    flag = self.novel_widget._removeSubsInfo(self.info)
                    if flag:
                        self.info.novel_subs_state = False
                        self.info.remove_subscribe()
                    self.sub_button.setText('未订阅')
                    self.sub_button.setChecked(True)
                    self.info_img.setSubscribeState(False)
        else:
            temp_index = self.info.novel_index
            if state == Qt.Checked:
                flag = self.novel_widget._addSubsInfo(self.info)
                if flag:
                    self.info.dump_subscribe()
                    self.info.novel_subs_state = False
                    self.info.novel_index = temp_index
                    self.info.novel_subs_index = -1

                self.sub_button.setText('已订阅')
                self.sub_button.setChecked(False)
                self.info_img.setSubscribeState(True)
            elif state == Qt.Unchecked:
                flag = self.novel_widget._removeSubsInfo(self.info)
                if flag:
                    self.info.remove_subscribe()
                    self.info.novel_subs_state = False
                    self.info.novel_index = temp_index
                    self.info.novel_subs_index = -1
                self.sub_button.setText('未订阅')
                self.sub_button.setChecked(True)
                self.info_img.setSubscribeState(False)
        length = len(self.novel_widget.subscribe_urls)
        self.novel_widget.titleMsgInfo(f'已订阅: {length}本小说', True)

    def closeMessage(self) -> None:
        self.remove_signal.emit()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._inf:
            self.showStatic(self._inf)
            w = (self.width() - 7) / 2
            self.frame_9.setFixedWidth(w)
            self.frame_10.setFixedWidth(w)
        if self.in_read:
            if not self.mark_button.isHidden():
                self._show_mark_button()
            if not self.more_widget.isHidden():
                self._show_more_widget()

    @pyqtSlot()
    def nextInf(self) -> None:
        inf = self._inf
        novel_app = self._inf.novel_app
        page_state = novel_app.beforePageToTaskWidget()
        total = novel_app.listWidget_3.count(
        ) if page_state == PageState.subscribe_page else novel_app.getResultsCount(
        )
        if page_state != PageState.subscribe_page:
            if inf.novel_index < total:
                widget = novel_app.getSearchWidget(inf.novel_index)
                icon_widget = novel_app.getIconWidget(inf.novel_index)
                widget.setFocus(True)
                icon_widget.setFocus(True)
                next_inf = widget.info
                self.showFullMessage(next_inf)
                self.autoProcessFlags()
                # inf.novel_app._parent.selectdialog.inf = next_inf
                self._inf = next_inf
                # self.textBrowser.info = next_inf
        else:
            if inf.novel_index < total:
                subscribe_widget = novel_app.getSubscribeWidget(
                    inf.novel_index)
                next_inf = subscribe_widget.info
                self.showFullMessage(next_inf)
                self.autoProcessSubmitFlags()
                self.exitButtonShowPolicy()
                # inf.novel_app._parent.selectdialog.inf = next_inf
                self._inf = next_inf
                # self.textBrowser.info = next_inf
        self.subscribePageInitPolicy(False)

    @pyqtSlot()
    def previousInf(self) -> None:
        inf = self._inf
        novel_app = self._inf.novel_app
        page_state = novel_app.beforePageToTaskWidget()
        if page_state != PageState.subscribe_page:
            if inf.novel_index >= 2:
                widget = novel_app.getSearchWidget(inf.novel_index - 2)
                icon_widget = novel_app.getIconWidget(inf.novel_index - 2)
                widget.setFocus(True)
                icon_widget.setFocus(True)
                previous_inf = widget.info
                self.showFullMessage(previous_inf)
                self.autoProcessFlags()
                # inf.novel_app._parent.selectdialog.inf = previous_inf
                self._inf = previous_inf
                # self.textBrowser.info = previous_inf

        else:
            if inf.novel_index >= 2:
                subscribe_widget = novel_app.getSubscribeWidget(
                    inf.novel_index - 2)
                previous_inf = subscribe_widget.info
                self.showFullMessage(previous_inf)
                self.autoProcessSubmitFlags()
                # inf.novel_app._parent.selectdialog.inf = previous_inf
                self.exitButtonShowPolicy()
                self._inf = previous_inf
                # self.textBrowser.info = previous_inf
        self.subscribePageInitPolicy(False)

    @pyqtSlot()
    def showChapters(self) -> None:
        self.novel_widget.showChapters()

    def paintEvent(self, a0) -> None:
        super().paintEvent(a0)
        if not self.select_dia.is_show:
            self.inFocus()

    def inFocus(self):
        self.info_img.destroyShadow()
        s = '''
            QProgressBar {
                text-align: center; /*进度值居中*/;
                color: rgb(0, 0, 0);
                border:1px solid gray;
                border-radius:5px;
                font-family:华文细黑;
                background-color: white}
            QProgressBar::chunk {
                background-color: rgb(6, 168, 255);
                width:10px;
            }
        '''
        self.progressBar.setStyleSheet(s)

    def desFocus(self, des_color: ColorTypes):
        self.info_img.createShadow(des_color)
        s = '''
            QProgressBar {
                text-align: center; /*进度值居中*/;
                color: rgb(0, 0, 0);
                border:1px solid gray;
                border-radius:5px;
                font-family:华文细黑;
                background-color: rgba(%s, %s, %s, %s)}
            QProgressBar::chunk {
                background-color: rgb(6, 168, 255);
                width:10px;
            }
        '''
        t = (des_color.red(), des_color.green(), des_color.blue(), des_color.alpha())
        self.progressBar.setStyleSheet(s % t)

    def setReadStyle(self,
                     bkg_color: ColorTypes,
                     text_color: ColorTypes,
                     theme: str,
                     hover_color: ColorTypes = None) -> None:
        self.style_handle.setReadStyle(bkg_color, text_color, theme,
                                       hover_color)
