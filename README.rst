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
Gitter API token. It is convenient to add at least one room to ROOMS.

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
Run the bot on the ``mytestroom`` (if defined in ROOMS inside config) or
by Gitter room ID:

.. code-block:: console

   $ python hadroid/botctl.py stream mytestroom --verbose
   $ python hadroid/botctl.py stream 1234567890 --verbose

For CRON commands, run a CRON daemon in a separate shell:

.. code-block:: console

   $ python hadroid/botctl.py cron mytestroom --verbose
