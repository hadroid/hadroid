"""Coffee module."""

import json
import os
default_db_name = 'coffeedb.json'


class CoffeeBook(object):
    def __init__(self, db_name=None):
        self.fn = db_name or default_db_name
        if self.exists():
            self.load()
        else:
            self.create()

    def create(self):
        self.db = {
            'users': {},  # user_id -> 'fromUser' info
            'balance': {},  # user_id -> number of coffees
            'ops': [],  # list of operations
        }

    def save(self):
        with open(self.fn, 'w') as fp:
            json.dump(self.db, fp, indent=2)

    def load(self):
        with open(self.fn, 'r') as fp:
            self.db = json.load(fp)

    def exists(self):
        return os.path.isfile(self.fn)

    def get_balance(self, uid):
        return self.db['balance'][uid]

    def update_drinker(self, user):
        uid = user['id']
        if uid not in self.db['users']:
            self.db['users'][uid] = user
        if uid not in self.db['balance']:
            self.db['balance'][uid] = 0
        self.save()

    def update_balance(self, uid, value, time):
        self.db['balance'][uid] += value
        self.db['ops'].append((uid, value, time))
        self.save()

    def handle_msg(self, client, args, msg):
        self.client = client
        self.msg = msg
        user = msg['fromUser']
        uid = user['id']

        if args['buy'] or args['pay']:
            n = int(args['<n>']) if args['<n>'] else 1
            v = n if args['buy'] else -n
            self.db['balance'][uid] += v
            self.db['ops'].append((uid, v, self.msg['sent']))
        elif args['balance']:
            return self.db['balance'][uid]
        self.save()


def make_coffee(client, args, msg):
    book = CoffeeBook('coffeedb_{0}.json'.format(client.room_id))

    user = msg['fromUser']
    book.update_drinker(user)
    uid = user['id']

    if args['buy'] or args['pay']:
        n = int(args['<n>']) if args['<n>'] else 1
        v = n if args['buy'] else -n
        book.update_balance(uid, v, msg['sent'])
        client.send("@{un} OK".format(un=user['username']))
    elif args['balance']:
        blnc = book.get_balance(uid)
        client.send("@{un}'s coffee balance: {b}".format(
            un=user['username'], b=blnc))
    elif args['stats']:
        client.send("Coffee stats feature is coming soon...")
