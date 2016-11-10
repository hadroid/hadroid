import pytest
import os
import json


@pytest.fixture
def datadir():
    return os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture
def menus(datadir):
    with open(os.path.join(datadir, 'menus.json'), 'r') as fp:
        menus_data = json.load(fp)
    return menus_data
