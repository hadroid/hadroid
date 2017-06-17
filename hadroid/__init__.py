"""Hadroid bot."""
import os
import importlib.util
from collections import namedtuple


Module = namedtuple('Module', ['names', 'main', 'usage'])


def _load_config_from_path(cfg_path):
    """Load configuration from path."""
    if cfg_path is not None and os.path.isfile(cfg_path):
        spec = importlib.util.spec_from_file_location(".", cfg_path)
        cfg_m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cfg_m)
        return dict((k, getattr(cfg_m, k)) for k in
                    dir(cfg_m) if str.isupper(k))
    else:
        raise Exception("Path '{0}' is not a valid config".format(
            cfg_path))


def load_default_config():
    """Load the default configuration."""
    cfg_path = os.path.join(os.path.dirname(__file__), 'config.py')
    return _load_config_from_path(cfg_path)


def load_config_from_env():
    """Load the extra configuration from environment."""
    cfg_path = os.environ.get('HADROID_CONFIG')
    if not cfg_path:
        raise Exception('HADROID_CONFIG variable not set.')
    return _load_config_from_path(cfg_path)


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
            self_cfg = load_default_config()
            self_cfg.update(load_config_from_env())
            self.cfg = self_cfg
        if attr in self_cfg:
            return self_cfg[attr]
        else:
            return super(Config, self).__getattribute__(attr)


C = Config()

__version__ = '0.1.4'

__all__ = ('C', '__version__', 'config', 'build_usage_str', 'Module')
