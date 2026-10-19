Quickstart
==========

Every call is a coroutine, so run them inside an event loop. The examples below leave out the
``asyncio.run(main())`` boilerplate shown on the :doc:`front page <index>`.

List giveaways
--------------

.. code-block:: python

   from gamerpower import GamerPower

   async with GamerPower() as gp:
       for g in await gp.giveaways():
           worth = f"${g.worth:.2f}" if g.worth is not None else "unknown value"
           ends = g.end_date or "no end date"
           print(f"{g.title} ({worth}), ends: {ends}")
           print(g.open_giveaway_url)

Each item is a :class:`~gamerpower.Giveaway`. Its fields are listed in the
:doc:`API reference <api>`. Two of them can be ``None``: ``worth`` when the API reports
``"N/A"`` and ``end_date`` when the giveaway has no end date.

Filter and sort
---------------

.. code-block:: python

   from gamerpower import GiveawayType, Platform, SortBy

   best_steam_games = await gp.giveaways(Platform.STEAM, GiveawayType.GAME, SortBy.VALUE)

See :doc:`guides/filtering` for combining several platforms and for what the filters accept.

Get one giveaway
----------------

.. code-block:: python

   from gamerpower import NotFound

   try:
       g = await gp.giveaway(3817)
   except NotFound:
       print("no giveaway with that id")

Count and value of the live giveaways
-------------------------------------

.. code-block:: python

   total = await gp.worth()
   print(total.active_giveaways, total.worth_usd)

Closing the client
------------------

``async with`` closes the underlying HTTP session for you. Without it, close the client
yourself:

.. code-block:: python

   gp = GamerPower()
   try:
       games = await gp.giveaways()
   finally:
       await gp.close()

To share one ``httpx.AsyncClient`` with the rest of your application, pass it in with
``GamerPower(http=client)``. The client then leaves it open.

Next steps
----------

- Get notified of new giveaways with :doc:`guides/watching`.
- Know what can go wrong in :doc:`guides/errors`.
- Post new giveaways from a Discord bot with :doc:`guides/discord-bot`.
