"""
Restaurant 2 Diner Droid.

Fetches the menu from Restaurant 2 and broadcasts it to Gitter.
Can print to standard output (stdout), a "QA" Gitter room (qa) or
"production" Gitter room (prod).
<day> can be either "today" or "tomorrow"
To use Gitter a file named "ACCESS_TOKEN" needs to be placed in this directory
containing a single line with the Gitter access token.

Usage:
    r2d2 menu <day> (stdout|qa|prod)
    r2d2 say <msg> (stdout|qa|prod)

Options:
    -h --help   Show this help.
    --version   Show version.
"""


import requests
import json
from menu import fetch_menu, format_pretty_menu_msg
from config import ACCESS_TOKEN, TEST_ROOM_ID, MAIN_ROOM_ID
from docopt import docopt


class Client(object):
    def send_msg(self, text):
        """Sends a message to a destination."""
        raise NotImplementedError


class GitterClient(Client):
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


class StdoutClient(Client):
    """Simple client for printint to console (testing)."""
    def send_msg(self, text):
        print(text)


if __name__ == '__main__':
    args = docopt(__doc__, version='0.0.1')

    # To which Gitter room (or stdout) to broadcast
    if args['stdout']:
        client = StdoutClient()
    else:
        if args['qa']:
            room_id = TEST_ROOM_ID
        elif args['prod']:
            room_id = MAIN_ROOM_ID
        client = GitterClient(ACCESS_TOKEN, room_id)

    # Main functions
    if args['menu']:
        day = args['<day>']
        assert day in ['today', 'tomorrow']
        menu = fetch_menu(day)
        msg = format_pretty_menu_msg(menu)
        client.send_msg(msg)
    elif args['say']:
        msg = args['<msg>']
        client.send_msg(msg)
