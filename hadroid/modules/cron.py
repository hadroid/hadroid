"""Cron control module."""

import json
import os
import uuid
from datetime import datetime

import pytz
from crontab import CronTab

CRON_USAGE = 'cron ((add | a) <time> <cmd> | (remove | rm) <idx> |' \
    ' (list | ls) | (timezone [<tzname>]))'


class CronBook(object):
    """This is the JSON-based database implementation of the cron events.

    Each event is defined as a dictionary containting:

        eventId - unique UUID for each event definition
        time - CRON-like time signature of the event
        command - Bot command to execute
        roomId - Gitter channel on which the event is to be executed
        timezone - timezone according to which the event is to be executed
    """
    def __init__(self, cronbook_name='cronbook.json'):
        self.fn = cronbook_name
        if self.exists():
            self.load()
        else:
            self.create()

    def create(self):
        self.db = {
            'events': [],
            'defaultTimezone': 'Europe/Zurich',
        }

    def save(self):
        with open(self.fn, 'w') as fp:
            json.dump(self.db, fp, indent=2)

    def load(self):
        with open(self.fn, 'r') as fp:
            self.db = json.load(fp)

    def set_timezone(self, tz):
        self.db['defaultTimezone'] = tz
        self.save()

    def get_timezone(self):
        return self.db['defaultTimezone']

    def exists(self):
        return os.path.isfile(self.fn)

    def add(self, time, command, room_id):
        event = {
            'eventId': str(uuid.uuid4()),
            'time': time,
            'command': command,
            'roomId': room_id,
            'timezone': self.get_timezone()
        }
        self.db['events'].append(event)
        self.save()

    def list(self, room_id=None):
        events = list(self.db['events'])
        if room_id is not None:
            events = [ev for ev in events if ev['roomId'] == room_id]
        return [(i, event['time'], event['command']) for i, event in
                enumerate(events)]

    def _remove_by_id(self, ev_id):
        self.db['events'] = [ev for ev in self.db['events']
                             if ev['eventId'] != ev_id]
        self.save()

    def get_by_id(self, ev_id):
        return next((ev for ev in self.db['events'] if ev['eventId'] == ev_id),
                    None)

    def remove(self, idx, room_id=None):
        events = list(self.db['events'])
        if room_id is not None:
            events = [ev for ev in events if ev['roomId'] == room_id]
        del_ev = events[idx]
        self._remove_by_id(del_ev['eventId'])

    @staticmethod
    def get_event_dt_utc(event):
            ev_tz = pytz.timezone(event['timezone'])
            ev_now = datetime.now(ev_tz)  # Local 'now' time of event
            ts_next = CronTab(event['time']).next(ev_now, delta=False)
            dt_next = ev_tz.localize(datetime.fromtimestamp(ts_next))
            return dt_next.astimezone(pytz.utc)

    def get_upcoming_events(self):
        events = []
        for ev in self.db['events']:
            ev_dt = self.get_event_dt_utc(ev)
            events.append((ev['eventId'], ev_dt))
        return events


def cron(client, args, msg_json):
    cb = CronBook()
    if args['add'] or args['a']:
        cb.add(args['<time>'], args['<cmd>'], room_id=client.room_id)
    elif args['list'] or args['ls']:
        jobs = cb.list(client.room_id)
        if jobs:
            msg = "\n".join("{0} ({1}): '{2}'".format(i, t, c)
                            for i, t, c in jobs)
            client.send(msg, block=True)
        else:
            msg = "No cron jobs available."
            client.send(msg)
    elif args['remove'] or args['rm']:
        idx = int(args['<idx>'])
        cb.remove(idx, room_id=client.room_id)
    elif args['timezone']:
        if args['<tzname>']:
            cb.set_timezone(args['<tzname>'])
        msg = "Current CRON TimeZone: {0}".format(cb.get_timezone())
        client.send(msg)
