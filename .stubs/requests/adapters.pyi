from urllib3 import Retry


class HTTPAdapter:
    def __init__(
        self,
        pool_connections: int = ...,
        pool_maxsize: int = ...,
        max_retries: Retry | int | None = ...,
        pool_block: bool = ...,
    ) -> None: ...
    def init_poolmanager(
        self, connections: int, maxsize: int, block: bool = False, **pool_kwargs: object
    ) -> None: ...
