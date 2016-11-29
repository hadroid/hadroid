"""Bot configuration."""
from collections import namedtuple
from hadroid.modules.coffee import coffee, COFFEE_USAGE
from hadroid.modules.menu import menu, MENU_USAGE
from hadroid.modules.base import echo, whatsnew, changelog, ping, selfdestruct
from hadroid.modules.cron import cron, CRON_USAGE
Module = namedtuple('Module', ['names', 'main', 'usage'])
# Register modules
MODULES = (
    Module(('coffee', 'c'), coffee, COFFEE_USAGE),
    Module(('menu', 'm'), menu, MENU_USAGE),
    Module(('cron', ), cron, CRON_USAGE),
    Module(('echo', ), echo, 'echo <msg>'),
    Module(('ping', ), ping, None),
    Module(('whatsnew', ), whatsnew, None),
    Module(('changelog', ), changelog, None),
    Module(('selfdestruct', ), selfdestruct, None),
)

with open('ACCESS_TOKEN', 'r') as fp:
    ACCESS_TOKEN = fp.read().strip()
MAIN_ROOM_ID = '54ca0dd2db8155e6700f36e1'  # AfricanPenguin (Production)
QA_ROOM_ID = '5813d38ed73408ce4f31907b'  # R2-D2 Repair Station (QA)
TEST_ROOM_ID = '5813d47bd73408ce4f3190a4'  # R2-D2 Repair Station (Testing)

BOT_NAME = 'Hadroid'  # Change
# Respond to !<command> or @Hadroid <command>
CMD_PREFIX = ('!', '@' + BOT_NAME)

ADMINS = ('krzysztof', )
