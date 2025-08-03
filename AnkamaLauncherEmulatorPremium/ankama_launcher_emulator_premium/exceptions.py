import requests


class BannedException(Exception): ...


class ProxyRejectedError(Exception):
    """Ankama refused authentication because it rejects the outbound proxy."""


class HaapiHttpError(requests.exceptions.HTTPError):
    """A HAAPI call failed, keeping the status code reachable by callers."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code
