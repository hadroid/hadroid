"""
Hadroid Controller.

This is the controller for the bot, that sets up all of the plumbing for
authenticating to Gitter, listening on channel stream or executing commands.

Argument <room> can be either a pre-defined room from config (see C.ROOMS)
or a Gitter room ID.

Controller has multiple modes of operation:
'gitter' executes a single bot command and broadcast it to the gitter channel
'stream' launches the boot in the "listening" mode on given Gitter channel.
'cron' launches the periodic task loop.

Usage:
    botctl stream <room> [--verbose]
    botctl cron <room> [--verbose]
    botctl gitter <room> <cmd>...
    botctl stdout <cmd>...

Examples:
    botctl stream test
    botctl cron test
    botctl gitter test "menu today"
    botctl gitter qa "echo Hello everyone!"

Options:
    -h --help   Show this help.
    --verbose   Show errors.
    --version   Show version.
"""


import requests
import json
import shlex
import docopt
from datetime import timedelta
from time import sleep
from collections import namedtuple

from hadroid.docopt2 import docopt_parse
from hadroid import __version__, C
from hadroid.client import Client, StdoutClient
from hadroid.bot import __doc__ as bot_doc, bot_main
from hadroid.modules.cron import CronBook


class GitterClient(Client):
    """REST Gitter client."""

    def __init__(self, token, room_id):
        """Initialize Gitter client."""
        self.token = token
        self.room_id = room_id

    def send(self, msg, block=False):
        """Send message to Gitter channel."""
        url = 'https://api.gitter.im/v1/rooms/{room_id}/chatMessages'.format(
            room_id=self.room_id)
        headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
            'authorization': 'Bearer {token}'.format(token=self.token),
        }
        msg_fmt = '```text\n{msg}\n```' if block else '{msg}'
        data = json.dumps({'text': msg_fmt.format(msg=msg)})
        requests.post(url, data=data, headers=headers)


class StreamClient(GitterClient):
    """Streaming Gitter client."""

    def listen(self):
        """Listen on the channel."""
        url = 'https://stream.gitter.im/v1/rooms/{room}/chatMessages'.format(
            room=self.room_id)
        headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
            'authorization': 'Bearer {token}'.format(token=self.token),
        }
        r = requests.get(url, headers=headers, stream=True)
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
        while True:
            cb = CronBook()
            next_event = cb.get_next()
            if next_event is not None and \
                    next_event[0] < timedelta(seconds=30):
                ce = CronEvent(*next_event)
                sleep(ce.dt.seconds)
                self.respond(ce.cmd, {})
            else:
                sleep(20)

    def respond(self, cmd, msg_json):
        """Respond to a bot command."""
        try:
            # Create a 'fake' CLI execution of the actual bot program
            argv = cmd.split()
            args = docopt_parse(bot_doc, argv=argv)
            bot_main(self, args, msg_json)

        except docopt.DocoptExit as e:
            self.send("```text\n{0}```".format(str(e)))


if __name__ == '__main__':
    args = docopt.docopt(__doc__, version=__version__)

    room_id = C.ROOMS[args['<room>']] if args['<room>'] in C.ROOMS \
        else args['<room>']

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
    elif args['stdout']:
        bot_args = docopt_parse(bot_doc, args['<cmd>'], version=__version__)
        bot_main(StdoutClient(), bot_args)
