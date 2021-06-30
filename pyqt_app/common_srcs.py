from enum import Enum
from PyQt5.QtGui import QColor, qRgba

class CommonPixmaps(object):
    
    state_pixmap = ':/ico/checked_1206678_easyicon.net.svg'
    app_ico = ':/ico/蜘蛛.svg'
    command_help_button = ':/ico/help_48px_1117324_easyicon.net.ico'
    command_exit_button = ':/ico/application_exit_48px_518826_easyicon.net.ico'

    menu_wifi_transfer = ':/ico/wifi_128px_1227275_easyicon.net.ico'
    menu_wifi_close = ':/ico/no_signal_128px_1227250_easyicon.net.ico'
    menu_wifi_address = ':/ico/wifi_1166921_easyicon.net.svg'

    menu_info_show = ':/ico/button_check_64px_562153_easyicon.net.ico'
    menu_info_close = ':/ico/button_cross_64px_562154_easyicon.net.ico'

    menu_search_fast = ':/ico/Lightning_128px_538217_easyicon.net.ico'
    menu_search_slow = ':/ico/ACDSee_128px_538159_easyicon.net.ico'
    menu_search_mode = ':/ico/lightning_1223070_easyicon.net.svg'

    menu_load_plugins = ':/ico/plugin_128px_1163826_easyicon.net.ico'

    menu_command = ':/ico/command_1187457_easyicon.net.svg'
    menu_logs = ':/ico/document_1302124_easyicon.net.svg'
    menu_debug = ':/ico/debug_1153442_easyicon.net.svg'

    novel_fresh_button = ':/ico/refresh_173px_1188146_easyicon.net.png'
    novel_fresh_fail = ':/ico/cloud_fail_72px_1137820_easyicon.net.png'

    pop_window_ico = ':/ico/checkbox_64.179271708683px_1137621_easyicon.net.png'

    gif_crawl_novel = ':/gif/5-121204194113-50.gif'

    read_mark_up = ':/ico/bookmark_144px_1201612_easyicon.net.png'

    hl_fresh_svg = ':/hl/hlrefresh_1233084_easyicon.net.svg'
    hl_menu_svg = ':/hl/menu_1223077_easyicon.net.svg'
    hl_more_svg = ':/hl/navigation-more.svg'
    hl_leftarrow_svg = ':/hl/arrow_left_1223141_easyicon.net.svg'
    hl_book_mark = ':/hl/bookmark_1223025_easyicon.net.svg'
    hl_exit_read = ':/hl/270-cancel-circle.svg'
    hl_next_chapter = ':/hl/hangle-right.svg'
    hl_previous_chapter = ':/hl/hangle-left.svg'
    hl_skin_svg = ':/hl/skin.svg'
    hl_subs_read = ':/hl/阅读(2).svg'
    hl_other_button = ':/hl/切换.svg'

    chapter_read_state = ':/ico/verified_1222610_easyicon.net.svg'
    chapter_cached_state = ':/ico/已下载.png'

    theme_t_dark = ':/theme/hei.png'
    theme_t_1 = ':/theme/shennuan.png'
    theme_t_2 = ':/theme/huang.png'
    theme_t_3 = ':/theme/lv.png'
    theme_t_4 = ':/theme/lan.png'
    theme_t_5 = ''
    theme_t_6 = ':/theme/hui.png'
    theme_t_8 = ''

    selectdia_read_svg = ':/ico/阅读.svg'
    
    normal_button = ':/ico/close_512px_1175341_easyicon.net.png'
    hover_button = ':/ico/close_128px_1175741_easyicon.net.ico'


