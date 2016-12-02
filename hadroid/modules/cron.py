"""Cron control module."""

import json
import pytz
from datetime import datetime, timedelta
from crontab import CronTab
import os

CRON_USAGE = 'cron ((add | a) <time> <cmd> | (remove | rm) <idx> |' \
    ' (list | ls) | (timezone [<tzname>]) | next)'


class CronBook(object):
    def __init__(self, cronbook_name='cronbook.json'):
        self.fn = cronbook_name
        if self.exists():
            self.load()
        else:
            self.create()

    def create(self):
        self.db = {
            'jobs': [],
            'tz': 'Europe/Zurich',
        }

    def save(self):
        with open(self.fn, 'w') as fp:
            json.dump(self.db, fp, indent=2)

    def load(self):
        with open(self.fn, 'r') as fp:
            self.db = json.load(fp)

    def set_timezone(self, tz):
        self.db['tz'] = tz
        self.save()

    def get_timezone(self):
        return self.db['tz']

    def exists(self):
        return os.path.isfile(self.fn)

    def add(self, time, cmd):
        self.db['jobs'].append((time, cmd))
        self.save()

    def list(self):
        return [(i, time, cmd) for i, (time, cmd) in
                enumerate(self.db['jobs'])]

    def remove(self, idx):
        del self.db['jobs'][idx]
        self.save()

    def get_next(self):
        events = []
        t0 = datetime.now(pytz.timezone(self.db['tz']))
        for idx, time, cmd in self.list():
            t_wait = timedelta(seconds=CronTab(time).next(t0))
            events.append((t_wait, idx, time, cmd))
        events = list(sorted(events, key=lambda x: x[0]))
        return events[0] if events else None


def cron(client, args, msg_json):
    cb = CronBook()
    if args['add'] or args['a']:
        cb.add(args['<time>'], args['<cmd>'])
    elif args['list'] or args['ls']:
        jobs = cb.list()
        if jobs:
            msg = "\n".join("{0} ({1}): '{2}'".format(i, t, c)
                            for i, t, c in jobs)
            client.send(msg, block=True)
        else:
            msg = "No cron jobs available."
            client.send(msg)
    elif args['remove'] or args['rm']:
        idx = int(args['<idx>'])
        cb.remove(idx)
    elif args['timezone']:
        if args['<tzname>']:
            cb.set_timezone(args['<tzname>'])
        msg = "Current CRON TimeZone: {0}".format(cb.get_timezone())
        client.send(msg)
    elif args['next']:
        n = cb.get_next()
        client.send(str(n), block=True)
