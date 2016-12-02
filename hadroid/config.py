"""Default Hadroid configuration."""

from collections import namedtuple

from hadroid.modules.coffee import coffee, COFFEE_USAGE
from hadroid.modules.menu import menu, MENU_USAGE
from hadroid.modules.base import echo, whatsnew, changelog, ping, selfdestruct
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
    Module(('whatsnew', ), whatsnew, None),
    Module(('changelog', ), changelog, None),
    Module(('selfdestruct', ), selfdestruct, None),
)

ACCESS_TOKEN = 'YOUR_GITTER_ACCESS_TOKEN'

ROOMS = {
    'myroom': 'GITTER_ROOM_ID'
}

BOT_NAME = 'Hadroid'

# Respond to !<command> or @Hadroid <command>
CMD_PREFIX = ('!', '@' + BOT_NAME)

# Gitter username of the bot admins
ADMINS = ('krzysztof', )
