"""Base modules."""

import sys
from time import sleep

from hadroid import C


def ping(client, args, msg_json):
    client.send('Pong!')


def echo(client, args, msg_json):
    msg = " ".join(args['<msg>'])
    client.send(msg)


def selfdestruct(client, args, msg_json):
    if msg_json['fromUser']['username'] in C.ADMINS:
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
