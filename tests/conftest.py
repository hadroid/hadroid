import json
import os

import pytest


@pytest.fixture
def datadir():
    return os.path.join(os.path.dirname(__file__), 'data')


@pytest.yield_fixture
def env_testconfig(datadir):
    orig = os.environ.get('HADROID_CONFIG')
    os.environ['HADROID_CONFIG'] = os.path.join(datadir, 'testconfig.py')
    yield
    if orig:
        os.environ['HADROID_CONFIG'] = orig


@pytest.fixture
def default_client_args():
    d = {
        'run': False,
        'shutdown': False,
        'start': False,
        'stop': False,
        'list': False,
        '<client-name>': None,
        '<room>': None,
        '<client-id>': None,
    }
    return d


@pytest.fixture
def menus(datadir):
    with open(os.path.join(datadir, 'menus.json'), 'r') as fp:
        menus_data = json.load(fp)
    return menus_data


@pytest.fixture
def uservoice_tickets(datadir):
    """Uservoice tickets response mock."""
    with open(os.path.join(datadir, 'uservoice_tickets.json'), 'r') as fp:
        data = json.load(fp)
    return data
