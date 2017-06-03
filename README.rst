=============
 Hadroid Bot
=============

Installation
============
Hadroid is on PyPI:

.. code-block:: console

   $ pip install hadroid

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
The bot is run using the ``hadroid`` command,
which allows for launching bot threads that can listen
on the Gitter channels for incoming commands or execute periodic tasks.

Run the bot on Gitter
~~~~~~~~~~~~~~~~~~~~
Bot will listen for messages and reply back on a single channel.
This can be either an orgazation channel, repository or a private one-on-one
chat with a user. The bot needs to be already in the room, or at least one
private message needs to be send to the bot.

First, run the main bot "server" application:

.. code-block:: console

   $ hadroid run

Keep this session alive an in another session have the bot join some channels:

.. code-block:: console

   $ hadroid --help

For CRON commands, run a CRON daemon in a separate shell:

.. code-block:: console

   $ hadroid start stream <your_github_username>
   $ hadroid start cron <your_github_username>

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
