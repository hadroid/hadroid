from ..r2menu import parse_menu


def test_parsing(menus_html, menus_parsed_expected):
    for menu_name, menu_html in menus_html.items():
        menu = parse_menu(menu_html)
        exp = menus_parsed_expected[menu_name]
        assert menu == exp
