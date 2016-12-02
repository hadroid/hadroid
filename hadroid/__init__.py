"""Hadroid bot."""
import os
import importlib.util


def load_config_from_module(mod):
    """Load the configuration from a module."""
    return dict((k, getattr(mod, k)) for k in dir(mod) if str.isupper(k))


def load_config_from_env():
    """Loads the extra configuration from environment."""
    cfg_path = os.environ.get('HADROID_CONFIG')
    if cfg_path is not None:
        spec = importlib.util.spec_from_file_location(".", cfg_path)
        cfg_m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cfg_m)
        return load_config_from_module(cfg_m)
    return {}


class Config(object):
    """Config object."""
    def __init__(self):
        self.cfg = None

    def __getattribute__(self, attr):
        self_cfg = super(Config, self).__getattribute__('cfg')
        if self_cfg is None:
            import hadroid.config
            # Load the default configuration
            self_cfg = load_config_from_module(hadroid.config)
            # Update with user configuration
            self_cfg.update(load_config_from_env())
            self.cfg = self_cfg
        if attr in self_cfg:
            return self_cfg[attr]
        else:
            return super(Config, self).__getattribute__(attr)


C = Config()
__version__ = '0.1.0'

__all__ = ('C', '__version__', )
