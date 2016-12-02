Hadroid Gitter bot.

Installation
============
Hadroid is not on PyPI but it's easy to install from sources:

``git clone https://github.com/krzysztof/hadroid.git``
``cd hadroid``
``pip install -e .``

Configuration
=============
1. Copy the default configuration file:
``cp hadroid/config.py myconfig.py``

2. Edit the ``myconfig.py`` and set the ``GITTER_PERSONAL_ACCESS_TOKEN`` to your
Gitter API token. It is convenient to add at least one room to ROOMS.

3. Point to your config with environmental variable
``export HADROID_CONFIG=myconfig.py``

Usage
=====
There are two main bot files: ``bot.py`` and ``botctl.py``. The ``bot.py`` is
only useful when running the bot program locally as a single-command execution.
The ``botctl.py`` allows for launching ongoing bot "daemons" that can listen
on the Gitter channels for incoming commands or execute periodic commands.

Test the bot locally
--------------------
Either call the bot directly:
``python hadroid/bot.py --help``
``python hadroid/bot.py ping``

or through the controller with ``stdout`` client:
``python hadroid/botctl.py stdout ping``

Run the bot on Gitter
---------------------
1. Run the bot on the ``mytestroom`` (if defined in ROOMS inside config) or
by Gitter room ID:
``python hadroid/botctl.py stream mytestroom --verbose``
``python hadroid/botctl.py stream 1234567890 --verbose``

2. For CRON jobs, run a CRON daemon in a separate shell:
``python hadroid/botctl.py cron mytestroom --verbose``
