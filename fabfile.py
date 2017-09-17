#!/usr/bin/env python
"""Fabric commands for provisioning Hadroid

Attention!!! This file is still a WIP. Most of the commands are unstable and
not tested properly, so use with caution.
"""

import tempfile
from os.path import join as join_path

from fabric.api import cd, env, local, settings, shell_env, sudo
from fabric.contrib.project import rsync_project
from fabtools import python, require, supervisor

#
# Utilities
#

class sudosu:
    def __init__(self, user):
        self.user = user

    def __enter__(self):
        self.old_sudo_prefix = env.sudo_prefix
        self.old_sudo_user, env.sudo_user = env.sudo_user, self.user
        env.sudo_prefix = "sudo -S -p '%(sudo_prompt)s' su - %(sudo_user)s -c"

    def __exit__(self, a, b, c):
        env.sudo_prefix = self.old_sudo_prefix
        env.sudo_user = self.old_sudo_user

#
# Basic configuration
#

env.use_ssh_config = True

env.app_user = 'hadroid'
env.app_name = env.app_user

env.app_path = '/srv/hadroid'
env.code_path = join_path(env.app_path, 'code')
env.etc_path = join_path(env.app_path, 'etc')

env.venv_path = join_path(env.app_path, 'venv')
env.venv_bin = join_path(env.venv_path, 'bin')

env.hadroid_bot = join_path(env.venv_bin, 'hadroid-bot')
env.hadroid_botctl = join_path(env.venv_bin, 'hadroid-botctl')

env.hadroid_config = join_path(env.etc_path, 'hadroid_config.py')


#
# Bootstrap
#

def bootstrap():
    """Bootstrap a fresh machine."""
    install_system_deps()
    setup_environment()


def install_system_deps():
    """Install system services and binaries."""
    require.deb.package('virtualenv')
    require.deb.package('supervisor')


def setup_environment():
    """Setup users, groups, supervisor, etc."""
    # FIXME: When `fabtools v0.21.0` gets released, remove this...
    with shell_env(SYSTEMD_PAGER=''):
        require.users.user(
            name=env.app_user,
            group=env.app_user,
            system=True,
            shell='/bin/bash',
        )

        for path in (env.app_path, env.etc_path):
            require.directory(
                path=path,
                owner=env.app_user,
                group=env.app_user,
                use_sudo=True,
            )

        require.python.virtualenv(
            directory=env.venv_path,
            venv_python='python3',
            user=env.app_user,
            use_sudo=True,
        )

        require.supervisor.process(
            name=env.app_name,
            command='{} stream --verbose'.format(env.hadroid_botctl),
            user=env.app_user,
            directory=env.app_path,
            stdout_logfile='/var/log/hadroid.log',
            stderr_logfile='/var/log/hadroid-err.log',
            environment='HADROID_CONFIG={}'.format(env.hadroid_config),
        )


#
# Deploy
#

def deploy(config_path=None):
    """Deploy Hadroid (requires running "bootstrap" once)."""
    install_package()
    if config_path:
        update_config(config_path)
    restart_supervisor()


def install_package():
    """Install the Hadroid Python package."""
    with tempfile.NamedTemporaryFile() as src_files:
        local('git ls-files --exclude-standard > {}'.format(src_files.name))
        rsync_project(
            remote_dir=env.code_path,
            local_dir='./',
            extra_opts=('--rsync-path="sudo -u {} rsync" --files-from={}'
                        .format(env.app_user, src_files.name)),
            delete=True,
            default_opts='-thrvz')
    with sudosu(user=env.app_user), python.virtualenv(env.venv_path), \
            cd(env.code_path):
        with settings(warn_only=True):
            sudo('pip uninstall -y hadroid')
        sudo('pip install -e .')


def update_config(config_path):
    """Update the Hadroid config."""
    require.file(
        path=env.hadroid_config,
        source=config_path,
        owner=env.app_user,
        group=env.app_user,
        mode='0600',
        use_sudo=True,
    )


#
# Supervisord management
#

def start_hadroid(app_name=None):
    """Start the supervisor process."""
    supervisor.start_process(app_name or env.app_name)


def stop_hadroid(app_name=None):
    """Stop the supervisor process."""
    supervisor.stop_process(app_name or env.app_name)


def restart_supervisor(app_name=None):
    """Restart the supervisor process."""
    supervisor.restart_process(app_name or env.app_name)
