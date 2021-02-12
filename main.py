from dearpygui.core import *
from dearpygui.simple import *

def click_impl(sender, data):
    print("cc")
    print(sender)
    print(data)
    open_file_dialog()

# themes = ["Dark", "Light", "Classic", "Dark 2", "Grey", "Dark Grey", "Cherry", "Purple", "Gold", "Red"]
set_main_window_size(1280, 720)
set_main_window_pos(50, 50)
set_main_window_title("成績單解析器成績單解析器2.0")
set_theme("Light")
add_additional_font("NotoSansTC-Black.otf", 20, "chinese_full")

show_documentation()
# show_debug()
# show_about()
# show_metrics()
# show_logger()

with window("main"):
    with menu_bar("Main menu bar"):
        add_menu_item('中文')
        add_menu_item('777')
        with menu("hey"):
            add_menu_item('456')
            add_menu_item('446')

        add_menu_item('good')


with window("files",
    width= 250,
    height=696,
    x_pos=0,
    y_pos=24,
    no_resize=True,
    no_move=True,
    no_title_bar=True):
    add_text('hey')
    add_button('click me!', callback=click_impl)


with window("Commands",
            width= 250,
            height=696,
            x_pos=250,
            y_pos=24,
            no_resize=True,
            no_move=True,
            no_title_bar=True):
    add_text('hey')
    add_button('bbbb', callback=click_impl)

with window("info",
            width= 780,
            height=696,
            x_pos=500,
            y_pos=24,
            no_resize=True,
            no_move=True,
            no_title_bar=True):
    add_text('hey')
    add_button('aaaa', callback=click_impl)

start_dearpygui(primary_window="main")
