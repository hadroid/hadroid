"""CERN Restaurants menu fetching module."""

import re

import requests

MENU_USAGE = '(menu | m) [<day>] [--yall]'


def wash_item(item):
    """Format some "ugly" menu items in a nicer way."""
    item['name'] = re.sub('\s\s+', ' ', item['name'].strip())
    if item['name'] == 'Pizza du jour 11.50 Pizza margherita 8.50':
        item['name'] = 'Pizza du jour / Pizza margherita'
        item['price'] = '11.50 / 8.50'
    elif item['name'] == 'Paillard de Dinde Onglet de Boeuf Saucisse de veau':
        item['name'] = 'Paillard de Dinde, Onglet de Boeuf, Saucisse de veau'
    return item


def fetch_menu(day='today'):
    """Fetch the menu."""
    r = requests.get('https://r1d2.herokuapp.com/{day}/r2'.format(day=day))
    return [wash_item(i) for i in r.json()['menu']]


def price_formatter(price):
    """Format price."""
    if isinstance(price, float):
        return '{:.2f}'.format(price)
    else:
        return price


def type_formatter(type_):
    """Format the menu item types with some emoji."""
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


def format_pretty_menu_msg(menu, day=None):
    """Format the menu with pretty words and pictures."""
    if not menu:
        return "Menu not available."
    items = []
    msg = ("{0}'s R2 selection:\n".format(day.title())) if day else ''
    for i in menu:
        items.append('* {name} ({price} CHF) {type}\n'.format(
            name=i['name'],
            price=price_formatter(i['price']),
            type=type_formatter(i['type']),
        ))
    return msg + '\n'.join(items)


def menu(client, args, msg_json):
    day = (args['<day>'] or 'today').lower()
    days = ['today', 'tomorrow', 'monday', 'tuesday', 'wednesday',
            'thursday', 'friday']
    if day not in days:
        msg = "Please specify a correct day ('today', 'tomorrow'" \
              " or 'monday' to 'friday')."
    else:
        msg = ""
        if args['--yall']:
            msg += ":fork_and_knife: Hey Y'@/all," \
                " it's lunch time! :clock12:\n"
        menu = fetch_menu(day)
        msg += format_pretty_menu_msg(menu, day=day)
    client.send(msg)
