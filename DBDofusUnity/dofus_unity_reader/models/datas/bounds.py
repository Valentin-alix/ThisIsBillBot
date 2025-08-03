from __future__ import annotations

from msgspec import Struct


class Bounds(Struct, frozen=True, kw_only=True):
    x: float
    y: float
    width: float
    height: float
