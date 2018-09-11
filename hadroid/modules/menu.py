"""CERN Restaurants menu fetching module.

Required configuration:
NOVAE_TOKEN = '<token-from-browser-localStorage>'
"""

import re
from datetime import date, timedelta
from itertools import groupby

import requests

from hadroid import C

MENU_USAGE = '(menu | m) [<day>] [--yall]'

def _next_weekday(day_num):
    d = date.today()
    while d.weekday() != day_num:
        d += timedelta(days=1)
    return d


DATE_MAPPING = {
    'today': lambda: date.today(),
    'tomorrow': lambda: date.today() + timedelta(days=1),
    'monday': lambda: _next_weekday(0),
    'tuesday': lambda: _next_weekday(1),
    'wednesday': lambda: _next_weekday(2),
    'thursday': lambda: _next_weekday(3),
    'friday': lambda: _next_weekday(4),
}


MEN = [
    ('Le Marché', 'Fajitas de poulet aux épices douces'),
    ('La Saison', 'Poisson de la pêche du jour'),
    ('Végétarien', 'Gyoza de légumes et lait de coco au curry vert'),
    ('Pâte du jour', 'Spaghetti à la bolognaise'),
    ('La Spécialité', 'SUSHIMAN (13.00 - 17.00)'),
    ('Le Grill', 'Schüblig de St-Gall 8.50'),
    ('Le Grill no 1', 'Paillard de dinde'),
    ('Le Grill no 2', 'Bavette de bœuf'),
    ('Pizza du jour', 'Pizza du jour'),
    ('Pizza', 'Pizza Margarita'),
]


def wash_item(item):
    """Format some "ugly" menu items in a nicer way."""
    name = re.sub('\s\s+', ' ', item['title']['fr'].strip())
    type_ = item['model']['title'].strip()
    if type_.lower().startswith('le grill'):
        type_ = 'Grill'
    elif type_.lower().startswith('végétarien'):
        type_ = 'Vegetarian'
    elif type_.lower().startswith('pâte du jour'):
        type_ = 'Pasta'
    elif type_.lower().startswith('la spécialité'):
        type_ = 'Speciality'
    elif type_.lower().startswith('pizza'):
        type_ = 'Pizza'
    price = item['prices'][0]['price'] or None
    return {'name': name, 'type': type_, 'price': price}


def fetch_menu(day='today'):
    """Fetch the menu."""
    d = DATE_MAPPING[day]().isoformat()
    url = 'https://api.mynovae.ch/en/api/connected/menu/{date}'.format(date=d)
    headers = {'Authorization': 'Bearer {}'.format(C.NOVAE_TOKEN)}
    r = requests.get(url, headers=headers, params={'empty': 1, 'public': 1})
    r2_menu = [r for r in r.json() if 'R2' in r['name']][0].get('menus', [])
    items = [wash_item(i) for i in r2_menu]
    return sorted(items, key=lambda i: i['type'])


def price_formatter(price):
    """Format price."""
    if isinstance(price, float):
        return '{:.2f}'.format(price)
    else:
        return price


def type_formatter(type_):
    """Format the menu item types with some emoji."""
    return {
        'Vegetarian': ':herb:',
        'Pasta': ':spaghetti:',
        'Grill': ':meat_on_bone:',
        'Pizza': ':pizza:',
        'Speciality': ':ok_hand:',
        'La Saison': ':fish: / :pig: / :cow:',
        'Le Marché': ':man_with_gua_pi_mao:',
    }.get(type_, '')


def format_pretty_menu_msg(menu, day=None):
    """Format the menu with pretty words and pictures."""
    if not menu:
        return "Menu not available."
    lines = []
    msg = ("{0}'s R2 selection:\n".format(day.title())) if day else ''
    for type_, item_group in groupby(menu, lambda i: i['type']):
        lines.append('* {type} {emoji}'.format(
            type=type_,
            emoji=type_formatter(type_)))
        for i in item_group:
            if i['price']:
                lines.append('  * {name} ({price} CHF)'.format(
                    name=i['name'],
                    price=price_formatter(i['price'] or ''),
                ))
            else:
                lines.append('  * {name}'.format(name=i['name']))
    return msg + '\n'.join(lines)


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
