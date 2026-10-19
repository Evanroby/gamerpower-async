# gamerpower-async

[![Documentation](https://img.shields.io/readthedocs/gamerpower-async)](https://gamerpower-async.readthedocs.io/en/latest/) [![PyPI version](https://img.shields.io/pypi/v/mkdocs-badges)](https://pypi.org/project/gamerpower-async/)

Unofficial async Python wrapper for the [GamerPower API](https://www.gamerpower.com/api-read) (free games, in-game loot, beta keys).

You can find the official documentation for the API wraper [here](https://gamerpower-async.readthedocs.io/en/latest/).

Not affiliated with GamerPower. The API is free and needs no key. Their terms ask for an active hyperlink back to [GamerPower.com](https://www.gamerpower.com) wherever you show the data, and you may not sell the data or claim it as your own.

## Install

```bash
pip install gamerpower-async
```

Python 3.11+, the only dependency is `httpx`.

## Use

```python
import asyncio
from gamerpower import GamerPower, GiveawayType, Platform, SortBy


async def main():
    async with GamerPower() as gp:
        # one platform and type, sorted by the api
        for g in await gp.giveaways(Platform.STEAM, GiveawayType.GAME, SortBy.VALUE):
            print(g.title, g.worth, g.end_date, g.open_giveaway_url)

        # several platforms go through /filter, sorting is done client side
        await gp.giveaways([Platform.EPIC_GAMES_STORE, Platform.GOG], sort_by=SortBy.DATE)

        one = await gp.giveaway(525)  # raises NotFound
        total = await gp.worth()  # total.active_giveaways, total.worth_usd


asyncio.run(main())
```

### Watching for new giveaways

```python
async with GamerPower() as gp:
    async for g in gp.watch(interval=300, platform=Platform.EPIC_GAMES_STORE):
        print("new:", g.title)
```

Without `seen`, the first poll only records what already exists, so a restart does not repost everything. To survive restarts, load the ids you already posted from your database and pass them in. The set is updated as giveaways are yielded:

```python
seen = {1001, 1002}
async for g in gp.watch(seen=seen):
    ...
```

A failed poll is logged on the `gamerpower` logger and retried at the next interval.

## Behavior

- Requests are spaced at least 0.15s apart (the API asks for no more than 10 req/s).
- 429 and 5xx responses and network errors are retried 3 times with backoff. Other 4xx raise `HTTPError` right away.
- A 201 ("no active giveaways") returns an empty list.
- A 404 raises `NotFound`. A response that does not look like a giveaway raises `GamerPowerError`.
- Pass your own `httpx.AsyncClient` to `GamerPower(http=...)` to share a session. It is not closed for you.

## Known limits

- `end_date` and `published_date` are naive datetimes, the API does not document a timezone.
- `Giveaway.type` and `Giveaway.platforms` are the API's display labels (for example `"PC, Steam"` becomes `("PC", "Steam")`), not the filter slugs from `Platform`.

## Tests

```bash
python tests/test_gamerpower.py
```

No network needed, the client is tested against `httpx.MockTransport`.
