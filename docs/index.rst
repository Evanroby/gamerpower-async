gamerpower-async
================

An unofficial asynchronous Python wrapper for the `GamerPower <https://www.gamerpower.com>`_
API, which tracks free games, in-game loot and beta keys that are being given away.

.. code-block:: python

   import asyncio

   from gamerpower import GamerPower, Platform


   async def main():
       async with GamerPower() as gp:
           for g in await gp.giveaways(Platform.EPIC_GAMES_STORE):
               print(g.title, g.end_date)


   asyncio.run(main())

Features
--------

- Fully asynchronous, built on ``httpx``, with type hints throughout.
- Filter by platform and type, sort by date, value or popularity.
- :meth:`~gamerpower.GamerPower.watch` turns the API into a stream of new giveaways, ready to
  plug into a Discord bot.
- Built-in rate limiting and retries.
- No API key needed.

.. note::

   This project is not affiliated with GamerPower. Their terms ask for an active hyperlink back
   to GamerPower.com wherever you show their data, see :doc:`terms`.

.. toctree::
   :maxdepth: 2
   :caption: Getting started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: Guides

   guides/filtering
   guides/watching
   guides/errors
   guides/discord-bot

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api
   changelog
   terms
