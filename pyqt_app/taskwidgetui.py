# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\task_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(760, 519)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.stackedWidget = QtWidgets.QStackedWidget(Form)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_6 = QtWidgets.QFrame(self.page)
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_4.setContentsMargins(5, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButton = HoverButton(self.frame_6)
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton.setStyleSheet("QPushButton{image:url(:/ico/close_512px_1175341_easyicon.net.png);border:none;width:23px;height:23px}\n"
"QPushButton:hover{image: url(:/ico/close_128px_1175741_easyicon.net.ico);width:23px;height:23px}\n"
"")
        self.pushButton.setText("")
        self.pushButton.setIconSize(QtCore.QSize(22, 22))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_4.addWidget(self.pushButton)
        self.info_title = QtWidgets.QLabel(self.frame_6)
        self.info_title.setStyleSheet("QLabel{font: bold 14pt}")
        self.info_title.setAlignment(QtCore.Qt.AlignCenter)
        self.info_title.setObjectName("info_title")
        self.horizontalLayout_4.addWidget(self.info_title)
        spacerItem = QtWidgets.QSpacerItem(5000, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.checkBox = QtWidgets.QCheckBox(self.frame_6)
        self.checkBox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.checkBox.setStyleSheet("QCheckBox{\n"
"    spacing: 2px;\n"
"}\n"
"\n"
"/*QCheckBox::indicator{\n"
"    width: 15px;\n"
"    height:15px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked{\n"
"    image:url(:/ico/unchecked_checkbox_64px_1170301_easyicon.net.png);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked{\n"
"    image:url(:/ico/checked_checkbox_64px_1101338_easyicon.net.png);\n"
"}*/\n"
"\n"
"")
        self.checkBox.setText("")
        self.checkBox.setTristate(False)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_4.addWidget(self.checkBox)
        self.sub_button = QtWidgets.QPushButton(self.frame_6)
        self.sub_button.setStyleSheet("QPushButton{border:none}\n"
"QPushButton:hover{border:1px solid lightgray;border-radius:3px;background:lightgray}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ico/check_128px_1138992_easyicon.net.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/ico/close_128px_1138994_easyicon.net.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.sub_button.setIcon(icon)
        self.sub_button.setIconSize(QtCore.QSize(23, 27))
        self.sub_button.setCheckable(True)
        self.sub_button.setChecked(False)
        self.sub_button.setObjectName("sub_button")
        self.horizontalLayout_4.addWidget(self.sub_button)
        self.frame_2 = QtWidgets.QFrame(self.frame_6)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pushButton_2 = QtWidgets.QPushButton(self.frame_2)
        self.pushButton_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_2.setStyleSheet("QPushButton{border:none}\n"
"QPushButton:hover{border:1px solid lightgray;border-radius:3px;background:lightgray}")
        self.pushButton_2.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/ico/angle-left.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon1)
        self.pushButton_2.setIconSize(QtCore.QSize(23, 27))
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_5.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.frame_2)
        self.pushButton_3.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_3.setStyleSheet("QPushButton{border:none}\n"
"QPushButton:hover{border:1px solid lightgray;border-radius:3px;background:lightgray}")
        self.pushButton_3.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/ico/angle-right.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_3.setIcon(icon2)
        self.pushButton_3.setIconSize(QtCore.QSize(23, 27))
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_5.addWidget(self.pushButton_3)
        self.horizontalLayout_4.addWidget(self.frame_2)
        self.horizontalLayout_4.setStretch(1, 10)
        self.verticalLayout.addWidget(self.frame_6)
        self.frame_4 = QtWidgets.QFrame(self.page)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.frame_13 = QtWidgets.QFrame(self.frame_4)
        self.frame_13.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_13.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_13.setObjectName("frame_13")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frame_13)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.info_img = TaskWidgetSubmitLabel(self.frame_13)
        self.info_img.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.info_img.setObjectName("info_img")
        self.verticalLayout_5.addWidget(self.info_img)
        spacerItem1 = QtWidgets.QSpacerItem(20, 129, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem1)
        self.horizontalLayout_9.addWidget(self.frame_13)
        self.info_introduced = QtWidgets.QTextEdit(self.frame_4)
        font = QtGui.QFont()
        font.setFamily("微软雅黑 Light")
        font.setPointSize(11)
        self.info_introduced.setFont(font)
        self.info_introduced.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.info_introduced.setStyleSheet("background-color:rgba(0,0,0,0)")
        self.info_introduced.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.info_introduced.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.info_introduced.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.info_introduced.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.info_introduced.setObjectName("info_introduced")
        self.horizontalLayout_9.addWidget(self.info_introduced)
        self.verticalLayout.addWidget(self.frame_4)
        self.line_2 = QtWidgets.QFrame(self.page)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.frame_5 = QtWidgets.QFrame(self.page)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.frame_8 = QtWidgets.QFrame(self.frame_5)
        self.frame_8.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_8.setObjectName("frame_8")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.frame_8)
        self.horizontalLayout_7.setContentsMargins(0, -1, 0, -1)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.pushButton_6 = QtWidgets.QPushButton(self.frame_8)
        self.pushButton_6.setStyleSheet("font: 11.5pt;\n"
"text-decoration: underline;\n"
"border:none;\n"
"font-weight:bold")
        self.pushButton_6.setObjectName("pushButton_6")
        self.horizontalLayout_7.addWidget(self.pushButton_6)
        spacerItem2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem2)
        self.frame_3 = QtWidgets.QFrame(self.frame_8)
        self.frame_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_5 = QtWidgets.QPushButton(self.frame_3)
        self.pushButton_5.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_5.setStyleSheet("QPushButton{font: 11.5pt;\n"
"text-decoration: underline;\n"
"font-weight:bold;\n"
"border:none}\n"
"QPushButton:hover{\n"
"color: rgb(200, 105, 255)}")
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_3.addWidget(self.pushButton_5)
        self.label_2 = QtWidgets.QLabel(self.frame_3)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        spacerItem3 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.horizontalLayout_7.addWidget(self.frame_3)
        self.horizontalLayout_6.addWidget(self.frame_8)
        self.fresh_button = GifButton(self.frame_5)
        font = QtGui.QFont()
        font.setFamily("黑体")
        font.setPointSize(9)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.fresh_button.setFont(font)
        self.fresh_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.fresh_button.setStyleSheet("QPushButton{border:none}\n"
"QPushButton:checked{border:1px solid lightgray;\n"
"border-radius:2px;background-color: gray}\n"
"QPushButton:hover{border:1px solid lightgray;border-radius:2px;background-color:lightgray}")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/ico/refresh_173px_1188146_easyicon.net.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fresh_button.setIcon(icon3)
        self.fresh_button.setObjectName("fresh_button")
        self.horizontalLayout_6.addWidget(self.fresh_button)
        self.read_button = QtWidgets.QPushButton(self.frame_5)
        font = QtGui.QFont()
        font.setFamily("黑体")
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.read_button.setFont(font)
        self.read_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.read_button.setStyleSheet("QPushButton{border:none}\n"
"QPushButton:hover{border:1px solid lightgray;border-radius:2px;background-color:lightgray}")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/ico/Metro_Text_Document_128px_1097814_easyicon.net.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.read_button.setIcon(icon4)
        self.read_button.setIconSize(QtCore.QSize(23, 23))
        self.read_button.setObjectName("read_button")
        self.horizontalLayout_6.addWidget(self.read_button)
        spacerItem4 = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem4)
        self.msg_button = QtWidgets.QPushButton(self.frame_5)
        self.msg_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.msg_button.setStyleSheet("QPushButton{border:none}\n"
"")
        self.msg_button.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/ico/EditDocument_1194764_easyicon.net.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.msg_button.setIcon(icon5)
        self.msg_button.setIconSize(QtCore.QSize(28, 28))
        self.msg_button.setObjectName("msg_button")
        self.horizontalLayout_6.addWidget(self.msg_button)
        self.info_down = GifButton(self.frame_5)
        self.info_down.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.info_down.setStyleSheet("QPushButton{border:none}\n"
"QPushButton:hover{border:1px solid lightgray;border-radius:3px;background:lightgray}")
        self.info_down.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/ico/download_1229240_easyicon.net.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.info_down.setIcon(icon6)
        self.info_down.setIconSize(QtCore.QSize(28, 28))
        self.info_down.setObjectName("info_down")
        self.horizontalLayout_6.addWidget(self.info_down)
        self.pushButton_4 = QtWidgets.QPushButton(self.frame_5)
        self.pushButton_4.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_4.setStyleSheet("QPushButton{border:none}\n"
"QPushButton:hover{border:1px solid lightgray;border-radius:3px;background:lightgray}")
        self.pushButton_4.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/ico/refresh_1233084_easyicon.net.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_4.setIcon(icon7)
        self.pushButton_4.setIconSize(QtCore.QSize(28, 28))
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_6.addWidget(self.pushButton_4)
        self.verticalLayout.addWidget(self.frame_5)
        self.line = QtWidgets.QFrame(self.page)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.frame_7 = QtWidgets.QFrame(self.page)
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.frame_7)
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.frame_9 = QtWidgets.QFrame(self.frame_7)
        self.frame_9.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_9.setObjectName("frame_9")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_9)
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.label_5 = QtWidgets.QLabel(self.frame_9)
        font = QtGui.QFont()
        font.setFamily("SimSun-ExtB")
        self.label_5.setFont(font)
        self.label_5.setStyleSheet("")
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 1)
        self.label_13 = TaskInfoLabel(self.frame_9)
        self.label_13.setStyleSheet("color: black;\n"
"font-weight:bold;\n"
"")
        self.label_13.setOpenExternalLinks(False)
        self.label_13.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 0, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.frame_9)
        self.label_6.setStyleSheet("")
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.label_14 = TaskInfoLabel(self.frame_9)
        self.label_14.setStyleSheet("QLabel{color: gray;font-weight:bold}\n"
"QLabel:hover{color: blue; font-weight:bold}")
        self.label_14.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 1, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.frame_9)
        self.label_7.setStyleSheet("")
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)
        self.label_15 = TaskInfoLabel(self.frame_9)
        self.label_15.setStyleSheet("font-family:宋体")
        self.label_15.setOpenExternalLinks(False)
        self.label_15.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.label_15.setObjectName("label_15")
        self.gridLayout.addWidget(self.label_15, 2, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.frame_9)
        self.label_12.setStyleSheet("")
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 3, 0, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.frame_9)
        self.label_16.setObjectName("label_16")
        self.gridLayout.addWidget(self.label_16, 3, 1, 1, 1)
        self.gridLayout.setColumnStretch(1, 20)
        self.horizontalLayout_8.addWidget(self.frame_9)
        self.frame_10 = QtWidgets.QFrame(self.frame_7)
        self.frame_10.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_10.setObjectName("frame_10")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_10)
        self.gridLayout_2.setVerticalSpacing(10)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_8 = QtWidgets.QLabel(self.frame_10)
        self.label_8.setStyleSheet("")
        self.label_8.setObjectName("label_8")
        self.gridLayout_2.addWidget(self.label_8, 0, 0, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.frame_10)
        self.label_17.setStyleSheet("")
        self.label_17.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.label_17.setObjectName("label_17")
        self.gridLayout_2.addWidget(self.label_17, 0, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.frame_10)
        self.label_9.setStyleSheet("")
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 1, 0, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.frame_10)
        self.label_18.setStyleSheet("")
        self.label_18.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.label_18.setObjectName("label_18")
        self.gridLayout_2.addWidget(self.label_18, 1, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.frame_10)
        self.label_10.setStyleSheet("")
        self.label_10.setObjectName("label_10")
        self.gridLayout_2.addWidget(self.label_10, 2, 0, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.frame_10)
        self.label_19.setStyleSheet("")
        self.label_19.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.label_19.setObjectName("label_19")
        self.gridLayout_2.addWidget(self.label_19, 2, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.frame_10)
        self.label_11.setStyleSheet("")
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 3, 0, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.frame_10)
        self.label_20.setStyleSheet("")
        self.label_20.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.label_20.setObjectName("label_20")
        self.gridLayout_2.addWidget(self.label_20, 3, 1, 1, 1)
        self.gridLayout_2.setColumnStretch(1, 20)
        self.horizontalLayout_8.addWidget(self.frame_10)
        self.verticalLayout.addWidget(self.frame_7)
        self.frame = QtWidgets.QFrame(self.page)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.progressBar = QtWidgets.QProgressBar(self.frame)
        self.progressBar.setStyleSheet("QProgressBar {\n"
"    text-align: center; /*进度值居中*/;\n"
"    color: rgb(0, 0, 0);\n"
"    border:1px solid gray;\n"
"    border-radius:5px;\n"
"    font-family:华文细黑;\n"
"}\n"
"QProgressBar::chunk {\n"
"    background-color: rgb(6, 168, 255);\n"
"    width:10px;\n"
"}\n"
"")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout_2.addWidget(self.progressBar)
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setMinimumSize(QtCore.QSize(50, 0))
        self.label.setStyleSheet("font-family:华文细黑;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.horizontalLayout_2.setStretch(0, 40)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout.addWidget(self.frame)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setStyleSheet("")
        self.page_2.setObjectName("page_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.page_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame_12 = QtWidgets.QFrame(self.page_2)
        self.frame_12.setStyleSheet("")
        self.frame_12.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_12.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_12.setObjectName("frame_12")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_12)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.readbar_widget = ReadBar(self.frame_12)
        self.readbar_widget.setStyleSheet("")
        self.readbar_widget.setObjectName("readbar_widget")
        self.verticalLayout_3.addWidget(self.readbar_widget)
        self.stackedWidget_2 = QtWidgets.QStackedWidget(self.frame_12)
        self.stackedWidget_2.setObjectName("stackedWidget_2")
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.page_3)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.stackedWidget_3 = QtWidgets.QStackedWidget(self.page_3)
        self.stackedWidget_3.setObjectName("stackedWidget_3")
        self.page_5 = QtWidgets.QWidget()
        self.page_5.setObjectName("page_5")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.page_5)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.textBrowser = TaskReadBrowser(self.page_5)
        self.textBrowser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.textBrowser.setStyleSheet("")
        self.textBrowser.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_7.addWidget(self.textBrowser)
        self.stackedWidget_3.addWidget(self.page_5)
        self.page_6 = QtWidgets.QWidget()
        self.page_6.setObjectName("page_6")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.page_6)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.auto_split = AutoSplitContentTaskReadWidget(self.page_6)
        self.auto_split.setObjectName("auto_split")
        self.verticalLayout_6.addWidget(self.auto_split)
        self.stackedWidget_3.addWidget(self.page_6)
        self.verticalLayout_4.addWidget(self.stackedWidget_3)
        self.frame_11 = QtWidgets.QFrame(self.page_3)
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(12)
        self.frame_11.setFont(font)
        self.frame_11.setStyleSheet("")
        self.frame_11.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_11.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_11.setObjectName("frame_11")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.frame_11)
        self.horizontalLayout_10.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.chapter_label = QtWidgets.QLabel(self.frame_11)
        self.chapter_label.setObjectName("chapter_label")
        self.horizontalLayout_10.addWidget(self.chapter_label)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem5)
        self.prev_button = ColorButton(self.frame_11)
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        self.prev_button.setFont(font)
        self.prev_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.prev_button.setText("")
        self.prev_button.setCheckable(True)
        self.prev_button.setObjectName("prev_button")
        self.horizontalLayout_10.addWidget(self.prev_button)
        self.next_button = ColorButton(self.frame_11)
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.next_button.setFont(font)
        self.next_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.next_button.setText("")
        self.next_button.setCheckable(True)
        self.next_button.setObjectName("next_button")
        self.horizontalLayout_10.addWidget(self.next_button)
        self.exit_button = ColorButton(self.frame_11)
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        self.exit_button.setFont(font)
        self.exit_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.exit_button.setText("")
        self.exit_button.setCheckable(True)
        self.exit_button.setObjectName("exit_button")
        self.horizontalLayout_10.addWidget(self.exit_button)
        self.sizedown_button = QtWidgets.QPushButton(self.frame_11)
        self.sizedown_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.sizedown_button.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/ico/font_size_down_1170460_easyicon.net.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.sizedown_button.setIcon(icon8)
        self.sizedown_button.setCheckable(True)
        self.sizedown_button.setObjectName("sizedown_button")
        self.horizontalLayout_10.addWidget(self.sizedown_button)
        self.sizeup_button = QtWidgets.QPushButton(self.frame_11)
        self.sizeup_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.sizeup_button.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/ico/font_size_up_1170461_easyicon.net.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.sizeup_button.setIcon(icon9)
        self.sizeup_button.setCheckable(True)
        self.sizeup_button.setObjectName("sizeup_button")
        self.horizontalLayout_10.addWidget(self.sizeup_button)
        self.other_button = ColorButton(self.frame_11)
        self.other_button.setText("")
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/hl/其他.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.other_button.setIcon(icon10)
        self.other_button.setObjectName("other_button")
        self.horizontalLayout_10.addWidget(self.other_button)
        self.markup_button = ColorButton(self.frame_11)
        self.markup_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.markup_button.setText("")
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/hl/bookmark_1223025_easyicon.net.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.markup_button.setIcon(icon11)
        self.markup_button.setCheckable(True)
        self.markup_button.setObjectName("markup_button")
        self.horizontalLayout_10.addWidget(self.markup_button)
        self.skin_button = ColorButton(self.frame_11)
        self.skin_button.setText("")
        self.skin_button.setObjectName("skin_button")
        self.horizontalLayout_10.addWidget(self.skin_button)
        self.chapters_button_2 = ColorButton(self.frame_11)
        self.chapters_button_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.chapters_button_2.setText("")
        self.chapters_button_2.setCheckable(True)
        self.chapters_button_2.setObjectName("chapters_button_2")
        self.horizontalLayout_10.addWidget(self.chapters_button_2)
        self.more_button = ColorButton(self.frame_11)
        self.more_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.more_button.setText("")
        self.more_button.setCheckable(True)
        self.more_button.setObjectName("more_button")
        self.horizontalLayout_10.addWidget(self.more_button)
        self.verticalLayout_4.addWidget(self.frame_11)
        self.verticalLayout_4.setStretch(0, 20)
        self.stackedWidget_2.addWidget(self.page_3)
        self.verticalLayout_3.addWidget(self.stackedWidget_2)
        self.verticalLayout_2.addWidget(self.frame_12)
        self.stackedWidget.addWidget(self.page_2)
        self.horizontalLayout.addWidget(self.stackedWidget)

        self.retranslateUi(Form)
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_2.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.info_title.setText(_translate("Form", "小说名"))
        self.sub_button.setText(_translate("Form", "已订阅"))
        self.pushButton_2.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">上一个(Z)</span></p></body></html>"))
        self.pushButton_3.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">下一个(C)</span></p></body></html>"))
        self.info_img.setText(_translate("Form", "照片"))
        self.pushButton_6.setText(_translate("Form", "任务详情"))
        self.pushButton_5.setText(_translate("Form", "按章节下载"))
        self.label_2.setText(_translate("Form", "几把"))
        self.fresh_button.setText(_translate("Form", "获取最新章节"))
        self.read_button.setText(_translate("Form", "阅读"))
        self.msg_button.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-weight:600;\">下载日志</span></p></body></html>"))
        self.info_down.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-weight:600;\">开始下载</span></p></body></html>"))
        self.pushButton_4.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-weight:600;\">重新下载</span></p></body></html>"))
        self.label_5.setText(_translate("Form", "文件名称"))
        self.label_13.setText(_translate("Form", "TextLabel"))
        self.label_6.setText(_translate("Form", "存储目录"))
        self.label_14.setText(_translate("Form", "TextLabel"))
        self.label_7.setText(_translate("Form", "下载地址"))
        self.label_15.setText(_translate("Form", "https://www.baidu.com"))
        self.label_12.setText(_translate("Form", "平均速度"))
        self.label_16.setText(_translate("Form", "TextLabel"))
        self.label_8.setText(_translate("Form", "任务状态"))
        self.label_17.setText(_translate("Form", "TextLabel"))
        self.label_9.setText(_translate("Form", "文件大小"))
        self.label_18.setText(_translate("Form", "2012"))
        self.label_10.setText(_translate("Form", "创建时间"))
        self.label_19.setText(_translate("Form", "TextLabel"))
        self.label_11.setText(_translate("Form", "完成时间"))
        self.label_20.setText(_translate("Form", "TextLabel"))
        self.progressBar.setFormat(_translate("Form", "%p%"))
        self.label.setText(_translate("Form", "21.34k/s "))
        self.chapter_label.setText(_translate("Form", "TextLabel"))
        self.prev_button.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-weight:600;\">上一章 (快捷键: 1)</span></p></body></html>"))
        self.prev_button.setShortcut(_translate("Form", "1"))
        self.next_button.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-weight:600;\">下一章 (快捷键: 2)</span></p></body></html>"))
        self.next_button.setShortcut(_translate("Form", "2"))
        self.exit_button.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-weight:600;\">退出阅读 (快捷键: Esc)</span></p></body></html>"))
        self.exit_button.setShortcut(_translate("Form", "Esc"))
        self.other_button.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">翻页方式</span></p></body></html>"))
        self.markup_button.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">添加书签</span></p></body></html>"))
        self.skin_button.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">阅读主题</span></p></body></html>"))
        self.chapters_button_2.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">信息</span></p></body></html>"))
        self.more_button.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">设置</span></p></body></html>"))
from .customwidgets import AutoSplitContentTaskReadWidget, ColorButton, GifButton, HoverButton, ReadBar, TaskInfoLabel, TaskReadBrowser, TaskWidgetSubmitLabel
