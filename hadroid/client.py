"""Base Client classes."""

from hadroid.modules.cron import CronBook
import pytz
import requests
import json
from time import sleep

import shlex
from collections import namedtuple
from datetime import datetime

import docopt
from hadroid import C, __version__
from hadroid.docopt2 import docopt_parse

CronEvent = namedtuple('CronEvent', ['dt', 'idx', 'time', 'cmd'])


def bot_main(client, args, msg_json=None):
    """Main bot function."""
    for m in C.MODULES:
        if any(args[name] for name in m.names):
            m.main(client, args, msg_json)


class Client(object):
    """Base communication client."""

    def send(self, msg, *args, **kwargs):
        """Send a message to a destination."""
        raise NotImplementedError


class StdoutClient(Client):
    """Simple client for printing to console."""

    def send(self, msg, *args, **kwargs):
        """Send a message to standard output."""
        print(msg)


class GitterClient(Client):
    """REST Gitter client."""

    def __init__(self, token, room_id=None):
        """Initialize Gitter client."""
        self.token = token
        self.room_id = room_id
        self.headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
            'authorization': 'Bearer {token}'.format(token=self.token),
        }

    def resolve_room_id(self, room):
        """Resolve room or username to a Gitter RoomID."""
        url = 'https://api.gitter.im/v1/rooms'
        resp = requests.get(url, headers=self.headers)
        for r in resp.json():
            if (not r['oneToOne'] and r['uri'] == room) or \
                    (r['oneToOne'] and r['user']['username'] == room):
                return r['id']

    def send(self, msg, room_id=None, block=False):
        """Send message to Gitter channel."""
        url = 'https://api.gitter.im/v1/rooms/{room_id}/chatMessages'.format(
            room_id=(room_id or self.room_id))
        msg_fmt = '```text\n{msg}\n```' if block else '{msg}'
        data = json.dumps({'text': msg_fmt.format(msg=msg)})
        requests.post(url, data=data, headers=self.headers)


class StreamClient(GitterClient):
    """Streaming Gitter client."""

    def listen(self, room_id=None):
        """Listen on the channel."""
        url = 'https://stream.gitter.im/v1/rooms/{room}/chatMessages'.format(
            room=self.room_id)
        r = requests.get(url, headers=self.headers, stream=True)
        for line in r.iter_lines():
            if line and len(line) > 1:
                try:
                    msg = line.decode('utf8')
                    print(msg)
                    self.parse_message(json.loads(msg))
                except Exception as e:
                    print(repr(e))

    def parse_message(self, msg_json):
        """Parse a chat message for bot-mentions."""
        text = msg_json['text']
        # ignore messages from the bot himself
        if msg_json['fromUser']['username'] == C.BOT_NAME:
            return
        try:  # respond only to some bot-prefixed messages
            prefix = next(p for p in C.CMD_PREFIX if text.startswith(p))
            text = text.lstrip(prefix).strip()
        except StopIteration:
            return
        self.respond(text, msg_json)

    def respond(self, cmd, msg_json):
        """Respond to a bot command."""
        try:
            # Create a 'fake' CLI execution of the actual bot program
            argv = shlex.split(cmd.replace('``', '"'))
            args = docopt_parse(C.DOC, argv=argv, version=__version__)
            bot_main(self, args, msg_json)

        except docopt.DocoptExit as e:
            self.send("```text\n{0}```".format(str(e)))


class CronClient(GitterClient):
    """Cron client."""

    def listen(self):
        """Wait for the next cron event and execute it."""
        events_backlog = []
        while True:
            # Get a fresh CronBook definition and current time
            cb = CronBook()
            now = datetime.now(pytz.utc)

            # Update events in the backlog
            events = cb.get_upcoming_events()
            for ev in events:
                if ev not in events_backlog:
                    events_backlog.append(ev)

            # Determine what is to be executed now and what stays
            exec_ev = [ev for ev in events_backlog if ev[1] < now]
            events_backlog = [ev for ev in events_backlog if ev[1] >= now]

            if C.DEBUG:
                print("To be executed:", exec_ev)
                print("Backlog:", events_backlog)

            # Execute events from backlog
            for ev in exec_ev:
                event = cb.get_by_id(ev[0])
                if event is not None:
                    self.respond(event['command'], {},
                                 room_id=event['roomId'])
            sleep(30)

    def respond(self, cmd, msg_json, room_id=None):
        """Respond to a bot command."""
        try:
            # Create a 'fake' CLI execution of the actual bot program
            argv = cmd.split()
            args = docopt_parse(C.DOC, argv=argv)
            client = GitterClient(self.token, room_id)
            bot_main(client, args, msg_json)

        except docopt.DocoptExit as e:
            self.send("```text\n{0}```".format(str(e)))
