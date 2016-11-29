"""
Restaurant 2 Diner Droid Controller.

This is the controller for the R2-D2 bot, that sets up all of the plumbing for
authenticating to Gitter, listening on channel stream or executing commands.

The 'stream' command will just hook the boot on the "listening" mode on given
channel. The 'exec' command will execute a single bot command and broadcast
it on the Gitter channel (for actual commands see 'bot.py').

Usage:
    gitterbot stream (test|qa|prod)
    gitterbot exec (test|qa|prod) <cmd>

Examples:
    gitterbot stream qa
    gitterbot exec test "menu today"
    gitterbot exec qa "echo Hello everyone!"

Options:
    -h --help   Show this help.
    --version   Show version.
"""


import requests
import json
import docopt

from r2d2.client import Client
from r2d2.bot import __doc__ as bot_doc, bot_main
from r2d2 import __version__
from r2d2.config import ACCESS_TOKEN, QA_ROOM_ID, TEST_ROOM_ID, MAIN_ROOM_ID, \
    CMD_PREFIX, BOT_NAME


# We need to patch docopt's 'extras' function as it was hard sys-exiting
# the bot after '--help/-h' or '--version' commands
def extras_patch(help, version, options, doc):
    """Patch of docopt.extra handler."""
    exc = None
    if help and any((o.name in ('-h', '--help')) and o.value for o in options):
        exc = docopt.DocoptExit()
        exc.args = (doc.strip("\n"), )
    if version and any(o.name == '--version' and o.value for o in options):
        exc = docopt.DocoptExit()
        exc.args = (version, )
    if exc is not None:
        raise exc


# Apply the patch above to docopt.extras
docopt.extras = extras_patch


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
        msg_fmt = '```text{msg}```' if block else '{msg}'
        data = json.dumps({'text': msg_fmt.format(msg=msg)})
        r = requests.post(url, data=data, headers=headers)
        assert r.status_code == 200


class GitterStream(GitterClient):
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
                    self.parse_message(json.loads(line.decode('utf8')))
                except Exception as e:
                    print(repr(e))

    def respond(self, cmd, msg_json):
        """Respond to a bot command."""
        try:
            # Create a 'fake' CLI execution of the actual bot program
            argv = cmd.split()
            args = docopt.docopt(bot_doc, argv=argv, version=__version__)
            bot_main(self, args, msg_json)

        except docopt.DocoptExit as e:
            self.send("```text\n{0}```".format(str(e)))

    def parse_message(self, msg_json):
        """Parse a chat message for bot-mentions."""
        text = msg_json['text']
        # ignore messages from the bot himself
        if msg_json['fromUser']['username'] == BOT_NAME:
            return
        try:  # respond only to some bot-prefixed messages
            prefix = next(p for p in CMD_PREFIX if text.startswith(p))
            text = text.lstrip(prefix).strip()
        except StopIteration:
            return
        self.respond(text, msg_json)


if __name__ == '__main__':
    args = docopt.docopt(__doc__, version=__version__)
    if args['qa']:
        room_id = QA_ROOM_ID
    elif args['test']:
        room_id = TEST_ROOM_ID
    elif args['prod']:
        room_id = MAIN_ROOM_ID

    if args['stream']:
        client = GitterStream(ACCESS_TOKEN, room_id)
        client.listen()
    elif args['exec']:
        client = GitterClient(ACCESS_TOKEN, room_id)
        bot_argv = args['<cmd>'].split()  # split except quotes
        bot_args = docopt.docopt(bot_doc, argv=bot_argv,
                                 version=__version__)
        bot_main(client, bot_args)
