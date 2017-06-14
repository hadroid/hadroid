"""Example Hadroid configuration."""

from hadroid.modules.base import echo, ping, selfdestruct
from hadroid.modules.coffee import COFFEE_USAGE, coffee
from hadroid.modules.cron import CRON_USAGE, cron
from hadroid.modules.menu import MENU_USAGE, menu
from hadroid.client import StreamClient, CronClient
from hadroid import Module
from hadroid import build_usage_str

GITTER_PERSONAL_ACCESS_TOKEN = 'YOUR_GITTER_PERSONAL_ACCESS_TOKEN'

SOCKET_PATH = '/tmp/hadroid_socket'
SOCKET_BUFSIZE = 16 * 1024

MODULES = (
    Module(('--help', ), None, None),
    Module(('coffee', 'c'), coffee, COFFEE_USAGE),
    Module(('menu', 'm'), menu, MENU_USAGE),
    Module(('cron', ), cron, CRON_USAGE),
    Module(('echo', ), echo, 'echo <msg>...'),
    Module(('ping', ), ping, None),
    Module(('selfdestruct', ), selfdestruct, None),
)

CLIENTS = {
    'stream': StreamClient,
    'cron': CronClient,
}

DEBUG = False

BOT_NAME = 'Hadroid'

# Set the default Gitter room for the bot to join
ROOM = ''

# Respond to !<command> or @Hadroid <command>
CMD_PREFIX = ('!', '@' + BOT_NAME)

# Gitter username of the bot admins
ADMINS = ('krzysztof', )

# Bot docstring configuration
DOC_HEADER = """
Hadroid Help Manual.

Parameter <day> can be either 'today', 'tomorrow' or 'monday'-'friday'.
For coffee module <n> stands for number of coffees drank or paid for.
If <n> is not specified, it stands for buying or paying for one coffee.
Instead direct message you can also preceed the commands with a bang '!',
for example instead of '@{botname} menu' you can just type '!menu'.
"""[:-1].format(botname=BOT_NAME)

DOC_USAGE = build_usage_str(MODULES, BOT_NAME)

DOC_EXAMPLES = """
    @{botname} menu tomorrow
    @{botname} echo Hello Y'@/all!

    Treat yourself a coffee:
    @{botname} coffee

    Treat yourself and your best buddy a coffee:
    @{botname} coffee drink 2

    Pay your coffee debts:
    @{botname} coffee pay 2
"""[1:-1].format(botname=BOT_NAME)

DOC_OPTIONS = """
    <n>           Number of coffees [default: 1].
    -h --help     Show this help.
    --version     Show version.
    --yall        Use the southern charm.
"""[1:-1]


DOC = """
{header}

Usage:
{usage}

Examples:
{examples}

Options:
{options}
""".format(header=DOC_HEADER, usage=DOC_USAGE, examples=DOC_EXAMPLES,
           options=DOC_OPTIONS)
