Errors, retries and rate limits
===============================

Exceptions
----------

Every error raised by the library inherits from :class:`~gamerpower.GamerPowerError`, so one
``except`` clause catches them all.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Exception
     - Raised when
   * - :class:`~gamerpower.NotFound`
     - :meth:`~gamerpower.GamerPower.giveaway` is asked for an id that does not exist.
   * - :class:`~gamerpower.HTTPError`
     - The API answers with an unexpected status. The code is in its ``status`` attribute.
   * - :class:`~gamerpower.GamerPowerError`
     - A request keeps failing at the network level (timeout, connection error), the body is not
       JSON, or the JSON does not look like a giveaway.

.. code-block:: python

   from gamerpower import GamerPowerError, NotFound

   try:
       g = await gp.giveaway(3817)
   except NotFound:
       ...
   except GamerPowerError as e:
       print("gamerpower is having trouble:", e)

Empty results are not errors
----------------------------

The API reports "nothing found" either with HTTP 201 or with an error-style JSON body
(``{"status": 0, "status_message": ...}``). The client treats both the same way: lists come back
empty, :meth:`~gamerpower.GamerPower.worth` returns zeros, and
:meth:`~gamerpower.GamerPower.giveaway` raises :class:`~gamerpower.NotFound`.

This also means a filter value the API does not know gives an empty list rather than an
exception.

Retries
-------

A request is attempted up to three times. The client retries on network errors, HTTP 429 and
HTTP 5xx, waiting 0.5 seconds and then 1 second between attempts. If the last attempt fails too,
the error is raised.

Other 4xx responses are not retried: they raise :class:`~gamerpower.HTTPError` immediately, and
404 raises :class:`~gamerpower.NotFound`.

Timeouts
--------

The client creates its own ``httpx.AsyncClient`` with a 10 second timeout. To use other
settings, build the client yourself and pass it in:

.. code-block:: python

   import httpx

   http = httpx.AsyncClient(timeout=30)
   gp = GamerPower(http=http)

You are then responsible for closing ``http``.

Rate limiting
-------------

GamerPower asks for no more than 10 requests per second. The client spaces its requests at
least 0.15 seconds apart, which is about 6 requests per second, and applies this to every call
made through the same ``GamerPower`` instance, even from concurrent tasks.

The limit is per instance. If you run several clients or several processes, they do not know
about each other, so keep an eye on the total.
