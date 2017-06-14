"""Test the hadroid."""

from multiprocessing import Process
from hadroid.botctl import server, client
from time import sleep

def _server_run():
    server()


def off_test_server(env_testconfig, default_client_args):
    """Test version import."""
    p = Process(target=_server_run)
    p.start()
    # TODO: Needs a better way to run this async
    sleep(3)
    default_client_args.update({'list': True})
    ret = client(default_client_args)

