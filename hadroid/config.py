"""Default Hadroid configuration."""

from collections import namedtuple

from hadroid.modules.coffee import coffee, COFFEE_USAGE
from hadroid.modules.menu import menu, MENU_USAGE
from hadroid.modules.base import echo, ping, selfdestruct
from hadroid.modules.cron import cron, CRON_USAGE

Module = namedtuple('Module', ['names', 'main', 'usage'])

#
# Default Configuration
#
MODULES = (
    Module(('coffee', 'c'), coffee, COFFEE_USAGE),
    Module(('menu', 'm'), menu, MENU_USAGE),
    Module(('cron', ), cron, CRON_USAGE),
    Module(('echo', ), echo, 'echo <msg>...'),
    Module(('ping', ), ping, None),
    Module(('selfdestruct', ), selfdestruct, None),
)

GITTER_PERSONAL_ACCESS_TOKEN = 'YOUR_GITTER_PERSONAL_ACCESS_TOKEN'

ROOMS = {
    'myroom': 'GITTER_ROOM_ID'
}

BOT_NAME = 'Hadroid'

# Respond to !<command> or @Hadroid <command>
CMD_PREFIX = ('!', '@' + BOT_NAME)

# Gitter username of the bot admins
ADMINS = ('krzysztof', )

# Bot docstring configuration
DOC_HEADER = """
Parameter <day> can be either 'today', 'tomorrow' or 'moday'-'friday'.
For coffee module <n> stands for number of coffees drank or paid for.
If <n> is not specified, it stands for buying or paying for one coffee.
Instead direct message you can also preceed the commands with a bang '!',
for example instead of '@{botname} menu' you can just type '!menu'.
"""[:-1]

DOC_EXAMPLES = """
    @{botname} menu tomorrow
    @{botname} echo Hello Y'@/all!

    Treat yourself a coffee:
    @{botname} coffee

    Treat yourself and your best buddy a coffee:
    @{botname} coffee drink 2

    Pay your coffee debts:
    @{botname} coffee pay 2
"""[1:-1]

DOC_OPTIONS = """
    <n>           Number of coffees [default: 1].
    -h --help     Show this help.
    --version     Show version.
    --yall        Use the southern charm.
"""[1:-1]