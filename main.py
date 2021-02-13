from dearpygui.core import *
from dearpygui.simple import *


def click_impl(sender, data):
    print("cc")
    print(sender)
    print(data)
    open_file_dialog()


def SetGT():
    set_value("GT", get_value("NG"))


def SetPdfDir():
    select_directory_dialog(callback=ApplyPdfDir)


def ApplyPdfDir(_, data):
    log_debug(data)
    set_value("DD", data[0])


# themes = ["Dark", "Light", "Classic", "Dark 2", "Grey", "Dark Grey", "Cherry", "Purple", "Gold", "Red"]
add_additional_font("NotoSansTC-Black.otf", 20, "chinese_full")
set_main_window_size(1280, 720)
set_main_window_pos(50, 50)
set_main_window_title("Dear Score Sheet Pdf Parser 2.0")
set_main_window_resizable(False)
set_theme("Light")

with window("main"):
    with menu_bar("Main menu bar"):
        add_menu_item("選擇目錄", callback=SetPdfDir)
        add_menu_item('開始解析')
        add_spacing(count=2)
        add_input_int('幾群?', min_value=2, max_value=15, default_value=5, width=100, source="NG", callback=SetGT)
        add_spacing(count=2)
        add_menu_item('分群')
        add_menu_item('關於')

with window("Files",
            width=400,
            height=696,
            x_pos=0,
            y_pos=24,
            no_resize=True,
            no_move=True,
            no_title_bar=True):
    add_text(str(get_value("NG")), source='GT')
    add_text("Is this good?", bullet=True)
    add_text("Is this good?", bullet=True, source="DD")
    add_drawing("PlotArea", width=200, height=200, )
    add_simple_plot("ddd", value=[1, 7, 2, 0.3], height=100)

draw_rectangle("PlotArea", [0, 0], [200, 200], rounding=3, color=[200, 200, 200])
draw_line("PlotArea", [10, 10], [100, 100], [255, 128, 102], 3)
draw_line("PlotArea", [50, 130], [70, 30], [212, 18, 18], 8)

# with window("Info",
#             width= 880,
#             height=696,
#             x_pos=400,
#             y_pos=24,
#             no_resize=True,
#             no_move=True,
#             no_title_bar=True):
#     add_text('hey')
#     add_button('bbbb', callback=click_impl)


show_documentation()
show_style_editor()
# show_debug()
# show_about()
# show_metrics()
show_logger()

start_dearpygui(primary_window="main")
