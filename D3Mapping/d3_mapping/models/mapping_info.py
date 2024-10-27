from typing import Mapping
from pydantic import BaseModel

from d3_mapping.utils import Percentage


class BaseMappingInfo(BaseModel):
    clear_msg_namespace: str
    similarity: Percentage


type FieldMapping = Mapping[str, tuple[float, str, MappingInfo | None] | None]


class MappingInfo(BaseModel):
    clear_msg_namespace: str
    similarity: Percentage
    field_mapping: FieldMapping


temp = {
    "exchange_positions": (
        0.8,
        "yhg",
        MappingInfo(
            clear_msg_namespace="ExchangePositions",
            similarity=0.8,
            field_mapping={
                "start_cell": (0.5, "kuu", None),
                "end_cell": (1, "kab", None),
            },
        ),
    )
}


game_action_fight_event: FieldMapping = {
    "exchange_positions": (
        0.8,
        "yhg",
        MappingInfo(
            clear_msg_namespace="GameActionFightEvent.ExchangePosition",
            similarity=1,
            field_mapping={"start_cell": (1, "jik", None)},
        ),
    ),
}

type OutputFieldMapping = Mapping[str, tuple[float, str] | None]


class OutputMappingInfo(BaseMappingInfo):
    field_mapping: OutputFieldMapping
