from __future__ import annotations

from functools import cached_property

from pydantic import BaseModel, Field


class PinnedPair(BaseModel):
    obf: str
    non_obf: str
    field_mapping_by_obf: dict[str, str] = Field(default_factory=dict[str, str])

    @cached_property
    def field_mapping_by_non_obf(self) -> dict[str, str]:
        return {non_obf: obf for obf, non_obf in self.field_mapping_by_obf.items()}


class PinnedPairsConfig(BaseModel):
    pairs: list[PinnedPair]

    @cached_property
    def pinned_pair_msg_by_non_obf(self) -> dict[str, PinnedPair]:
        return {pair.non_obf: pair for pair in self.pairs}

    @cached_property
    def pinned_pair_msg_by_obf(self) -> dict[str, PinnedPair]:
        return {pair.obf: pair for pair in self.pairs}
