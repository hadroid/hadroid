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
    botctl start <client> <room>
    botctl stop <client-id>
    botctl list

Examples:
    botctl run
    botctl start stream krzysztof
    botctl start cron zenodo
    botctl start stream zenodo
    botctl start stream zenodo/zenodo

Options:
    <client>        Can be either "stream" for GitterStream client or "cron"
                    for cron job runner.
    <room>          Either Gitter room name or Gitter username.
    <client-id>     ID of the client that is to be shut-down.
"""


import os
import socket
import pickle
from docopt import docopt

from multiprocessing import Process
from hadroid import C, __version__


def client_function(client):
    """Client listener as a function passed to the process."""
    client.listen()


def manage_clients(client_processes, args):
    """Manage the bot clients."""
    if args['start']:
        room = args['<room>']
        client_name = args['<client>']

        client_class = C.CLIENTS[client_name]
        client_id = max(client_processes.keys()) + 1 if client_processes else 0
        args = (C.GITTER_PERSONAL_ACCESS_TOKEN, )
        client = client_class(*args)
        room_id = client.resolve_room_id(room)
        process_name = "{0} {1}".format(client_class.__name__, room)
        client.room_id = room_id
        p = Process(target=client_function, args=(client, ), name=process_name)
        client_processes[client_id] = p
        p.start()
        return "Created {0}".format(client_id)

    if args['stop']:
        client_id = int(args['<client-id>'])

        if client_id not in client_processes:
            print("Client {0} not found.".format(client_id))
        p = client_processes[client_id]
        p.terminate()
        del client_processes[client_id]
        return "Stopped {0}".format(client_id)

    if args['list']:
        return "\n".join(["{0} {1}".format(uuid, process.name)
                          for uuid, process in client_processes.items()])


def server():
    """Run the client manager."""
    client_processes = {}
    socket_path = '/tmp/hadroid_socket'
    print("Unlinking socket.")
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            raise
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
                data = conn.recv(1024)
                args = pickle.loads(data)
                ret = manage_clients(client_processes, args)
                b_ret = pickle.dumps(ret)
                conn.sendall(b_ret)


def main():
    """Main bot function function."""
    args = docopt(__doc__, version=__version__)

    if args['run']:
        server()
    else:
        socket_path = '/tmp/hadroid_socket'
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(socket_path)
            b_msg = pickle.dumps(args)
            s.sendall(b_msg)
            b_data = s.recv(1024)
            data = pickle.loads(b_data)
            print(data)


if __name__ == '__main__':
    main()
