import requests
import json
from menu import fetch_menu, format_pretty_menu_msg
from config import ACCESS_TOKEN, ROOM_IDS
import sys


class GitterClient(object):
    def __init__(self, token, room_id):
        self.token = token
        self.room_id = room_id

    def send_msg(self, text):
        url = 'https://api.gitter.im/v1/rooms/{room_id}/chatMessages'.format(
            room_id=self.room_id)
        headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
            'authorization': 'Bearer {token}'.format(token=self.token),
        }
        data = json.dumps({'text': text})
        r = requests.post(url, data=data, headers=headers)
        assert r.status_code == 200


def menu():
    room = sys.argv[2]
    day = sys.argv[3]
    out = sys.argv[4]
    assert room in ROOM_IDS.keys()
    assert day in ['today', 'tomorrow']
    assert out in ['gitter', 'console']

    menu = fetch_menu(day)
    msg = format_pretty_menu_msg(menu)
    if out == 'gitter':
        token = ACCESS_TOKEN
        room_id = ROOM_IDS[room]
        c = GitterClient(token, room_id)
        c.send_msg(msg)
    elif out == 'console':
        print(msg)


def say():
    room = sys.argv[2]
    assert room in ROOM_IDS.keys()
    msg = sys.argv[3]
    token = ACCESS_TOKEN
    room_id = ROOM_IDS[room]
    c = GitterClient(token, room_id)
    c.send_msg(msg)

if __name__ == '__main__':
    opt = sys.argv[1]
    if opt == 'menu':
        menu()
    elif opt == 'say':
        say()
