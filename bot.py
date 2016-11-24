"""
Restaurant 2 Diner Droid.

Parameter <day> can be either 'today', 'tomorrow' or 'moday'-'friday'.
For coffee module <n> stands for number of coffees drank or paid for.
If <n> is not specified, it stands for buying or paying for one coffee.
Instead direct message you can also preceed the commands with a bang '!',
for example instead of '@{botname} menu' you can just type '!menu'.

Usage:
{usage}

Examples:
    @{botname} menu tomorrow
    @{botname} echo Hello Y'@/all!

    Treat yourself a coffee:
    @{botname} coffee

    Treat yourself and your best buddy a coffee:
    @{botname} coffee drink 2

    Pay your debts
    @{botname} coffee pay 2

Options:
    <n>           Number of coffees [default: 1].
    -h --help     Show this help.
    --version     Show version.
    --yall        Use the southern charm.
"""


from __init__ import __version__
from docopt import docopt
from config import BOT_NAME, MODULES
from client import StdoutClient

# Patch the docstring
usage_str = "\n".join(("    @{0} {1}".format(BOT_NAME,
                                             m.usage or m.names[0])
                       for m in MODULES))
__doc__ = __doc__.format(botname=BOT_NAME, usage=usage_str)


def bot_main(client, args, msg_json=None):
    """Main bot function."""
    for m in MODULES:
        if any(args[name] for name in m.names):
            m.main(client, args, msg_json)


if __name__ == "__main__":
    """When called directly, use a console client."""
    args = docopt(__doc__, version=__version__)
    bot_main(StdoutClient(), args)
