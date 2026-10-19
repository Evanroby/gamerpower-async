import asyncio
import functools
import time

import httpx

from gamerpower import (
    GamerPower,
    GamerPowerError,
    GiveawayType,
    HTTPError,
    NotFound,
    Platform,
    SortBy,
)
from gamerpower.client import MIN_INTERVAL
from gamerpower.models import Giveaway, Worth, _date, _money


def sync(fn):
    @functools.wraps(fn)
    def run():
        asyncio.run(fn())

    return run


def item(id, worth="$9.99", users=10, end="2026-10-08 23:59:00"):
    return {
        "id": id,
        "title": f"game {id}",
        "worth": worth,
        "users": users,
        "published_date": "2026-10-01 10:00:00",
        "end_date": end,
        "platforms": "PC, Steam",
        "type": "Game",
        "status": "Active",
    }


def make(handler):
    return GamerPower(httpx.AsyncClient(transport=httpx.MockTransport(handler)))


def test_parsing():
    assert _money("$29.99") == 29.99
    assert _money("$1,234.50") == 1234.5
    assert _money("N/A") is None
    assert _date("N/A") is None
    assert _date("2026-10-08 23:59:00").day == 8
    g = Giveaway.from_dict(item(1, worth="N/A", end="N/A"))
    assert g.worth is None and g.end_date is None
    assert g.platforms == ("PC", "Steam")
    assert Worth.from_dict(
        {"active_giveaways_number": 3, "worth_estimation_usd": "12.50"}
    ) == Worth(3, 12.5)


def test_real_samples():
    # shapes copied from the live api on 2026-10-19
    g = Giveaway.from_dict(
        {
            "id": 3817,
            "title": "Agent A: A puzzle in disguise (Epic Games) Giveaway",
            "worth": "$19.99",
            "published_date": "2026-10-15 11:04:37",
            "type": "Game",
            "platforms": "PC, Android, iOS, Epic Games Store",
            "end_date": "2026-10-22 23:59:00",
            "users": 30590,
            "status": "Active",
        }
    )
    assert g.worth == 19.99 and g.end_date.hour == 23 and g.users == 30590
    assert g.platforms == ("PC", "Android", "iOS", "Epic Games Store")
    no_worth = {"id": 3792, "title": "Castlevania", "worth": "N/A", "end_date": "2026-10-24 23:59:00"}
    assert Giveaway.from_dict(no_worth).worth is None
    assert Worth.from_dict(
        {"active_giveaways_number": 107, "worth_estimation_usd": "538.77"}
    ) == Worth(107, 538.77)


@sync
async def test_single_filter_and_params():
    urls = []

    def handler(req):
        urls.append(req.url)
        return httpx.Response(200, json=[item(1), item(2)])

    async with make(handler) as gp:
        out = await gp.giveaways(Platform.STEAM, GiveawayType.LOOT, SortBy.VALUE)
    assert [g.id for g in out] == [1, 2]
    assert urls[0].path == "/api/giveaways"
    assert dict(urls[0].params) == {"platform": "steam", "type": "loot", "sort-by": "value"}


@sync
async def test_multi_uses_filter_and_sorts_here():
    urls = []

    def handler(req):
        urls.append(req.url)
        return httpx.Response(200, json=[item(1, worth="$5.00"), item(2, worth="$20.00")])

    async with make(handler) as gp:
        out = await gp.giveaways([Platform.EPIC_GAMES_STORE, Platform.STEAM], sort_by=SortBy.VALUE)
    assert [g.id for g in out] == [2, 1]
    assert urls[0].path == "/api/filter"
    assert "platform=epic-games-store+steam" in str(urls[0])


@sync
async def test_no_giveaways_is_empty_list():
    body = {"status": 0, "status_message": "No active giveaways available"}
    async with make(lambda req: httpx.Response(201, json=body)) as gp:
        assert await gp.giveaways() == []
        assert await gp.worth() == Worth(0, 0.0)


@sync
async def test_errors():
    async with make(lambda req: httpx.Response(404, json={"status": 0})) as gp:
        try:
            await gp.giveaway(999)
            raise AssertionError("expected NotFound")
        except NotFound:
            pass

    calls = []

    def bad_request(req):
        calls.append(1)
        return httpx.Response(400)

    async with make(bad_request) as gp:
        try:
            await gp.giveaways()
            raise AssertionError("expected HTTPError")
        except HTTPError as e:
            assert e.status == 400
    assert len(calls) == 1  # 4xx is not retried

    missing = {"status": 0, "status_message": "No giveaway found with that id"}
    async with make(lambda req: httpx.Response(200, json=missing)) as gp:
        assert await gp.giveaways() == []
        try:
            await gp.giveaway(9999)
            raise AssertionError("expected NotFound")
        except NotFound:
            pass

    async with make(lambda req: httpx.Response(200, json={"foo": 1})) as gp:
        try:
            await gp.giveaways()
            raise AssertionError("expected GamerPowerError")
        except GamerPowerError:
            pass


@sync
async def test_retry_on_server_error():
    calls = []

    def handler(req):
        calls.append(1)
        if len(calls) == 1:
            return httpx.Response(500)
        return httpx.Response(200, json=[item(1)])

    async with make(handler) as gp:
        out = await gp.giveaways()
    assert len(calls) == 2 and out[0].id == 1


@sync
async def test_throttle():
    async with make(lambda req: httpx.Response(200, json=[])) as gp:
        start = time.monotonic()
        await gp.giveaways()
        await gp.giveaways()
        assert time.monotonic() - start >= MIN_INTERVAL * 0.9


@sync
async def test_watch_primes_then_yields_new_only():
    polls = iter([[item(1), item(2)], [item(1), item(2), item(3)]])
    async with make(lambda req: httpx.Response(200, json=next(polls))) as gp:
        agen = gp.watch(interval=0)
        g = await asyncio.wait_for(anext(agen), 5)
        assert g.id == 3
        await agen.aclose()


@sync
async def test_watch_with_seen_set():
    seen = {1}
    async with make(lambda req: httpx.Response(200, json=[item(1), item(2)])) as gp:
        agen = gp.watch(interval=0, seen=seen)
        g = await asyncio.wait_for(anext(agen), 5)
        assert g.id == 2 and seen == {1, 2}
        await agen.aclose()


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
