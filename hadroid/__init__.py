"""Hadroid bot."""
import os
import importlib.util
from collections import namedtuple


Module = namedtuple('Module', ['names', 'main', 'usage'])


def load_config_from_module(mod):
    """Load the configuration from a module."""
    return dict((k, getattr(mod, k)) for k in dir(mod) if str.isupper(k))


def load_config_from_env():
    """Load the extra configuration from environment."""
    cfg_path = os.environ.get('HADROID_CONFIG')
    if cfg_path is not None and os.path.isfile(cfg_path):
        spec = importlib.util.spec_from_file_location(".", cfg_path)
        cfg_m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cfg_m)
        return load_config_from_module(cfg_m)
    return {}


def build_usage_str(modules, botname):
    """Build the bot usage string from the list of modules.

    :type botname: str
    :type modules: (Module)
    :param modules: iterable of Module objects
    """
    return"\n".join(("    @{0} {1}".format(botname,
                                           m.usage or m.names[0])
                     for m in modules))


class Config(object):
    """Config object."""

    def __init__(self):
        self.cfg = None

    def __getattribute__(self, attr):
        self_cfg = super(Config, self).__getattribute__('cfg')
        if self_cfg is None:
            # Load the configuration from the environment
            self_cfg = load_config_from_env()
            self.cfg = self_cfg
        if attr in self_cfg:
            return self_cfg[attr]
        else:
            return super(Config, self).__getattribute__(attr)


C = Config()

__version__ = '0.1.1'

__all__ = ('C', '__version__', 'config', 'build_usage_str', 'Module')
