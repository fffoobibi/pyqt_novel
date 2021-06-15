listwidget_v_scrollbar = '''
                QScrollBar:vertical {
                    background: #E4E4E4;
                    padding: 0px;
                    border-radius: 3px;
                    max-width: 12px;
                }
                QScrollBar::handle:vertical {
                    background: lightgray;
                    min-height: 20px;
                    border-radius: 3px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #00BB9E;
                }
                QScrollBar::handle:vertical:pressed {
                    background: #00BB9E;
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
                }'''

listwidget_h_scrollbar = '''
                QScrollBar:horizontal {
                    background: #E4E4E4;
                    padding: 0px;
                    border-radius: 3px;
                    max-height: 12px;
                }
                QScrollBar::handle:horizontal {
                    background: lightgray;
                    min-width: 20px;
                    border-radius: 3px;
                }
                QScrollBar::handle:horizontal:hover {
                    background: #00BB9E;
                }
                QScrollBar::handle:horizontal:pressed {
                    background: #00BB9E;
                }
                QScrollBar::add-page:horizontal {
                    background: none;
                }
                QScrollBar::sub-page:horizontal {
                    background: none;
                }
                QScrollBar::add-line:horizontal {
                    background: none;
                }
                QScrollBar::sub-line:horizontal {
                    background: none;
                }'''

read_v_style = '''
                QScrollBar:vertical {
                    background: #161819;
                    padding: 0px;
                    border-radius: 3px;
                    max-width: 12px;
                }
                QScrollBar::handle:vertical {
                    background: #666666;
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
listwidget_style = '''
    QListWidget::Item:hover{
    background-color: white;
    color:black;
    border:none}
    QListWidget::Item{
    border-bottom:1px solid rgb(212, 212, 212)}
    QListWidget::Item:selected{
    background-color: lightgray;
    color:black}
    QListWidget{outline:0px; background-color: transparent;border:none}
    '''

listview_style = '''
    QListView::item:hover{
    background: white;
    color:black;
    border:none}

    QListView::item{
    border-bottom:1px solid rgb(212, 212, 212)}

    QListView::item:selected{
    background: lightgray;
    color:black}

    QListView{outline:0px;background: transparent;border:none}
'''

site_button_listview_style = '''
    QListView::item:hover{
    background: white;
    color:black;}
    QListView::item{
    border-bottom:1px solid rgb(212, 212, 212)}
    QListView{outline:0px;background: transparent;border:1px solid lightgray}
'''

site_button_v_scrollbar = '''
                QScrollBar:vertical {
                    background: #E4E4E4;
                    padding: 0px;
                    max-width: 4px;
                }
                QScrollBar::handle:vertical {
                    background: lightgray;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #00BB9E;
                }
                QScrollBar::handle:vertical:pressed {
                    background: #00BB9E;
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
                }'''

listwidget_img_style = '''
    QListWidget::Item:hover{
    background-color:transparent;
    color:black}
    QListWidget::Item{
    border-bottom:1px solid rgb(212, 212, 212)}
    QListWidget::Item:selected{
    background-color: white;
    color:black}
    QListWidget{outline:0px; background-color: transparent;border:none}'''

iconslistwidget_style = '''
QListWidget::Item:hover{
background-color:rgba(50, 50, 50, 120);
color:black;
border-radius:5px}

QListWidget::Item{
border-bottom:1px solid rgb(212, 212, 212)}
QListWidget::Item:selected{
background-color: white;
color:black;
border-radius:5px}
QListWidget{outline:0px; background-color: transparent;border:none}
'''

listwidget_img2_style = '''
    QListWidget::Item:hover{
    background-color:transparent;
    color:black}
    QListWidget::Item{
    border-bottom:1px solid rgb(212, 212, 212)}
    QListWidget::Item:selected{
    background-color: white;
    color:black;
    border-radius:5px}
    QListWidget{outline:0px; background-color: transparent;border:none}'''

submit_listwidget_style = '''
    QListWidget::Item:hover{
        background-color:transparent;
        color:black}
    QListWidget::Item{
        /*border-bottom:1px solid rgb(212, 212, 212)*/}
    QListWidget::Item:selected{
        background-color: transparent;
        color:black;
        border-radius:5px}
    QListWidget{
        outline:0px; background-color: transparent;
        border-top:1px solid lightgray;
        border-bottom:1px solid lightgray;
        border-left:0px solid lightgray;
        border-right:0px solid lightgray;}
