import requests
import re


def item_cleaner(item):
    """Format some pre-defined items in a nicer way."""
    item['name'] = re.sub('\s\s+', ' ', item['name'].strip())
    if item['name'] == 'Pizza du jour 11.50 Pizza margherita 8.50':
        item['name'] = 'Pizza du jour / Pizza margherita'
        item['price'] = '11.50 / 8.50'
    elif item['name'] == 'Paillard de Dinde Onglet de Boeuf Saucisse de veau':
        item['name'] = 'Paillard de Dinde, Onglet de Boeuf, Saucisse de veau'
    return item


def fetch_menu(day='today'):
    r = requests.get('https://r1d2.herokuapp.com/{day}/r2'.format(day=day))
    return [item_cleaner(i) for i in r.json()['menu']]


def price_formatter(price):
    if isinstance(price, float):
        return '{:.2f}'.format(price)
    else:
        return price


def type_formatter(type_):
    emoji = {
        'vegetarian': ':herb:',
        'grill': ':meat_on_bone:',
        'pizza': ':pizza:',
        'speciality': ':ok_hand:',
    }
    if type_ in emoji:
        return emoji[type_]
    else:
        return ''


def format_pretty_menu_msg(menu):
    msg = ":fork_and_knife: Hey Y'@/all, it's lunch time! :clock12:\n"
    msg += "Today's R2 selection:\n"
    items = []
    for i in menu:
        items.append('* {name} ({price} CHF) {type}\n'.format(
            name=i['name'],
            price=price_formatter(i['price']),
            type=type_formatter(i['type']),
        ))
    msg += '\n'.join(items)
    return msg


if __name__ == '__main__':
    menu = fetch_menu()
    menu2 = fetch_menu('tomorrow')
    print(format_pretty_menu_msg(menu))
    print(format_pretty_menu_msg(menu2))
