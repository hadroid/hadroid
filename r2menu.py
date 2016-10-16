import requests
import datetime
import sys
import re
from pyquery import PyQuery


def fetch_menu(menu_name):
    from config import REQUESTS

    url = REQUESTS[menu_name]['url']
    headers = REQUESTS[menu_name]['headers']
    text = requests.get(url, headers=headers).text
    return text


def mock_menu():
    with open("menu2.html", "r") as fp:
        text = fp.read()
    return text


def type_parser(type_):
    type_ = type_.strip()
    if type_ == 'Menu 1':
        return 'Menu1'
    return type_


def price_parser(price):
    if price is None:
        return ''
    price = price.strip()
    if price.endswith('.-'):
        return price[:-2]
    return price


def name_parser(name):
    return re.sub('\s\s+', ' ', name.strip())


def format_menu_item(type_, dish, price):
    if name_parser(dish) == 'Pizza du jour 11.50 Pizza margherita 8.50':
        dish = 'Pizza du jour / Pizza margherita'
        price = '11.50 / 8.50'
    elif name_parser(dish) == \
            'Paillard de Dinde Onglet de Boeuf Saucisse de veau':
        dish = 'Paillard de Dinde, Onglet de Boeuf, Saucisse de veau'
    return {
        'type': type_parser(type_),
        'name': name_parser(dish),
        'price': price_parser(price),
    }


def parse_menu(menu_html):
    # yup... they close <span> with </font>
    menu_html = menu_html.replace("</font>", "</span>")
    menu_html = menu_html.replace("<br />", "")
    menu_html = menu_html.replace("\n", "")
    pq = PyQuery(menu_html)
    topmenus = [e.text for e in pq('table.menuRestaurant tr td.typeMenu')]
    days = [e.text for e in pq('table.menuRestaurant tr td.EnteteMenu')]
    query = 'table.HauteurMenu tr td table.HauteurMenu tr td span'
    dish_names = [e.text for e in pq(query)]
    prices = [e.text for e in pq(
        'table.HauteurMenu tr td table.HauteurMenu tr td center table tr td')]
    dishes_prices = zip(*([iter(zip(dish_names, prices))] * 3))
    days_dishes = zip(days, dishes_prices)
    d = []
    for item in days_dishes:
        day, dish_prices = item
        dd = []  # daily dishes
        for entry in zip(dish_prices, topmenus):
            dish_price, type_ = entry
            dish, price = dish_price
            price = '' if price is None else price
            dd.append(format_menu_item(type_, dish, price))
        d.append(dd)
    return d


def fetch_full_weekly_menu():
    menu1_html = fetch_menu('R2-Menu1')
    menu2_html = fetch_menu('R2-Menu2')
    d1 = parse_menu(menu1_html)
    d2 = parse_menu(menu2_html)
    zip(d1, d2)
    d = [i1 + i2 for i1, i2 in zip(d1, d2)]
    return d


def name_formatter(name):
    return name


def price_formatter(price):
    if price:
        return '({} CHF)'.format(price)
    else:
        return price


def type_formatter(type_):
    emoji = {
        'Végétarien': ':herb:',
        'Le Grill': ':meat_on_bone:',
        'pizza': ':pizza:',
        'Spécialité': ':ok_hand:',
    }
    if type_ in emoji:
        return emoji[type_]
    else:
        return ''


def menu_for_the_day(day_of_week=None):
    weekly_menu = fetch_full_weekly_menu()
    if day_of_week is None:
        day_of_week = datetime.datetime.now().weekday()
    if day_of_week > 4:
        raise Exception("Menu of the day not available for weekend.")
    today = weekly_menu[day_of_week]
    msg = ":fork_and_knife: Hey Y'@/all, it's lunch time! :clock12:\n"
    msg += "Today's R2 selection:\n"
    items = []
    for i in today:
        items.append('* *{name}* {price} {type}\n'.format(
            name=name_formatter(i['name']),
            price=price_formatter(i['price']),
            type=type_formatter(i['type']),
        ))
    msg += '\n'.join(items)
    return msg


if __name__ == '__main__':
    day_of_week = int(sys.argv[1])
    print(menu_for_the_day(day_of_week))
