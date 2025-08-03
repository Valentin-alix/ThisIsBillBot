from collections.abc import Callable
from typing import Any

from pydantic import ConfigDict, validate_call


def strict_validate_call[F: Callable[..., Any]](func: F) -> F:
    return validate_call(config=ConfigDict(strict=True))(func)
