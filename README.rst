=============
 Hadroid Bot
=============

Installation
============
Hadroid is not on PyPI but it's easy to install from sources:

.. code-block:: console

   $ git clone https://github.com/krzysztof/hadroid.git
   $ cd hadroid
   $ pip install -e .

Configuration
=============
Copy the default configuration file:

.. code-block:: console

   $ cp hadroid/config.py myconfig.py

Edit the ``myconfig.py`` and set the ``GITTER_PERSONAL_ACCESS_TOKEN`` to your
Gitter API token.

Point to your config with environmental variable:

.. code-block:: console

   $ export HADROID_CONFIG=myconfig.py

Usage
=====
There are two main bot files: ``bot.py`` and ``botctl.py``. The ``bot.py`` is
only useful when running the bot program locally as a single-command execution.
The ``botctl.py`` allows for launching ongoing bot "daemons" that can listen
on the Gitter channels for incoming commands or execute periodic commands.

Test the bot locally
~~~~~~~~~~~~~~~~~~~~
Either call the bot directly:

.. code-block:: console

   $ python hadroid/bot.py --help
   $ python hadroid/bot.py ping

or through the controller with ``stdout`` client:

.. code-block:: console

   $ python hadroid/botctl.py stdout ping

Run the bot on Gitter
~~~~~~~~~~~~~~~~~~~~
Bot will listen for messages and reply back on a single channel.
This can be either an orgazation channel, repository or a private one-on-one
chat with a user. The bot needs to be already in the room, or at least one
private message needs to be send to the bot.

Run the bot on some of the room he's already in, or chat with him privately:

.. code-block:: console

   $ python hadroid/botctl.py stream 'myorg/myroom' --verbose
   $ python hadroid/botctl.py stream 'myorg/somerepo' --verbose
   $ python hadroid/botctl.py stream 'myusername' --verbose

For CRON commands, run a CRON daemon in a separate shell:

.. code-block:: console

   $ python hadroid/botctl.py cron mytestroom --verbose


Deployment
==========
To deploy Hadroid you can use the provided `fabile.py
<http://docs.fabfile.org/en/latest/>`_ (tested on commonly used VPS vanilla
instances of Ubuntu 16.04 and Debian 8) in the following manner:

.. code-block:: console

   $ # fabtools is a helper library for Fabric
   $ pip2 install --user fabric fabtools

   $ # "bootstrap" has to run once for each machine you plan to deploy
   $ fab -U root -H my-server.xyz bootstrap

   $ # You should run "deploy" everytime you change the config as well
   $ fab -U root -H my-server.xyz deploy:config_path=/path/to/your/config.py

   $ # To manage the bot you can use the "start/stop/restart" commands:
   $ fab -U root -H my-server.xyz start

Take a look and modify the fabfile if your remote machine doesn't play well.
