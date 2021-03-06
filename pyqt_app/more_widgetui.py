# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\more_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(762, 613)
        Form.setStyleSheet("QWidget{background-color:#000000}")
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setStyleSheet("QPushButton{border: none; font-family: 宋体; color:#AAAAAA; font-size: 10pt;font-weight:bold; background-color:transparent}\n"
"QPushButton:checked{color:#CC295F; font-size: 14pt; font-weight:bold; font-family: 宋体}\n"
"QFrame{background-color: #2B2B2B}\n"
"")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_6 = HoverButton(self.frame)
        self.pushButton_6.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_6.setStyleSheet("QPushButton{image:url(:/ico/close_512px_1175341_easyicon.net.png);border:none;width:23px;height:23px}\n"
"QPushButton:hover{image: url(:/ico/close_128px_1175741_easyicon.net.ico);width:23px;height:23px}\n"
"")
        self.pushButton_6.setText("")
        self.pushButton_6.setCheckable(True)
        self.pushButton_6.setObjectName("pushButton_6")
        self.horizontalLayout.addWidget(self.pushButton_6)
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setStyleSheet("")
        self.pushButton.setCheckable(True)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.frame)
        self.pushButton_3.setCheckable(True)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)
        self.horizontalLayout.setStretch(3, 1)
        self.verticalLayout.addWidget(self.frame)
        self.stackedWidget = QtWidgets.QStackedWidget(Form)
        self.stackedWidget.setStyleSheet("")
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setStyleSheet("font-family: 宋体;\n"
"font-size: 11pt;\n"
"color: #FFFFFF")
        self.page.setObjectName("page")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout_2.setContentsMargins(-1, 11, -1, -1)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scrollArea = QtWidgets.QScrollArea(self.page)
        self.scrollArea.setStyleSheet("background:transparent;\n"
"border:none")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 108, 443))
        self.scrollAreaWidgetContents.setStyleSheet("QSlider::groove:horizontal {\n"
"border: 1px solid #4A708B;\n"
"background: #C0C0C0;\n"
"height: 5px;\n"
"border-radius: 1px;\n"
"padding-left:-1px;\n"
"padding-right:-1px;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal {\n"
"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"    stop:0 #B1B1B1, stop:1 #c4c4c4);\n"
"background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,\n"
"    stop: 0 #5DCCFF, stop: 1 #1874CD);\n"
"border: 1px solid #4A708B;\n"
"height: 10px;\n"
"border-radius: 2px;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal {\n"
"background: #575757;\n"
"border: 0px solid #777;\n"
"height: 10px;\n"
"border-radius: 2px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal \n"
"{\n"
"    background: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, \n"
"    stop:0.6 #45ADED, stop:0.778409 rgba(255, 255, 255, 255));\n"
"\n"
"    width: 11px;\n"
"    margin-top: -3px;\n"
"    margin-bottom: -3px;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:hover {\n"
"    background: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0.6 #2A8BDA, \n"
"    stop:0.778409 rgba(255, 255, 255, 255));\n"
"\n"
"    width: 11px;\n"
"    margin-top: -3px;\n"
"    margin-bottom: -3px;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal:disabled {\n"
"background: #00009C;\n"
"border-color: #999;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal:disabled {\n"
"background: #eee;\n"
"border-color: #999;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:disabled {\n"
"background: #eee;\n"
"border: 1px solid #aaa;\n"
"border-radius: 4px;\n"
"}\n"
"")
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_8 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_4.addWidget(self.label_8)
        self.font_combo = FontCombobox(self.scrollAreaWidgetContents)
        self.font_combo.setStyleSheet("QComboBox{border: 1px solid white;border-radius:3px}\n"
"QComboBox:focus{border: 1px solid #CC295F;border-radius:3px}")
        self.font_combo.setObjectName("font_combo")
        self.verticalLayout_4.addWidget(self.font_combo)
        self.label_4 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_4.addWidget(self.label_4)
        self.checkBox = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox.setStyleSheet("QCheckBox{\n"
"    spacing: 5px;\n"
"}\n"
"\n"
"QCheckBox::indicator{\n"
"    width: 32px;\n"
"    height: 32px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked{\n"
"    image:url(:/ico/按钮_开启.png);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked{\n"
"    image:url(:/ico/按钮_关闭.png);\n"
"}\n"
"")
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout_4.addWidget(self.checkBox)
        self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName("label")
        self.verticalLayout_4.addWidget(self.label)
        self.frame_6 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.horizontalSlider = QtWidgets.QSlider(self.frame_6)
        self.horizontalSlider.setStyleSheet("")
        self.horizontalSlider.setMinimum(12)
        self.horizontalSlider.setMaximum(80)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalLayout_6.addWidget(self.horizontalSlider)
        self.fz_plus = QtWidgets.QPushButton(self.frame_6)
        self.fz_plus.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.fz_plus.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ico/jia.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fz_plus.setIcon(icon)
        self.fz_plus.setCheckable(True)
        self.fz_plus.setObjectName("fz_plus")
        self.horizontalLayout_6.addWidget(self.fz_plus)
        self.fz_subtract = QtWidgets.QPushButton(self.frame_6)
        self.fz_subtract.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.fz_subtract.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/ico/jian.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fz_subtract.setIcon(icon1)
        self.fz_subtract.setCheckable(True)
        self.fz_subtract.setObjectName("fz_subtract")
        self.horizontalLayout_6.addWidget(self.fz_subtract)
        self.verticalLayout_4.addWidget(self.frame_6)
        self.label_2 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_4.addWidget(self.label_2)
        self.frame_7 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.frame_7)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.horizontalSlider_2 = QtWidgets.QSlider(self.frame_7)
        self.horizontalSlider_2.setStyleSheet("")
        self.horizontalSlider_2.setMinimum(100)
        self.horizontalSlider_2.setMaximum(500)
        self.horizontalSlider_2.setSingleStep(10)
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.horizontalLayout_7.addWidget(self.horizontalSlider_2)
        self.ls_plus = QtWidgets.QPushButton(self.frame_7)
        self.ls_plus.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ls_plus.setText("")
        self.ls_plus.setIcon(icon)
        self.ls_plus.setCheckable(True)
        self.ls_plus.setObjectName("ls_plus")
        self.horizontalLayout_7.addWidget(self.ls_plus)
        self.ls_subtract = QtWidgets.QPushButton(self.frame_7)
        self.ls_subtract.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ls_subtract.setText("")
        self.ls_subtract.setIcon(icon1)
        self.ls_subtract.setCheckable(True)
        self.ls_subtract.setObjectName("ls_subtract")
        self.horizontalLayout_7.addWidget(self.ls_subtract)
        self.verticalLayout_4.addWidget(self.frame_7)
        self.label_5 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_4.addWidget(self.label_5)
        self.frame_8 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_8.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_8.setObjectName("frame_8")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.frame_8)
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.horizontalSlider_3 = QtWidgets.QSlider(self.frame_8)
        self.horizontalSlider_3.setStyleSheet("")
        self.horizontalSlider_3.setMinimum(20)
        self.horizontalSlider_3.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_3.setObjectName("horizontalSlider_3")
        self.horizontalLayout_8.addWidget(self.horizontalSlider_3)
        self.indent_plus = QtWidgets.QPushButton(self.frame_8)
        self.indent_plus.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.indent_plus.setText("")
        self.indent_plus.setIcon(icon)
        self.indent_plus.setCheckable(True)
        self.indent_plus.setObjectName("indent_plus")
        self.horizontalLayout_8.addWidget(self.indent_plus)
        self.indent_subtract = QtWidgets.QPushButton(self.frame_8)
        self.indent_subtract.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.indent_subtract.setText("")
        self.indent_subtract.setIcon(icon1)
        self.indent_subtract.setCheckable(True)
        self.indent_subtract.setObjectName("indent_subtract")
        self.horizontalLayout_8.addWidget(self.indent_subtract)
        self.verticalLayout_4.addWidget(self.frame_8)
        self.label_6 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_4.addWidget(self.label_6)
        self.frame_9 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_9.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_9.setObjectName("frame_9")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.frame_9)
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.horizontalSlider_4 = QtWidgets.QSlider(self.frame_9)
        self.horizontalSlider_4.setStyleSheet("")
        self.horizontalSlider_4.setMinimum(5)
        self.horizontalSlider_4.setMaximum(500)
        self.horizontalSlider_4.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_4.setObjectName("horizontalSlider_4")
        self.horizontalLayout_9.addWidget(self.horizontalSlider_4)
        self.margin_plus = QtWidgets.QPushButton(self.frame_9)
        self.margin_plus.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.margin_plus.setText("")
        self.margin_plus.setIcon(icon)
        self.margin_plus.setCheckable(True)
        self.margin_plus.setObjectName("margin_plus")
        self.horizontalLayout_9.addWidget(self.margin_plus)
        self.margin_subtract = QtWidgets.QPushButton(self.frame_9)
        self.margin_subtract.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.margin_subtract.setText("")
        self.margin_subtract.setIcon(icon1)
        self.margin_subtract.setCheckable(True)
        self.margin_subtract.setObjectName("margin_subtract")
        self.horizontalLayout_9.addWidget(self.margin_subtract)
        self.verticalLayout_4.addWidget(self.frame_9)
        self.label_9 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_4.addWidget(self.label_9)
        self.frame_10 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_10.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_10.setObjectName("frame_10")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.frame_10)
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.horizontalSlider_5 = QtWidgets.QSlider(self.frame_10)
        self.horizontalSlider_5.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_5.setObjectName("horizontalSlider_5")
        self.horizontalLayout_10.addWidget(self.horizontalSlider_5)
        self.bright_plus = QtWidgets.QPushButton(self.frame_10)
        self.bright_plus.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.bright_plus.setText("")
        self.bright_plus.setIcon(icon)
        self.bright_plus.setObjectName("bright_plus")
        self.horizontalLayout_10.addWidget(self.bright_plus)
        self.bright_subtract = QtWidgets.QPushButton(self.frame_10)
        self.bright_subtract.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.bright_subtract.setText("")
        self.bright_subtract.setIcon(icon1)
        self.bright_subtract.setObjectName("bright_subtract")
        self.horizontalLayout_10.addWidget(self.bright_subtract)
        self.verticalLayout_4.addWidget(self.frame_10)
        self.label_3 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_4.addWidget(self.label_3)
        self.frame_2 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.lineEdit.setStyleSheet("QLineEdit{border-top:1px solid white;\n"
"border-bottom:1px solid white;\n"
"border-left:1px solid white;\n"
"border-right:0px solid white;\n"
"border-top-left-radius:3px;\n"
"border-bottom-left-radius:3px;\n"
"background:black}\n"
"QLineEdit:focus{\n"
"border:1px solid #CC295F;\n"
"border-radius:3px;\n"
"background:black}\n"
"")
        self.lineEdit.setClearButtonEnabled(False)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.up_letter = QtWidgets.QPushButton(self.frame_2)
        self.up_letter.setStyleSheet("border-top:1px solid white;\n"
"border-bottom:1px solid white;\n"
"border-left:0px solid white;\n"
"border-right:0px solid white;\n"
"")
        self.up_letter.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/ico/up_arrow_1209003_easyicon.net.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.up_letter.setIcon(icon2)
        self.up_letter.setIconSize(QtCore.QSize(15, 20))
        self.up_letter.setCheckable(True)
        self.up_letter.setObjectName("up_letter")
        self.horizontalLayout_2.addWidget(self.up_letter)
        self.down_letter = QtWidgets.QPushButton(self.frame_2)
        self.down_letter.setStyleSheet("border-top:1px solid white;\n"
"border-bottom:1px solid white;\n"
"border-left:0px solid white;\n"
"border-right:1px solid white;\n"
"border-top-right-radius:3px;\n"
"border-bottom-right-radius:3px")
        self.down_letter.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/ico/down_arrow_1209032_easyicon.net.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.down_letter.setIcon(icon3)
        self.down_letter.setIconSize(QtCore.QSize(15, 20))
        self.down_letter.setCheckable(True)
        self.down_letter.setObjectName("down_letter")
        self.horizontalLayout_2.addWidget(self.down_letter)
        self.verticalLayout_4.addWidget(self.frame_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setStyleSheet("font-family: 宋体;\n"
"font-size: 11pt;\n"
"color: #FFFFFF")
        self.page_2.setObjectName("page_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.page_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.page_2)
        self.scrollArea_2.setStyleSheet("background:transparent;\n"
"border:none")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 740, 566))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_7 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_6.addWidget(self.label_7)
        self.frame_3 = QtWidgets.QFrame(self.scrollAreaWidgetContents_2)
        self.frame_3.setStyleSheet("QPushButton:checked{\n"
"image: url(:/ico/checked_1206678_easyicon.net.svg);\n"
"padding:8px;\n"
"border:1px solid red}")
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.t_1 = QtWidgets.QPushButton(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.t_1.sizePolicy().hasHeightForWidth())
        self.t_1.setSizePolicy(sizePolicy)
        self.t_1.setMaximumSize(QtCore.QSize(50, 50))
        self.t_1.setStyleSheet("background-color:#E6E0D3;\n"
"border-radius: 25px;\n"
"width: 50px;\n"
"height:50px;\n"
"color:#575048")
        self.t_1.setText("")
        self.t_1.setCheckable(True)
        self.t_1.setObjectName("t_1")
        self.gridLayout.addWidget(self.t_1, 0, 0, 1, 1)
        self.t_2 = QtWidgets.QPushButton(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.t_2.sizePolicy().hasHeightForWidth())
        self.t_2.setSizePolicy(sizePolicy)
        self.t_2.setStyleSheet("background-color:#EBDBAE;\n"
"border-radius: 25px;\n"
"width: 50px;\n"
"height:50px;\n"
"color:#49423A")
        self.t_2.setText("")
        self.t_2.setCheckable(True)
        self.t_2.setObjectName("t_2")
        self.gridLayout.addWidget(self.t_2, 0, 1, 1, 1)
        self.t_3 = QtWidgets.QPushButton(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.t_3.sizePolicy().hasHeightForWidth())
        self.t_3.setSizePolicy(sizePolicy)
        self.t_3.setStyleSheet("background-color:#D3E3D3;\n"
"border-radius: 25px;\n"
"width: 50px;\n"
"height:50px;\n"
"color:#49423A")
        self.t_3.setText("")
        self.t_3.setCheckable(True)
        self.t_3.setObjectName("t_3")
        self.gridLayout.addWidget(self.t_3, 0, 2, 1, 1)
        self.t_4 = QtWidgets.QPushButton(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.t_4.sizePolicy().hasHeightForWidth())
        self.t_4.setSizePolicy(sizePolicy)
        self.t_4.setStyleSheet("background-color:#E8F3F5;\n"
"border-radius: 25px;\n"
"width: 50px;\n"
"height:50px;\n"
"color:#49423A")
        self.t_4.setText("")
        self.t_4.setCheckable(True)
        self.t_4.setObjectName("t_4")
        self.gridLayout.addWidget(self.t_4, 0, 3, 1, 1)
        self.t_5 = QtWidgets.QPushButton(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.t_5.sizePolicy().hasHeightForWidth())
        self.t_5.setSizePolicy(sizePolicy)
        self.t_5.setStyleSheet("background-color:#F7E9E8;\n"
"border-radius: 25px;\n"
"width: 50px;\n"
"height:50px;\n"
"color:#49423A")
        self.t_5.setText("")
        self.t_5.setCheckable(True)
        self.t_5.setObjectName("t_5")
        self.gridLayout.addWidget(self.t_5, 1, 0, 1, 1)
        self.t_6 = QtWidgets.QPushButton(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.t_6.sizePolicy().hasHeightForWidth())
        self.t_6.setSizePolicy(sizePolicy)
        self.t_6.setStyleSheet("background-color:#E5E5E4;\n"
"border-radius: 25px;\n"
"width: 50px;\n"
"height:50px;\n"
"color:#49423A")
        self.t_6.setText("")
        self.t_6.setCheckable(True)
        self.t_6.setObjectName("t_6")
        self.gridLayout.addWidget(self.t_6, 1, 1, 1, 1)
        self.t_dark = QtWidgets.QPushButton(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.t_dark.sizePolicy().hasHeightForWidth())
        self.t_dark.setSizePolicy(sizePolicy)
        self.t_dark.setStyleSheet("background-color:#474947;\n"
"border-radius: 25px;\n"
"width: 50px;\n"
"height:50px")
        self.t_dark.setText("")
        self.t_dark.setCheckable(True)
        self.t_dark.setObjectName("t_dark")
        self.gridLayout.addWidget(self.t_dark, 1, 2, 1, 1)
        self.t_8 = QtWidgets.QPushButton(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.t_8.sizePolicy().hasHeightForWidth())
        self.t_8.setSizePolicy(sizePolicy)
        self.t_8.setStyleSheet("background-color:#FFFFFF;\n"
"border-radius: 25px;\n"
"width: 50px;\n"
"height:50px;\n"
"color:#49423A")
        self.t_8.setText("")
        self.t_8.setCheckable(True)
        self.t_8.setObjectName("t_8")
        self.gridLayout.addWidget(self.t_8, 1, 3, 1, 1)
        self.horizontalLayout_3.addLayout(self.gridLayout)
        spacerItem2 = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout_6.addWidget(self.frame_3)
        self.frame_5 = QtWidgets.QFrame(self.scrollAreaWidgetContents_2)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_5.setContentsMargins(0, -1, -1, -1)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_12 = QtWidgets.QLabel(self.frame_5)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_5.addWidget(self.label_12)
        self.checkBox_2 = QtWidgets.QCheckBox(self.frame_5)
        self.checkBox_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.checkBox_2.setText("")
        self.checkBox_2.setObjectName("checkBox_2")
        self.horizontalLayout_5.addWidget(self.checkBox_2)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem3)
        self.verticalLayout_6.addWidget(self.frame_5)
        self.frame_4 = QtWidgets.QFrame(self.scrollAreaWidgetContents_2)
        self.frame_4.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_10 = QtWidgets.QLabel(self.frame_4)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_4.addWidget(self.label_10)
        self.pushButton_4 = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_4.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_4.setStyleSheet("QPushButton{border:1px solid white;border-radius:3px}\n"
"QPushButton:hover{border:1px solid #CC295F;border-radius:3px}")
        self.pushButton_4.setText("")
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_4.addWidget(self.pushButton_4)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem4)
        self.label_11 = QtWidgets.QLabel(self.frame_4)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_4.addWidget(self.label_11)
        self.pushButton_5 = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_5.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_5.setStyleSheet("QPushButton{border:1px solid white;border-radius:3px}\n"
"QPushButton:hover{border:1px solid #CC295F;border-radius:3px}")
        self.pushButton_5.setText("")
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_4.addWidget(self.pushButton_5)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem5)
        self.verticalLayout_6.addWidget(self.frame_4)
        self.frame_11 = QtWidgets.QFrame(self.scrollAreaWidgetContents_2)
        self.frame_11.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_11.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_11.setObjectName("frame_11")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.frame_11)
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_13 = QtWidgets.QLabel(self.frame_11)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_11.addWidget(self.label_13)
        spacerItem6 = QtWidgets.QSpacerItem(7, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem6)
        self.background_button = BorderButton(self.frame_11)
        self.background_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.background_button.setStyleSheet("")
        self.background_button.setText("")
        self.background_button.setObjectName("background_button")
        self.horizontalLayout_11.addWidget(self.background_button)
        spacerItem7 = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem7)
        self.his_button = QtWidgets.QPushButton(self.frame_11)
        self.his_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.his_button.setStyleSheet("QPushButton{border:none}\n"
"QPushButton:hover{background-color:  rgba(217, 217, 217, 120)}\n"
"")
        self.his_button.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/ico/省略号.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.his_button.setIcon(icon4)
        self.his_button.setObjectName("his_button")
        self.horizontalLayout_11.addWidget(self.his_button)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem8)
        self.verticalLayout_6.addWidget(self.frame_11)
        self.frame_14 = QtWidgets.QFrame(self.scrollAreaWidgetContents_2)
        self.frame_14.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_14.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_14.setObjectName("frame_14")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout(self.frame_14)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_15 = QtWidgets.QLabel(self.frame_14)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_14.addWidget(self.label_15)
        self.use_image_checkbox = QtWidgets.QCheckBox(self.frame_14)
        self.use_image_checkbox.setStyleSheet("\n"
"QCheckBox::indicator{\n"
"    width: 50px;\n"
"    height: 28px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked{\n"
"    image:url(:/ico/开关-关.svg);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked{\n"
"    image:url(:/ico/开关-开.svg);\n"
"}\n"
"")
        self.use_image_checkbox.setIconSize(QtCore.QSize(30, 30))
        self.use_image_checkbox.setCheckable(True)
        self.use_image_checkbox.setChecked(True)
        self.use_image_checkbox.setObjectName("use_image_checkbox")
        self.horizontalLayout_14.addWidget(self.use_image_checkbox)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_14.addItem(spacerItem9)
        self.verticalLayout_6.addWidget(self.frame_14)
        spacerItem10 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem10)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.verticalLayout_3.addWidget(self.scrollArea_2)
        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setStyleSheet("font-family: 宋体;\n"
"font-size: 11pt;\n"
"color: #FFFFFF")
        self.page_3.setObjectName("page_3")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.page_3)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 20)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.frame_12 = QtWidgets.QFrame(self.page_3)
        self.frame_12.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_12.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_12.setObjectName("frame_12")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout(self.frame_12)
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_14 = QtWidgets.QLabel(self.frame_12)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_12.addWidget(self.label_14)
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem11)
        self.verticalLayout_5.addWidget(self.frame_12)
        self.frame_13 = QtWidgets.QFrame(self.page_3)
        self.frame_13.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_13.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_13.setObjectName("frame_13")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout(self.frame_13)
        self.horizontalLayout_13.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.read_combo = QtWidgets.QComboBox(self.frame_13)
        self.read_combo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.read_combo.setStyleSheet("QComboBox{border: 1px solid white;border-radius:3px}\n"
"QComboBox:focus{border: 1px solid #CC295F;border-radius:3px}\n"
"\n"
"QComboBox QAbstractItemView\n"
"{border: 1px solid rgb(161,161,161);\n"
"outline:0px\n"
"}\n"
"QComboBox QAbstractItemView::item\n"
"{ height: 24px;\n"
"outline:0px\n"
"}\n"
"QComboBox QAbstractItemView::item:hover\n"
"{ height: 24px;background: black;color:#CC295F\n"
"}\n"
"QComboBox QAbstractItemView::item:selected\n"
"{    \n"
"    background-color:#2B2B2B;\n"
"    color: white;\n"
"}\n"
"\n"
"")
        self.read_combo.setObjectName("read_combo")
        self.read_combo.addItem("")
        self.read_combo.addItem("")
        self.horizontalLayout_13.addWidget(self.read_combo)
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem12)
        self.verticalLayout_5.addWidget(self.frame_13)
        spacerItem13 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem13)
        self.stackedWidget.addWidget(self.page_3)
        self.verticalLayout.addWidget(self.stackedWidget)

        self.retranslateUi(Form)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "文字"))
        self.pushButton_2.setText(_translate("Form", "阅读背景"))
        self.pushButton_3.setText(_translate("Form", "其他"))
        self.label_8.setText(_translate("Form", "阅读字体"))
        self.label_4.setText(_translate("Form", "使用粗体"))
        self.checkBox.setText(_translate("Form", "开"))
        self.label.setText(_translate("Form", "字体大小: 25"))
        self.label_2.setText(_translate("Form", "多倍行距: 5"))
        self.label_5.setText(_translate("Form", "首行缩进: 20"))
        self.label_6.setText(_translate("Form", "边距大小: 20"))
        self.label_9.setText(_translate("Form", "屏幕亮度: 20"))
        self.label_3.setText(_translate("Form", "字符间距"))
        self.label_7.setText(_translate("Form", "阅读主题"))
        self.label_12.setText(_translate("Form", "自定义阅读主题"))
        self.label_10.setText(_translate("Form", "背景色:"))
        self.label_11.setText(_translate("Form", "字体色:"))
        self.label_13.setText(_translate("Form", "背景图:"))
        self.label_15.setText(_translate("Form", "使用背景图片:"))
        self.use_image_checkbox.setText(_translate("Form", "开"))
        self.label_14.setText(_translate("Form", "翻页方式"))
        self.read_combo.setItemText(0, _translate("Form", "滚动"))
        self.read_combo.setItemText(1, _translate("Form", "水平"))
from .customwidgets import BorderButton, FontCombobox, HoverButton
