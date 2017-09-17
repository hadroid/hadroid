import os

import pytest


@pytest.fixture
def datadir():
    """Test data directory."""
    return os.path.join(os.path.dirname(__file__), 'data')


@pytest.yield_fixture
def env_testconfig(datadir):
    """Test custom configuration of Hadroid."""
    orig = os.environ.get('HADROID_CONFIG')
    os.environ['HADROID_CONFIG'] = os.path.join(datadir, 'testconfig.py')
    yield
    if orig:
        os.environ['HADROID_CONFIG'] = orig


@pytest.fixture
def default_client_args():
    """Default arguments passed to the hadroid."""
    d = {
        'start': False,
        'status': False,
        'stop': False,
        'spawn': False,
        'kill': False,
        'list': False,
        '<client-type>': None,
        '<room>': None,
        '<client-id>': None,
    }
    return d


@pytest.fixture
def menus(datadir):
    """Menu mock."""
    with open(os.path.join(datadir, 'menus.json'), 'r') as fp:
        menus_data = json.load(fp)
    return menus_data
