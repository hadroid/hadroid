import pytest
import os
import json


@pytest.fixture
def datadir():
    return os.path.join(os.path.dirname(__file__), 'data')


def walk_test_files(dirname):
    dn, _, fns = next(os.walk(dirname))
    for fn in fns:
        if not fn.startswith('.') and fn.endswith(('html', 'json')):
            with open(os.path.join(dn, fn), 'r') as fp:
                yield fp


@pytest.fixture
def menus_html(datadir):
    ret = {}
    for fp in walk_test_files(os.path.join(datadir, 'menus')):
        name = os.path.basename(fp.name).rpartition('.')[0]
        ret[name] = fp.read()
    return ret


@pytest.fixture
def menus_parsed_expected(datadir):
    exp = {}
    for fp in walk_test_files(os.path.join(datadir, 'menus', 'parsed')):
        name = os.path.basename(fp.name).rpartition('.')[0]
        exp[name] = json.load(fp)
    return exp
