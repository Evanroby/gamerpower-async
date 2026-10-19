from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncIterator, Callable, Iterable
from datetime import datetime
from typing import Any

import httpx

from .enums import SortBy
from .errors import GamerPowerError, HTTPError, NotFound
from .models import Giveaway, Worth


BASE_URL = "https://www.gamerpower.com/api/"
MIN_INTERVAL = 0.15
RETRIES = 3

log = logging.getLogger(__name__)

_SORT_KEYS: dict[SortBy, Callable[[Giveaway], Any]] = {
    SortBy.DATE: lambda g: g.published_date or datetime.min,
    SortBy.VALUE: lambda g: g.worth or 0.0,
    SortBy.POPULARITY: lambda g: g.users,
}


def _join(value: str | Iterable[str] | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return str(value) or None
    return " ".join(str(v) for v in value) or None


def _shape(build: Callable[[Any], Any], data: Any) -> Any:
    try:
        return build(data)
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        raise GamerPowerError(f"unexpected response shape: {e!r}") from e


class GamerPower:
    """Async client for the GamerPower giveaways API.

    Use it as an async context manager so the HTTP session is closed for you::

        async with GamerPower() as gp:
            games = await gp.giveaways(Platform.STEAM)

    Requests made through one client are spaced at least 0.15 seconds apart, to stay under the
    API's limit of 10 requests per second. Failed requests are retried, see
    :doc:`/guides/errors`.

    Args:
        http: An ``httpx.AsyncClient`` to reuse. It is not closed by :meth:`close`. When
            omitted, the client creates its own (10 second timeout) and closes it.
    """

    def __init__(self, http: httpx.AsyncClient | None = None) -> None:
        self._own = http is None
        self._http = http or httpx.AsyncClient(
            timeout=10, headers={"User-Agent": "gamerpower-async/0.1"}
        )
        self._lock = asyncio.Lock()
        self._next = 0.0

    async def __aenter__(self) -> GamerPower:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the HTTP session, if this client created it.

        A session you passed in yourself is left open. Called for you when the client is used
        with ``async with``.
        """
        if self._own:
            await self._http.aclose()

    async def _throttle(self) -> None:
        async with self._lock:
            wait = self._next - time.monotonic()
            if wait > 0:
                await asyncio.sleep(wait)
            self._next = time.monotonic() + MIN_INTERVAL

    async def _get(self, path: str, params: dict[str, Any]) -> Any:
        params = {k: v for k, v in params.items() if v is not None}
        err: GamerPowerError
        for attempt in range(RETRIES):
            await self._throttle()
            try:
                r = await self._http.get(BASE_URL + path, params=params)
            except httpx.TransportError as e:
                err = GamerPowerError(f"request failed: {e!r}")
            else:
                if r.status_code == 201:
                    return None
                if r.status_code == 200:
                    try:
                        data = r.json()
                    except ValueError as e:
                        raise GamerPowerError("response is not json") from e
                    if isinstance(data, dict) and data.get("status") == 0:
                        return None
                    return data
                if r.status_code == 404:
                    raise NotFound(path)
                err = HTTPError(r.status_code)
                if r.status_code < 500 and r.status_code != 429:
                    raise err
            if attempt < RETRIES - 1:
                await asyncio.sleep(0.5 * 2**attempt)
        raise err

    async def giveaways(
        self,
        platform: str | Iterable[str] | None = None,
        type: str | Iterable[str] | None = None,
        sort_by: SortBy | str | None = None,
    ) -> list[Giveaway]:
        """Fetch the active giveaways, optionally filtered and sorted.

        With one platform and one type the filtering and sorting happen on the API's side.
        Several platforms or types are sent to the API's ``/filter`` endpoint, which has no sort
        option, so in that case the sorting is done by this library after the response arrives.
        Both ways give the same order.

        Args:
            platform: One platform or several, as :class:`~gamerpower.Platform` members or
                strings. ``None`` means every platform.
            type: One giveaway type or several, as :class:`~gamerpower.GiveawayType` members or
                strings. ``None`` means every type.
            sort_by: A :class:`~gamerpower.SortBy` member or its string value. ``None`` keeps the
                order chosen by the API.

        Returns:
            The matching giveaways. The list is empty when nothing matches, which is not an
            error.

        Raises:
            ValueError: If ``sort_by`` is not a valid sort order.
            GamerPowerError: If the request still fails after the retries, or the response does
                not have the expected shape.
        """
        platform, type = _join(platform), _join(type)
        sort = SortBy(sort_by) if sort_by else None
        params: dict[str, Any] = {"platform": platform, "type": type}
        multi = any(v and len(v.split()) > 1 for v in (platform, type))
        if multi:
            path = "filter"
        else:
            path = "giveaways"
            params["sort-by"] = str(sort) if sort else None

        data = await self._get(path, params)
        if data is None:
            return []
        items: list[Giveaway] = _shape(lambda d: [Giveaway.from_dict(x) for x in d], data)
        if multi and sort:
            items.sort(key=_SORT_KEYS[sort], reverse=True)
        return items

    async def giveaway(self, giveaway_id: int) -> Giveaway:
        """Fetch one giveaway by id.

        Args:
            giveaway_id: The giveaway's :attr:`~gamerpower.Giveaway.id`.

        Raises:
            NotFound: If no giveaway has that id.
            GamerPowerError: If the request fails after the retries, or the response does not
                have the expected shape.
        """
        data = await self._get("giveaway", {"id": giveaway_id})
        if data is None:
            raise NotFound(f"giveaway {giveaway_id}")
        return _shape(Giveaway.from_dict, data)

    async def worth(self, platform: str | None = None, type: str | None = None) -> Worth:
        """Fetch the number and combined value of the live giveaways.

        Args:
            platform: Only count giveaways on this platform.
            type: Only count giveaways of this type.

        Returns:
            A :class:`~gamerpower.Worth`. It is zero for both fields when nothing matches.

        Raises:
            GamerPowerError: If the request fails after the retries, or the response does not
                have the expected shape.
        """
        data = await self._get("worth", {"platform": _join(platform), "type": _join(type)})
        if data is None:
            return Worth(0, 0.0)
        return _shape(Worth.from_dict, data)

    async def watch(
        self,
        interval: float = 300,
        platform: str | Iterable[str] | None = None,
        type: str | Iterable[str] | None = None,
        seen: set[int] | None = None,
    ) -> AsyncIterator[Giveaway]:
        """Poll the API and yield each giveaway the first time it appears.

        This is an async generator, consume it with ``async for``. It never ends on its own:
        stop it by breaking out of the loop, calling ``aclose()`` on it, or cancelling the task
        that runs it.

        Giveaways are yielded oldest first. A failed poll is logged on the ``gamerpower`` logger
        and retried after ``interval`` seconds, it does not stop the generator.

        Without ``seen``, the first successful poll only records which giveaways already exist
        and yields nothing, so restarting a bot does not announce everything again. If you pass
        ``seen``, every giveaway whose id is not in it is yielded right away, including on the
        first poll. The set is updated in place (an id is added just before its giveaway is
        yielded), so you can use it to persist state. See :doc:`/guides/watching`.

        Args:
            interval: Seconds to wait between polls.
            platform: Same as in :meth:`giveaways`.
            type: Same as in :meth:`giveaways`.
            seen: Ids of giveaways to treat as already seen.

        Yields:
            Each new :class:`~gamerpower.Giveaway`.
        """
        prime = seen is None
        seen = set() if seen is None else seen
        while True:
            try:
                items = await self.giveaways(platform, type, SortBy.DATE)
            except GamerPowerError as e:
                # a bad poll must not kill the watcher
                log.warning("gamerpower poll failed: %s", e)
            else:
                for g in reversed(items):
                    if g.id not in seen:
                        seen.add(g.id)
                        if not prime:
                            yield g
                prime = False
            await asyncio.sleep(interval)
