Changelog
=========

0.1.0 (unreleased)
------------------

First version.

- :class:`~gamerpower.GamerPower` client with :meth:`~gamerpower.GamerPower.giveaways`,
  :meth:`~gamerpower.GamerPower.giveaway` and :meth:`~gamerpower.GamerPower.worth`.
- :meth:`~gamerpower.GamerPower.watch` to stream new giveaways, with an optional ``seen`` set
  for persistence.
- Typed models (:class:`~gamerpower.Giveaway`, :class:`~gamerpower.Worth`) and enums for
  platforms, types and sort orders.
- Request spacing under the API's rate limit, and retries on network errors, 429 and 5xx.
