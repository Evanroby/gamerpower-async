Filtering and sorting
=====================

:meth:`~gamerpower.GamerPower.giveaways` takes three optional arguments: ``platform``, ``type``
and ``sort_by``.

Platforms, types and sort orders
--------------------------------

Use the enums for autocompletion and typo safety. They are string enums, so a plain string
works too, which is handy for a value the API adds after this release.

.. code-block:: python

   from gamerpower import GiveawayType, Platform, SortBy

   await gp.giveaways(Platform.GOG)
   await gp.giveaways("gog")                      # same request
   await gp.giveaways(type=GiveawayType.LOOT)
   await gp.giveaways(sort_by=SortBy.POPULARITY)

See :class:`~gamerpower.Platform`, :class:`~gamerpower.GiveawayType` and
:class:`~gamerpower.SortBy` for every value.

Several platforms or types
--------------------------

Pass a list to match any of them:

.. code-block:: python

   await gp.giveaways(
       platform=[Platform.EPIC_GAMES_STORE, Platform.GOG],
       type=[GiveawayType.GAME, GiveawayType.LOOT],
       sort_by=SortBy.VALUE,
   )

How the request is sent depends on what you pass:

- One platform and one type (or fewer) go to the API's ``/giveaways`` endpoint, which also does
  the sorting.
- More than one platform or type go to ``/filter``, which has no sort option. The library then
  sorts the result itself, newest, most valuable or most popular first. A giveaway with no
  ``worth`` counts as zero when sorting by value.

You get the same order either way.

Slugs and labels are different
------------------------------

The values you filter with (``"epic-games-store"``) are not the values you read back
(``"Epic Games Store"``). Compare against the labels when you check a result in code:

.. code-block:: python

   for g in await gp.giveaways():
       if "Epic Games Store" in g.platforms:
           ...

:attr:`Giveaway.platforms <gamerpower.Giveaway.platforms>` is a tuple of labels, one per
platform, in the order the API lists them. Some labels have no documented filter slug, for
example ``"VR"``. Filtering by a slug the API does not know returns an empty list, so check the
slug if a filter unexpectedly finds nothing.

Nothing matches
---------------

An empty result is a normal answer, not an error: ``giveaways()`` returns ``[]`` and
``worth()`` returns zeros. A missing giveaway id is the one case that raises
:class:`~gamerpower.NotFound`, see :doc:`errors`.
