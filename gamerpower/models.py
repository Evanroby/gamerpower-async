from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _money(value: Any) -> float | None:
    try:
        return float(str(value).replace("$", "").replace(",", ""))
    except ValueError:
        return None


def _date(value: Any) -> datetime | None:
    try:
        return datetime.strptime(str(value), DATE_FORMAT)
    except ValueError:
        return None


@dataclass(frozen=True, slots=True)
class Giveaway:
    """One giveaway, as returned by the API.

    Instances are immutable. Text fields the API leaves out are empty strings.

    Attributes:
        id (int): Unique giveaway id. Use it to tell giveaways apart.
        title (str): Title, for example ``"Bad Cheese (Epic Games) Giveaway"``.
        worth (float | None): Estimated value in US dollars, or ``None`` when the API
            reports ``"N/A"``.
        thumbnail (str): URL of a small image.
        image (str): URL of a larger image.
        description (str): Free text, may contain newlines.
        instructions (str): Steps to claim the giveaway, separated by ``"\\r\\n"``.
        open_giveaway_url (str): GamerPower link that redirects to the giveaway on the
            store. Use it for "claim" links.
        published_date (datetime | None): When GamerPower published it. Naive datetime,
            the API does not state a timezone.
        type (str): Display label such as ``"Game"``. This is not a
            :class:`~gamerpower.GiveawayType` value.
        platforms (tuple[str, ...]): Display labels such as ``("PC", "Steam")``. These are
            not :class:`~gamerpower.Platform` slugs.
        end_date (datetime | None): When the giveaway ends, or ``None`` when it has no end
            date. Naive datetime, like ``published_date``.
        users (int): Popularity counter reported by the API.
        status (str): Giveaway status, for example ``"Active"``.
        gamerpower_url (str): The giveaway's page on gamerpower.com.
        open_giveaway (str): Redirect link, identical to ``open_giveaway_url`` in every
            response seen so far.
    """

    id: int
    title: str
    worth: float | None
    thumbnail: str
    image: str
    description: str
    instructions: str
    open_giveaway_url: str
    published_date: datetime | None
    type: str
    platforms: tuple[str, ...]
    end_date: datetime | None
    users: int
    status: str
    gamerpower_url: str
    open_giveaway: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Giveaway:
        """Build a giveaway from one item of the API's JSON.

        Args:
            d: A decoded JSON object. ``id`` and ``title`` are required.

        Raises:
            KeyError: If ``id`` or ``title`` is missing.
            ValueError: If ``id`` or ``users`` is not a number.

        :class:`~gamerpower.GamerPower` wraps these errors in
        :class:`~gamerpower.GamerPowerError`, so you only meet them if you call this yourself.
        """

        def s(key: str) -> str:
            return d.get(key) or ""

        # id and title are required, a KeyError here means the shape changed
        return cls(
            id=int(d["id"]),
            title=d["title"],
            worth=_money(d.get("worth")),
            thumbnail=s("thumbnail"),
            image=s("image"),
            description=s("description"),
            instructions=s("instructions"),
            open_giveaway_url=s("open_giveaway_url"),
            published_date=_date(d.get("published_date")),
            type=s("type"),
            platforms=tuple(p.strip() for p in s("platforms").split(",") if p.strip()),
            end_date=_date(d.get("end_date")),
            users=int(d.get("users") or 0),
            status=s("status"),
            gamerpower_url=s("gamerpower_url"),
            open_giveaway=s("open_giveaway"),
        )


@dataclass(frozen=True, slots=True)
class Worth:
    """Number and combined value of the live giveaways.

    Attributes:
        active_giveaways (int): How many giveaways are active.
        worth_usd (float): Their estimated combined value in US dollars.
    """

    active_giveaways: int
    worth_usd: float

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Worth:
        """Build a :class:`Worth` from the JSON returned by the ``/worth`` endpoint.

        Args:
            d: A decoded JSON object with ``active_giveaways_number`` and
                ``worth_estimation_usd``.

        Raises:
            KeyError: If one of those keys is missing.
        """
        return cls(
            active_giveaways=int(d["active_giveaways_number"]),
            worth_usd=_money(d["worth_estimation_usd"]) or 0.0,
        )
