"""Base modules."""

import sys
from time import sleep
from r2d2 import CHANGELOG, WHATSNEW
from r2d2.config import ADMINS


def ping(client, args, msg_json):
    client.send('Pong!')


def echo(client, args, msg_json):
    msg = " ".join(args['<msg>'])
    client.send(msg)


def changelog(client, args, msg_json):
    client.send(CHANGELOG, block=True)


def whatsnew(client, args, msg_json):
    client.send(WHATSNEW, block=True)


def selfdestruct(client, args, msg_json):
    if msg_json['fromUser']['username'] in ADMINS:
        client.send("Self destructing in 3...")
        sleep(1)
        client.send("2...")
        sleep(1)
        client.send("1..")
        sleep(1)
        client.send(":boom:")
        sys.exit(0)
    else:
        name = msg_json['fromUser']['displayName']
        name = name.split()[0] if name.split()[0] else name
        client.send(
            "I'm sorry {0}, I'm afraid I can't do that.".format(name))
