from typing import Any, Callable

from pydantic import BaseModel


class ProtoFieldValidator(BaseModel):
    validators: list[Callable[[Any], bool]]
