"""
Hadroid Controller.

This is the controller for the bot, that sets up all of the plumbing for
authenticating to Gitter, listening on channel stream or executing commands.

Option --room=<room> can be either an organization or repo name room name,
e.g.: 'myorg', 'myorg/myrepo', or a Gitter username for a One-To-One
conversation. If skipped the 'ROOM' config variable is used.

Controller has multiple modes of operation:
'gitter' executes a single bot command and broadcast it to the gitter channel
'stream' launches the boot in the "listening" mode on given Gitter channel.
'cron' launches the periodic task loop.

Usage:
    botctl stream [--room=<room>] [--verbose]
    botctl cron [--room=<room>] [--verbose]
    botctl gitter <cmd>... [--room=<room>]
    botctl stdout <cmd>...

Examples:
    botctl stream test
    botctl cron test
    botctl gitter test "menu today"
    botctl gitter qa "echo Hello everyone!"

Options:
    -h --help       Show this help.
    --room=<room>   Room where the bot will run.
    --verbose       Show errors.
    --version       Show version.
"""


import json
import shlex
from collections import namedtuple
from datetime import datetime
from time import sleep

import docopt
import pytz
import requests

from hadroid import C, __version__
from hadroid.bot import __doc__ as bot_doc
from hadroid.bot import bot_main
from hadroid.client import Client, StdoutClient
from hadroid.docopt2 import docopt_parse
from hadroid.modules.cron import CronBook


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
            args = docopt_parse(bot_doc, argv=argv, version=__version__)
            bot_main(self, args, msg_json)

        except docopt.DocoptExit as e:
            self.send("```text\n{0}```".format(str(e)))


CronEvent = namedtuple('CronEvent', ['dt', 'idx', 'time', 'cmd'])


class CronClient(GitterClient):
    """Cron client."""

    def listen(self):
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
                print(exec_ev)
                print(events_backlog)

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
            args = docopt_parse(bot_doc, argv=argv)
            client = GitterClient(self.token, room_id)
            bot_main(client, args, msg_json)

        except docopt.DocoptExit as e:
            self.send("```text\n{0}```".format(str(e)))


def main():
    """Main function."""
    args = docopt.docopt(__doc__, version=__version__)

    if args['stdout']:
        bot_args = docopt_parse(bot_doc, args['<cmd>'], version=__version__)
        bot_main(StdoutClient(), bot_args)

    room_id = GitterClient(C.GITTER_PERSONAL_ACCESS_TOKEN).resolve_room_id(
        args.get('--room', C.ROOM))

    if args['stream']:
        client = StreamClient(C.GITTER_PERSONAL_ACCESS_TOKEN, room_id)
        client.listen()
    if args['cron']:
        client = CronClient(C.GITTER_PERSONAL_ACCESS_TOKEN, room_id)
        client.listen()
    elif args['gitter']:
        client = GitterClient(C.GITTER_PERSONAL_ACCESS_TOKEN, room_id)
        bot_args = docopt_parse(bot_doc, args['<cmd>'], version=__version__)
        bot_main(client, bot_args)


if __name__ == '__main__':
    main()
