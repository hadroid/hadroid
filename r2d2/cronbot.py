"""
Timed-events controller for the R2-D2 bot.

The 'run' command will simply refresh the events list in the loop
 and execute them when the time comes.

Usage:
    cronbot run (qa | test | prod)
    cronbot add <time> <cmd>
    cronbot remove <idx>
    cronbot list
    cronbot next
"""


import json
import docopt
from datetime import datetime, timedelta
from time import sleep
from collections import namedtuple
from crontab import CronTab
import os

from r2d2.client import StdoutClient
from r2d2.gitterbot import GitterClient, extras_patch
from r2d2.bot import __doc__ as bot_doc, bot_main
from r2d2.config import ACCESS_TOKEN, QA_ROOM_ID, TEST_ROOM_ID, MAIN_ROOM_ID

CronEvent = namedtuple('CronEvent', ['dt', 'idx', 'time', 'cmd'])


# Apply the docopt patch
docopt.extras = extras_patch


class CronClient(GitterClient):
    """Cron client."""

    def listen(self):
        while True:
            cb = CronBook()
            next_event = cb.get_next()
            if next_event is not None and \
                    next_event[0] < timedelta(seconds=60):
                ce = CronEvent(*next_event)
                sleep(ce.dt.seconds)
                self.respond(ce.cmd, {})
            else:
                sleep(60)

    def respond(self, cmd, msg_json):
        """Respond to a bot command."""
        try:
            # Create a 'fake' CLI execution of the actual bot program
            argv = cmd.split()
            args = docopt.docopt(bot_doc, argv=argv)
            bot_main(self, args, msg_json)

        except docopt.DocoptExit as e:
            self.send("```text\n{0}```".format(str(e)))


class CronBook(object):
    def __init__(self, cronbook_name='cronbook.json'):
        self.fn = cronbook_name
        if self.exists():
            self.load()
        else:
            self.create()

    def create(self):
        self.db = []

    def save(self):
        with open(self.fn, 'w') as fp:
            json.dump(self.db, fp, indent=2)

    def load(self):
        with open(self.fn, 'r') as fp:
            self.db = json.load(fp)

    def exists(self):
        return os.path.isfile(self.fn)

    def add(self, time, cmd):
        self.db.append((time, cmd))
        self.save()

    def list(self):
        return [(i, time, cmd) for i, (time, cmd) in enumerate(self.db)]

    def remove(self, idx):
        del self.db[idx]
        self.save()

    def get_next(self):
        events = []
        t0 = datetime.now()
        for idx, time, cmd in self.list():
            t_wait = timedelta(seconds=CronTab(time).next(t0))
            events.append((t_wait, idx, time, cmd))
        events = sorted(events, key=lambda x: x[0])
        return list(events)[0]


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    if args['qa']:
        room_id = QA_ROOM_ID
    elif args['test']:
        room_id = TEST_ROOM_ID
    elif args['prod']:
        room_id = MAIN_ROOM_ID
    cb = CronBook()

    if args['run']:
        client = CronClient(ACCESS_TOKEN, room_id)
        client.listen()
    elif args['add']:
        cb.add(args['<time>'], args['<cmd>'])
    elif args['list']:
        jobs = cb.list()
        msg = "\n".join("{0} ({1}): '{2}'".format(i, t, c) for i, t, c in jobs)
        StdoutClient().send(msg, block=True)
    elif args['remove']:
        idx = int(args['<idx>'])
        cb.remove(idx)
    elif args['next']:
        cb.next()