'''
listwidget_selected_style = '''
    QListWidget::Item:hover:active{
    background-color:lightgray;
    color:black}
    QListWidget::Item{
    border-bottom:1px solid rgb(212, 212, 212)}
    QListWidget::Item:selected{
    color:black}
    QListWidget{outline:0px; background-color: transparent;border:none}'''


search_combo_style = '''
QComboBox {
    font-family: "Microsoft YaHei";
    color: #000000;
    font-weight: bold;
    height: auto;
    padding-left: 1px;
    border-width: 1px;
    border-style: solid;
    border-color: lightgray;
    border-top-left-radius: 5px;
    border-bottom-left-radius: 5px;
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
}

QComboBox::drop-down{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width:30px;
    height:36px;
    border-left: none;
}
QComboBox::down-arrow{
    width:  30px;
    height: 30px;
    image: url(':/ico/arrow_drop_down.svg')
}
QComboBox:on{ // 激活状态
    color: red;
    background-color: lightgray;
}
QComboBox:editable {
    color: white;
    background-color: #2E3648;
}

'''

search_combo_listview_style = '''
QListView {
    outline: 0px solid gray;   /* 选定项的虚框 */
    color: black;
     /* selection-background-color: lightgreen;  整个下拉窗体被选中项的背景色 */
}
QListView::item:hover {
    color: black;
    background-color: lightgreen;    /*整个下拉窗体越过每项的背景色 */
}
QListView::item{
    color: black;
    background-color: white;    /*整个下拉窗体越过每项的背景色 */
}
'''
font_combo_listwidget_style= '''
    QListWidget::Item:hover:active{
    background-color: rgba(153, 149, 149, 80);
    color:white}
    QListWidget{outline:0px; background-color: black; color: white; border: 1px solid lightgray}
'''

menu_style = '''
    QMenu {
    background-color : rgb(253,253,254);
    padding:5px;
    border:1px solid lightgray;
    }
    QMenu::item {
        font-size:9pt;
        color: rgb(0,0,0);
        background-color:rgb(253,253,254);
        padding: 10px 3px 8px 3px;
        margin: 3px 3px;
    }
    QMenu::item:selected {
        background-color : rgb(236,236,237);
    }
    QMenu::icon:checked {
        background: rgb(253,253,254);
        position: absolute;
        top: 1px;
        right: 1px;
        bottom: 1px;
        left: 1px;
    }
    QMenu::icon:checked:selected {
        background-color : rgb(236,236,237);
        background-image: url(:/space_selected.png);
    }
    QMenu::separator {
        height: 2px;
        background: rgb(235,235,236);
        margin-left: 10px;
        margin-right: 10px;
    }'''

menu_style2 = '''
    QMenu {
    background-color : #BEBEBE;
    border:1px solid #BEBEBE;
    }
    QMenu::item {
        font-size:9pt;
        color: black;
        background-color:#BEBEBE;
        padding: 5px 3px 8px 3px;
        margin: 3px 3px;
    }
    QMenu::item:selected {
        background-color : #f4f4f4;
    }
    QMenu::separator {
        height: 2px;
        background: #CECDCD;
        margin-left: 2px;
        margin-right: 2px;
    }
'''
from PyQt5.QtGui import QColor

color = {'undo': '#787C8A', 'doing': '#9ACD32',
         'done': '#F08080', 'down_ok': '#27A6F4',
         'down_fail': '#EABF4A', 
         'icon_hover_color': QColor(50, 50, 50, 120)}

COLOR = color

frame_less_stylesheet = """
/*标题栏*/

/*最小化最大化关闭按钮通用默认背景*/
#buttonMinimum,#buttonMaximum,#buttonClose {
    border: none;
}
/*悬停*/
#buttonMinimum:hover,#buttonMaximum:hover {
    color: white;
}
#buttonClose:hover {
    color: white;
}
/*鼠标按下不放*/
#buttonMinimum:pressed,#buttonMaximum:pressed {
    background-color: Firebrick;
}
#buttonClose:pressed {
    color: white;
    background-color: Firebrick;
}
"""

menubar_button_style = '''
QPushButton{background-color:transparent; border:none;text-align:right;font-family: 微软雅黑;font-size:9pt}
QPushButton:hover{color: #474746;background-color:#DBDBDB}
QPushButton:pressed{color: #474746;background-color:#DBDBDB} 
QPushButton::menu-indicator{image:none}'''

menu_button_style = '''
QPushButton{background-color:transparent; border: none; font-family: 微软雅黑}
QPushButton:hover{color: #474746;background-color:#DBDBDB; border:none}
QPushButton:pressed{color: #474746;background-color:#DBDBDB; border:none} '''