class StyleSheets(str, Enum):

    chapter_list_style = ''' 
        QListWidget::Item:hover:active{background-color: rgba(153, 149, 149, 80);color:#CCCCCC;border:none}
        QListWidget::Item{color:#CCCCCC; border:none;margin-left:10px}
        QListWidget::Item:selected{background-color: black;color: #CC295F}
        QListWidget{outline:0px; background-color: transparent; border:none}
    '''  # chapters_widget listwidget

    vertical_scroll_style = '''
        QScrollBar:vertical {background: black; padding: 0px;border-radius: 3px; max-width: 12px;}
        QScrollBar::handle:vertical {background: rgba(153, 149, 149, 80);min-height: 20px;border-radius: 3px;}
        QScrollBar::add-page:vertical {background: none;}
        QScrollBar::sub-page:vertical {background: none;}
        QScrollBar::add-line:vertical { background: none;}
        QScrollBar::sub-line:vertical {background: none; }
    '''  # more_widget scrollarea 

    pic_dialog_list_style = '''
            QListWidget::Item:hover:active{background-color: transparent; color:#CCCCCC;border:none}
            QListWidget::Item{color:#CCCCCC;border:none}
            QListWidget::Item:selected{ background-color: black;color: #CC295F}
            QListWidget{outline:0px; background-color: transparent; border:none}
        ''' # more_widget latest_dialog listwidget

    pic_dialog_style = '''
        QDialog{border:1px solid gray}QLabel{color:white; font-family: 微软雅黑}QPushButton{color:white;font-family: 微软雅黑}
        ''' # more_widget latest_dialog

    debugtextedit_v_scroll_style= '''
        QScrollBar:vertical {background: #E4E4E4;padding: 0px; border-radius: 3px;max-width: 12px;}
        QScrollBar::handle:vertical {background: lightgray; min-height: 20px; border-radius: 3px;}
        QScrollBar::handle:vertical:hover {background: #00BB9E;}
        QScrollBar::handle:vertical:pressed {background: #00BB9E;}
        QScrollBar::add-page:vertical { background: none;}
        QScrollBar::sub-page:vertical {background: none;}
        QScrollBar::add-line:vertical {background: none;}
        QScrollBar::sub-line:vertical {background: none;}
        '''
  
    debugtextedit_h_scroll_style = '''
        QScrollBar:horizontal {background: #E4E4E4;padding: 0px;border-radius: 3px;max-height: 12px;}
        QScrollBar::handle:horizontal {background: lightgray;min-width: 20px;border-radius: 3px;}
        QScrollBar::handle:horizontal:hover {background: #00BB9E;}
        QScrollBar::handle:horizontal:pressed {background: #00BB9E;}
        QScrollBar::add-page:horizontal {background: none;}
        QScrollBar::sub-page:horizontal {background: none;}
        QScrollBar::add-line:horizontal {background: none;}
        QScrollBar::sub-line:horizontal {background: none;}'''

    historycombobox_listview_style = '''
        QListView {outline: 0px;color: black;}
        QListView::item:hover {color: black;background-color: lightgreen;}
        QListView::item{color: black;background-color: white;}'''

    historycombobox_style = '''
        QComboBox {font-family: "Microsoft YaHei";color: #000000;font-weight: bold;padding-left: 1px;border: 1px solid lightgray;border-radius:5px}
        QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;}
        QComboBox::down-arrow{width:  30px;height: 30px;image: url(':/ico/arrow_drop_down.svg')}'''

    site_button_listview_style = '''
        QListView::item:hover{background: white;color:black;}
        QListView::item{border-bottom:1px solid rgb(212, 212, 212)}
        QListView{outline:0px;background: transparent;border:1px solid lightgray}'''

    menu_button_style = '''
        QPushButton{background-color:transparent; border: none; font-family: 微软雅黑}
        QPushButton:hover{color: #474746;background-color:#DBDBDB; border:none}
        QPushButton:pressed{color: #474746;background-color:#DBDBDB; border:none} '''

    menubar_button_style = '''
        QPushButton{background-color:transparent; border:none;text-align:right;font-family: 微软雅黑;font-size:9pt}
        QPushButton:hover{color: #474746;background-color:#DBDBDB}
        QPushButton:pressed{color: #474746;background-color:#DBDBDB} 
        QPushButton::menu-indicator{image:none}'''

    font_combo_listwidget_style= '''
        QListWidget::Item:hover:active{background-color: rgba(153, 149, 149, 80); color:white}
        QListWidget{outline:0px; background-color: black; color: white; border: 1px solid lightgray}'''

    menu_style= '''
        QMenu {background-color : rgb(253,253,254);padding:5px;border:1px solid lightgray;}
        QMenu::item {font-size:9pt;color: black;background-color:rgb(253,253,254);padding: 10px 3px 8px 3px;margin: 3px 3px;}
        QMenu::item:selected {background-color : rgb(236,236,237);}
        QMenu::icon:checked {background: rgb(253,253,254);position: absolute;top: 1px;right: 1px;bottom: 1px;left: 1px;}
        QMenu::icon:checked:selected {background-color : rgb(236,236,237);background-image: url(:/space_selected.png);}
        QMenu::separator {height: 2px;background: rgb(235,235,236);margin-left: 10px;margin-right: 10px;}'''

    menubar_menu_style = '''
        QMenu{background-color : #BEBEBE;border:1px solid #BEBEBE;}
        QMenu::item {font-size:9pt;color: black;background-color:#BEBEBE;padding: 5px 3px 8px 3px;margin: 3px 3px;}
        QMenu::item:selected {background-color : #f4f4f4;}
        QMenu::separator {height: 2px;background: #CECDCD;margin-left: 2px;margin-right: 2px;}'''

    dynamic_menu_style = '''
            QMenu {background-color : %s;padding:5px;border:1px solid %s}
            QMenu::item {font-size:9pt;background-color: %s;color: %s;padding: 10px 3px 8px 3px;margin: 3px 3px;}
            QMenu::item:selected { background-color : red;}
            QMenu::icon:checked {background: rgb(253,253,254); position: absolute;top: 1px;right: 1px;bottom: 1px;left: 1px;}
            QMenu::separator {height: 2px;background: rgb(235,235,236);margin-left: 10px;margin-right: 10px;}'''

    submit_list_style = '''
        QListWidget::Item:hover{background-color:transparent;color:black}
        QListWidget::Item{/*border-bottom:1px solid rgb(212, 212, 212)*/}
        QListWidget::Item:selected{background-color: transparent;color:black;border-radius:5px}
        QListWidget{outline:0px; background-color: transparent;border-top:1px solid lightgray;border-bottom:1px solid lightgray;
            border-left:0px solid lightgray;border-right:0px solid lightgray;}'''

    green_v_scroll_style = '''
        QScrollBar:vertical {background: #E4E4E4;padding: 0px;border-radius: 3px;max-width: 12px;}
        QScrollBar::handle:vertical {background: lightgray;min-height: 20px;border-radius: 3px;}
        QScrollBar::handle:vertical:hover {background: #00BB9E;}
        QScrollBar::handle:vertical:pressed {background: #00BB9E;}
        QScrollBar::add-page:vertical {background: none;}
        QScrollBar::sub-page:vertical {background: none;}
        QScrollBar::add-line:vertical {background: none;}
        QScrollBar::sub-line:vertical {background: none;}'''

    list_page_style = '''
        QListWidget::Item:hover{background-color: white; color:black; border:none}
        QListWidget::Item{border-bottom:1px solid rgb(212, 212, 212)}
        QListWidget::Item:selected{background-color: lightgray;color:black}
        QListWidget{outline:0px; background-color: transparent;border:none}
        '''
    icon_page_style = '''
        QListWidget::Item:hover{background-color:transparent;color:black}
        QListWidget::Item{border-bottom:1px solid rgb(212, 212, 212)}
        QListWidget::Item:selected{background-color: white;color:black;border-radius:5px}
        QListWidget{outline:0px; background-color: transparent;border:none}'''

    fileter_listview_style = '''
        QListView::item:hover{background: white;color:black;border:none}
        QListView::item{border-bottom:1px solid rgb(212, 212, 212)}
        QListView::item:selected{background: lightgray;color:black}
        QListView{outline:0px;background: transparent;border:none}'''
        
class COLORS(object):
    undo = '#787C8A'  # 任务初始颜色
    doing = '#9ACD32' # 下载中颜色
    done = '#F08080'  # 下载完成颜色
    down_ok = '#27A6F4'  # 已下载颜色
    down_fail = '#EABF4A' # 下载失败颜色
    icon_hover_color = QColor(50, 50, 50, 120) # 悬浮颜色

# print(QColor.fromRgba(qRgba(50, 50, 50, 120)))
# print(QColor('qrgba(50, 50, 50, 120)').isValid())
