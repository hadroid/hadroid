"""
The main Hadroid bot application.

Hadroid is ran as a kind-of a daemon (see "start", "stop" and "status"),
which controls a variety of clients (see "spawn", "kill" and "list").

Start the Hadrod daemon in the background:
  hadroid start &

You can check the daemon status with "status", or stop it with "stop":
  hadroid status
  hadroid stop

Spawn some clients (sub-processes):
  hadroid spawn stream <mygitterusername>
  hadroid spawn cron <mygitterusername>

then list the clients and their IDs:
  hadroid list

and finally kill some clients by their ID:
  hadroid kill 1

Usage:
    hadroid start
    hadroid status
    hadroid stop
    hadroid spawn <client-type> <room>
    hadroid kill <client-id>
    hadroid list

Examples:
    hadroid start
    hadroid spawn stream krzysztof
    hadroid spawn stream zenodo
    hadroid spawn cron zenodo
    hadroid spawn stream zenodo/zenodo

Options:
    <client-type>   Type of the client, can be either "stream" for GitterStream
                    client or "cron" for cron job runner.
    <room>          Either Gitter room name or Gitter username.
    <client-id>     ID of the client that is to be shut-down.
"""


import json
import logging
import os
import pickle
import socket
import sys
from multiprocessing import Process

from docopt import docopt

from hadroid import C, __version__

logging.basicConfig(
    filename=C.LOGFILE, level=logging.DEBUG, datefmt='%d/%m/%Y %H:%M:%S',
    format='%(asctime)s [%(process)d] %(levelname)s:%(message)s')


def spawn_client(clients, client_type, room):
    """Start a new bot client."""
    client_class = C.CLIENTS[client_type]
    client_id = max(clients.keys()) + 1 if clients else 0
    args = (C.GITTER_PERSONAL_ACCESS_TOKEN, )
    client = client_class(*args)
    room_id = client.resolve_room_id(room)
    process_name = "{0} {1}".format(client_class.__name__, room)
    client.room_id = room_id
    p = Process(target=client.listen, name=process_name)
    clients[client_id] = dict(process=p,
                              room=room,
                              client_type=client_type)
    p.start()
    logging.info("Client with ID {} started.".format(client_id))
    return client_id


def kill_client(clients, client_id):
    """Kill the currently running bot client."""
    if client_id not in clients:
        logging.info("Client {0} not found.".format(client_id))
    p = clients[client_id]['process']
    p.terminate()
    logging.info("Client {0} terminated.".format(client_id))
    del clients[client_id]


def serialize_clients(clients):
    """Serialize the clients to JSON and write them to disk."""
    logging.info("Serializing processes.")
    serialized = [(id_, cl['client_type'], cl['room'])
                  for id_, cl in clients.items()]
    logging.info("Saving.")
    with open('hadroid_clients.json', 'w') as fp:
        json.dump(serialized, fp, indent=2)


def list_clients(clients):
    """List the currently running clients."""
    return [(id_, cl['process'].name) for id_, cl in clients.items()]


def manage_clients(clients, args):
    """Manage the bot clients."""
    if args['status']:
        # If you got to this line, it means the Hadroid is running
        return "Hadroid is running."
    elif args['stop']:
        # Save all processes and shut down
        serialize_clients(clients)
        logging.info("Received the shutdown command.")
        logging.info("Terminating clients.")
        for client_id in list(clients.keys()):
            kill_client(clients, client_id)
        logging.info("Shutting down.")
        sys.exit(0)
    elif args['spawn']:
        logging.info("Starting a new client.")
        room = args['<room>']
        client_type = args['<client-type>']
        client_id = spawn_client(clients, client_type, room)
        serialize_clients(clients)
        return client_id
    elif args['kill']:
        # Kill a client
        logging.info("Stopping a client.")
        client_id = int(args['<client-id>'])
        kill_client(clients, client_id)
        serialize_clients(clients)
        return client_id
    elif args['list']:
        logging.info("Listing clients.")
        return list_clients(clients)


def run_server():
    """Run the client manager."""
    clients = {}
    socket_path = C.SOCKET_PATH
    logging.info("\n")
    logging.info("Starting Hadroid session.")
    logging.info("Unlinking socket.")
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            raise

    if os.path.isfile('hadroid_clients.json'):
        with open('hadroid_clients.json', 'r') as fp:
            loaded_clients = json.load(fp)
        for id_, client_type, room in loaded_clients:
            spawn_client(clients, client_type, room)
        logging.info("Loaded {} clients.".format(len(loaded_clients)))

    logging.info("Creating socket.")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        logging.info("Binding.")
        s.bind(socket_path)
        logging.info("Listening for messages.")
        while True:
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                logging.info('Received message.')
                data = conn.recv(C.SOCKET_BUFSIZE)
                args = pickle.loads(data)
                ret = manage_clients(clients, args)
                b_ret = pickle.dumps(ret)
                conn.sendall(b_ret)


def ctl_server(args):
    """Control the running Hadroid server."""
    socket_path = C.SOCKET_PATH
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(socket_path)
        b_msg = pickle.dumps(args)
        s.sendall(b_msg)
        if not args['stop']:
            b_data = s.recv(C.SOCKET_BUFSIZE)
            data = pickle.loads(b_data)
            return data
        else:
            return "Sent the shutdown signal to Hadroid."


def main():
    """Main execution function."""
    args = docopt(__doc__, version=__version__)

    if args['start']:
        run_server()
    else:
        try:
            ret = ctl_server(args)
            print(ret)
        except (ConnectionRefusedError, FileNotFoundError) as e:
            print("Could not connect to Hadroid (is it running?).")


if __name__ == '__main__':
    main()
