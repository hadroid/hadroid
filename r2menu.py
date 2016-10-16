import requests
import datetime
import sys
import re


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


def parse_menu(menu_html):
    from pyquery import PyQuery
    pq = PyQuery(menu_html)
    # yup... they close <span> with </font>
    menu_html = menu_html.replace("</font>", "</span>")
    topmenus = [e.text for e in pq('table.menuRestaurant tr td.typeMenu')]
    days = [e.text for e in pq('table.menuRestaurant tr td.EnteteMenu')]
    dish_names = [e.text for e in pq(
        'table.HauteurMenu tr td table.HauteurMenu tr td span')]
    prices = [e.text for e in pq(
        'table.HauteurMenu tr td table.HauteurMenu tr td center table tr td')]
    dishes_prices = zip(*([iter(zip(dish_names, prices))] * 3))
    days_dishes = zip(days, dishes_prices)
    d = []
    for item in days_dishes:
        day, dish_prices = item
        dd = []  # daily dishes
        for entry in zip(dish_prices, topmenus):
            dish_price, typ = entry
            dish, price = dish_price
            price = '' if price is None else price
            dd.append({
                'type': typ.strip(),
                'name': re.sub('\s\s+', ' ', dish.strip()),
                'price': price.strip(),
            })
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
    if price is None:
        return ''
    if price.strip().endswith('.-'):
        return price[:-2] + ' CHF'
    else:
        return price + ' CHF'


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
    day_of_week = day_of_week or datetime.datetime.now().weekday()
    if day_of_week > 4:
        day_of_week = 4
        print('Showing menu for last Friday')
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
