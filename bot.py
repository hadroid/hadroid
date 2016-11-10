"""
Restaurant 2 Diner Droid.

Parameter <day> can be either "today", "tomorrow" or "moday"-"friday".
For coffee module <n> stands for number of coffees drank or paid for.
If <n> is not specified, it stands for buying or paying for one coffee.
Instead direct message you can also preceed the commands with a bang '!',
for example '@CERN-R2-D2 menu' is equivalent to '!menu'.

Usage:
    @CERN-R2-D2 ping
    @CERN-R2-D2 (changelog | whatsnew)
    @CERN-R2-D2 (coffee | c) [(drink [<n>] | pay [<n>] | balance | stats)]
    @CERN-R2-D2 (menu | m) [<day>] [--yall]
    @CERN-R2-D2 echo <msg>...
    @CERN-R2-D2 selfdestruct

Examples:
    @CERN-R2-D2 menu tomorrow
    @CERN-R2-D2 echo Hello Y'@/all!

    Treat yourself a coffee:
    @CERN-R2-D2 coffee

    Treat yourself and your best buddy a coffee:
    @CERN-R2-D2 coffee drink 2

    Pay your debts
    @CERN-R2-D2 coffee pay 2

Options:
    <n>           Number of coffees [default: 1].
    -h --help     Show this help.
    --version     Show version.
    --yall        Use the southern charm.
"""

from __init__ import __version__, CHANGELOG, WHATSNEW
from docopt import docopt
from config import ADMINS
import sys
from time import sleep

from modules.coffee import make_coffee
from modules.menu import fetch_menu, format_pretty_menu_msg


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
    elif args['menu'] or args['m']:
        day = (args['<day>'] or 'today').lower()
        days = ['today', 'tomorrow', 'monday', 'tuesday', 'wednesday',
                'thursday', 'friday']
        if day not in days:
            msg = "Please specify a correct day ('today', 'tomorrow'" \
                  " or 'monday' to 'friday')."
        else:
            msg = ""
            if args['--yall']:
                msg += ":fork_and_knife: Hey Y'@/all, it's lunch time! :clock12:\n"
            menu = fetch_menu(day)
            msg += format_pretty_menu_msg(menu, day=day)
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
    elif args['coffee'] or args['c']:
        make_coffee(client, args, msg_json)
    elif args['changelog']:
        client.send("```text{}```".format(CHANGELOG))
    elif args['whatsnew']:
        client.send("```text{}```".format(WHATSNEW))

if __name__ == "__main__":
    args = docopt(__doc__, version=__version__)
    bot_main(StdoutClient(), args)
