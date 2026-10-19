Watching for new giveaways
==========================

:meth:`~gamerpower.GamerPower.watch` polls the API and yields each giveaway the first time it
appears. It is an async generator, so you consume it with ``async for``:

.. code-block:: python

   async with GamerPower() as gp:
       async for g in gp.watch(interval=300, platform=Platform.EPIC_GAMES_STORE):
           print("new:", g.title)

It never ends by itself. Stop it by breaking out of the loop, calling ``aclose()`` on the
generator, or cancelling the task that runs it.

What counts as new
------------------

The watcher keeps a set of giveaway ids it has already seen.

- **Without** ``seen``, the first successful poll only fills the set and yields nothing. A bot
  that restarts therefore does not announce every active giveaway again.
- **With** ``seen``, every giveaway whose id is not in your set is yielded right away,
  including on the first poll.

Inside one poll, giveaways come oldest first. The id is added to the set just before the
giveaway is yielded, so the set you passed always reflects what has been handed to you.

When a poll fails
-----------------

A failed poll is logged on the ``gamerpower`` logger as a warning and tried again after
``interval`` seconds. The generator keeps running. To see these warnings:

.. code-block:: python

   import logging

   logging.getLogger("gamerpower").setLevel(logging.WARNING)

Watching several filters
------------------------

Every ``watch()`` call polls on its own, so five watchers make five requests per interval. When
you want several platforms, run one unfiltered watcher and filter in code:

.. code-block:: python

   wanted = {"Epic Games Store", "Steam"}

   async for g in gp.watch():
       if wanted & set(g.platforms):
           ...

.. _watching-db:

Surviving restarts with a database
----------------------------------

The in-memory set is lost when the process stops, and the first-poll rule then hides anything
that appeared while the bot was offline. To keep state, store the ids you have handled and
pass them back in. This example uses ``asyncpg`` and PostgreSQL:

.. code-block:: python

   SCHEMA = "CREATE TABLE IF NOT EXISTS gamerpower_seen (id INTEGER PRIMARY KEY)"
   INSERT = "INSERT INTO gamerpower_seen (id) VALUES ($1) ON CONFLICT DO NOTHING"


   async def load_seen(pool, gp) -> set[int]:
       rows = await pool.fetch("SELECT id FROM gamerpower_seen")
       if rows:
           return {r["id"] for r in rows}
       # first run: mark everything that exists right now as seen, so only new giveaways get posted
       seen = {g.id for g in await gp.giveaways()}
       await pool.executemany(INSERT, [(i,) for i in seen])
       return seen


   async def run(pool, gp, post):
       seen = await load_seen(pool, gp)
       async for g in gp.watch(seen=seen):
           await post(g)
           await pool.execute(INSERT, g.id)

Two details matter here:

- **Seed the table on the first run.** Passing an empty ``seen`` set makes the watcher yield
  every active giveaway at once, which would flood a channel.
- **Record the id after posting.** If the process dies between the two steps, you post the
  giveaway twice on the next start. Recording first would instead lose it silently.
