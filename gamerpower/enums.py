from enum import StrEnum


class Platform(StrEnum):
    """Platform slugs accepted by the API's ``platform`` filter.

    Members are strings, so ``Platform.STEAM == "steam"``. Anywhere a platform is accepted you
    can also pass a plain string, for example a slug the API added after this release.

    These slugs are not the labels found in :attr:`~gamerpower.Giveaway.platforms`
    (``"epic-games-store"`` here, ``"Epic Games Store"`` there).
    """

    PC = "pc"
    STEAM = "steam"
    EPIC_GAMES_STORE = "epic-games-store"
    GOG = "gog"
    PS4 = "ps4"
    PS5 = "ps5"
    XBOX_SERIES = "xbox-series-xs"
    XBOX_ONE = "xbox-one"
    SWITCH = "switch"
    ANDROID = "android"
    IOS = "ios"
    DRM_FREE = "drm-free"
    ITCHIO = "itchio"


class GiveawayType(StrEnum):
    """Giveaway types accepted by the API's ``type`` filter.

    The ``type`` field of a returned giveaway is a free-text label such as ``"Game"``, it is
    not one of these values.
    """

    GAME = "game"
    LOOT = "loot"
    BETA = "beta"


class SortBy(StrEnum):
    """Sort orders for :meth:`~gamerpower.GamerPower.giveaways`.

    ``DATE`` puts the newest first, ``VALUE`` the most valuable first and ``POPULARITY`` the
    most popular first.
    """

    DATE = "date"
    VALUE = "value"
    POPULARITY = "popularity"
