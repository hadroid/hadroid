"""Bot configuration."""

MAIN_ROOM_ID = '54ca0dd2db8155e6700f36e1'  # AfricanPenguin (Production)
QA_ROOM_ID = '5813d38ed73408ce4f31907b'  # R2-D2 Repair Station (QA)
TEST_ROOM_ID = '5813d47bd73408ce4f3190a4'  # R2-D2 Repair Station (Testing)
BOT_NAME = 'CERN-R2-D2'

with open('ACCESS_TOKEN', 'r') as fp:
    ACCESS_TOKEN = fp.read().strip()

# !<command> or @CERN-R2-D2 <command>
CMD_PREFIX = ('!', '@' + BOT_NAME)

ADMINS = ('krzysztof', )
