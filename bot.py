"""
Restaurant 2 Diner Droid.

Parameter <day> can be either "today" or "tomorrow".
For coffee module <n> stands for number of coffees bought or paid back for.
If <n> is not specified, it stands for buying ONE coffee or paying back ALL
of the coffee debt.

Usage:
    @CERN-R2-D2 ping
    @CERN-R2-D2 coffee (buy [<n>] | pay [<n>] | balance | stats)
    @CERN-R2-D2 menu <day>
    @CERN-R2-D2 echo <msg>...
    @CERN-R2-D2 selfdestruct

Examples:
    @CERN-R2-D2 menu tomorrow
    @CERN-R2-D2 echo Hello @/all!

    Treat yourself a coffee:
    @CERN-R2-D2 coffee buy

    Treat yourself and your best buddy a coffee:
    @CERN-R2-D2 coffee buy 2

    Pay some of your debts
    @CERN-R2-D2 coffee pay 2

    Pay all of your debts
    @CERN-R2-D2 coffee pay all

Options:
    <n>           Number of coffees [default: 1].
    -h --help     Show this help.
    --version     Show version.
"""

from __init__ import __version__
from docopt import docopt
from menu import fetch_menu, format_pretty_menu_msg
from coffee import make_coffee
from config import ADMINS
import sys
from time import sleep


class Client(object):
    """Base communication client."""

    def send(self, msg):
        """Send a message to a destination."""
        raise NotImplementedError


class StdoutClient(Client):
    """Simple client for printing to console."""

    def send(self, msg):
        """Send a message to standard output."""
        print(msg)


def bot_main(client, args, msg_json=None):
    """Main bot function."""
    if args['ping']:
        client.send('Pong!')
    elif args['menu']:
        day = args['<day>']
        if day not in ['today', 'tomorrow']:
            msg = "Please specify a correct day (today or tomorrow)."
        else:
            menu = fetch_menu(day)
            msg = format_pretty_menu_msg(menu)
        client.send(msg)
    elif args['echo']:
        msg = " ".join(args['<msg>'])
        client.send(msg)
    elif args['selfdestruct']:
        if msg_json['fromUser']['username'] in ADMINS:
            client.send("Self destructing in 3...")
            sleep(1)
            client.send("2..")
            sleep(1)
            client.send("1..")
            sleep(1)
            client.send(":boom:")
            sys.exit(0)
        else:
            name = msg_json['fromUser']['displayName']
            name = name.split()[0] if name.split()[0] else name
            client.send(
                "I'm sorry {0}, I'm afraid I can't do that.".format(name))
    elif args['coffee']:
        make_coffee(client, args, msg_json)

if __name__ == "__main__":
    args = docopt(__doc__, version=__version__)
    bot_main(StdoutClient(), args)
