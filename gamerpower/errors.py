class GamerPowerError(Exception):
    """Base class for every error raised by this library."""


class NotFound(GamerPowerError):  # noqa: N818
    """The requested giveaway does not exist.

    Raised by :meth:`~gamerpower.GamerPower.giveaway` when the API answers 404 or replies with
    its error-style body (``{"status": 0, ...}``).
    """


class HTTPError(GamerPowerError):
    """The API answered with an HTTP status this library does not expect.

    Raised right away for client errors (4xx except 404), and after the retries are used up
    for 429 and 5xx responses.

    Attributes:
        status (int): The HTTP status code of the last response.
    """

    def __init__(self, status: int) -> None:
        super().__init__(f"unexpected http status {status}")
        self.status = status
