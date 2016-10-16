import requests
import json
from r2menu import menu_for_the_day
from config import ACCESS_TOKEN, TEST_ROOM_ID
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


def msg_main():
    day = int(sys.argv[1])
    msg = menu_for_the_day(day)  # day_of_week=None)

    token = ACCESS_TOKEN
    room_id = TEST_ROOM_ID
    c = GitterClient(token, room_id)
    c.send_msg(msg)

if __name__ == '__main__':
    msg_main()
