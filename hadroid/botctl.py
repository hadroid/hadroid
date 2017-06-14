"""
Run and manage Hadroid clients.

First, run the main server:
  botctl run

next, in a separate shell, add some clients:
  botctl start stream zenodo
  botctl start stream krzysztof
  botctl start stream slint
  botctl start cron zenodo

then list the clients and their IDs:
  botctl list

and finally kill some clients:
  botctl stop 1

Usage:
    botctl run
    botctl shutdown
    botctl start <client-name> <room>
    botctl stop <client-id>
    botctl list

Examples:
    botctl run
    botctl start stream krzysztof
    botctl start stream zenodo
    botctl start cron zenodo
    botctl start stream zenodo/zenodo

Options:
    <client-name>   Can be either "stream" for GitterStream client or "cron"
                    for cron job runner.
    <room>          Either Gitter room name or Gitter username.
    <client-id>     ID of the client that is to be shut-down.
"""


import os
import socket
import pickle
import json
import sys
from docopt import docopt

from multiprocessing import Process
from hadroid import C, __version__


def client_function(client):
    """Client listener as a function passed to the process."""
    client.listen()


def start_client(clients, client_name, room):
    """Start the client."""
    client_class = C.CLIENTS[client_name]
    client_id = max(clients.keys()) + 1 if clients else 0
    args = (C.GITTER_PERSONAL_ACCESS_TOKEN, )
    client = client_class(*args)
    room_id = client.resolve_room_id(room)
    process_name = "{0} {1}".format(client_class.__name__, room)
    client.room_id = room_id
    p = Process(target=client_function, args=(client, ), name=process_name)
    clients[client_id] = dict(process=p,
                              room=room,
                              client_name=client_name)
    p.start()
    return client_id


def stop_client(clients, client_id):
    """Stop the client."""
    if client_id not in clients:
        print("Client {0} not found.".format(client_id))
    p = clients[client_id]['process']
    p.terminate()
    del clients[client_id]


def save_clients(clients):
    """Serialize the clients."""
    print("Serializing processes.")
    serialized = [(id_, cl['client_name'], cl['room'])
                  for id_, cl in clients.items()]
    print("Saving.")
    with open('hadroid_clients.json', 'w') as fp:
        json.dump(serialized, fp, indent=2)


def manage_clients(clients, args):
    """Manage the bot clients."""
    if args['start']:
        room = args['<room>']
        client_name = args['<client-name>']
        client_id = start_client(clients, client_name, room)
        save_clients(clients)
        return client_id

    if args['stop']:
        # Stop a client
        client_id = int(args['<client-id>'])
        stop_client(clients, client_id)
        save_clients(clients)
        return client_id

    if args['list']:
        return [(id_, cl['process'].name) for id_, cl in clients.items()]

    if args['shutdown']:
        # Save all processes and shut down
        save_clients(clients)
        print("Terminating clients.")
        for client_id in list(clients.keys()):
            stop_client(clients, client_id)
        print("Shutting down.")
        sys.exit(0)
    if args['save']:
        save_clients(clients)


def server():
    """Run the client manager."""
    clients = {}
    socket_path = C.SOCKET_PATH
    print("Unlinking socket.")
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            raise

    if os.path.isfile('hadroid_clients.json'):
        with open('hadroid_clients.json', 'r') as fp:
            loaded_clients = json.load(fp)
        for id_, client_name, room in loaded_clients:
            start_client(clients, client_name, room)
        print("Loaded {} clients.".format(len(loaded_clients)))

    print("Creating socket.")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        print("Binding.")
        s.bind(socket_path)
        print("Listending for messages.")
        while True:
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                print('Received message.')
                data = conn.recv(C.SOCKET_BUFSIZE)
                args = pickle.loads(data)
                ret = manage_clients(clients, args)
                b_ret = pickle.dumps(ret)
                conn.sendall(b_ret)


def client(args):
    """Execute a client command."""
    socket_path = C.SOCKET_PATH
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(socket_path)
        b_msg = pickle.dumps(args)
        s.sendall(b_msg)
        if not args['shutdown']:
            b_data = s.recv(C.SOCKET_BUFSIZE)
            data = pickle.loads(b_data)
            return data
        else:
            return "Sent the shutdown signal."


def main():
    """Main bot function function."""
    args = docopt(__doc__, version=__version__)

    if args['run']:
        server()
    else:
        ret = client(args)
        print(ret)


if __name__ == '__main__':
    main()
