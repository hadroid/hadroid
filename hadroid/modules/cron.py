"""Cron control module."""


CRON_USAGE = 'cron (add <time> <cmd> | remove <idx> | list)'


def cron(client, args, msg_json):
    from hadroid.cronbot import CronBook
    cb = CronBook()
    if args['add']:
        cb.add(args['<time>'], args['<cmd>'])
    elif args['list']:
        jobs = cb.list()
        msg = "\n".join("{0} ({1}): '{2}'".format(i, t, c) for i, t, c in jobs)
        client.send(msg, block=True)
    elif args['remove']:
        idx = int(args['<idx>'])
        cb.remove(idx)
