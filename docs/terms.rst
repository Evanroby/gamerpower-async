Terms and attribution
=====================

This library is a client for the `GamerPower API <https://www.gamerpower.com/api-read>`_. It is
unofficial and not affiliated with GamerPower.

GamerPower's terms
------------------

As published on the `API page <https://www.gamerpower.com/api-read#terms>`_ (read on
19 October 2026, check it for changes):

- The API is free for personal and commercial use, with no key.
- You must give attribution with an active hyperlink back to
  `GamerPower.com <https://www.gamerpower.com>`_.
- You may not claim the data as your own or sell it without permission.
- Do not exceed 10 requests per second. The client keeps well under that, see
  :doc:`guides/errors`.

In practice, wherever your application shows data from this library, show a link to
GamerPower.com next to it. :doc:`guides/discord-bot` shows one way to do it in an embed.

Library license
---------------

The code of this library is released under the MIT license, see the ``LICENSE`` file. The
license covers the code only. The data returned by the API stays under GamerPower's terms.
