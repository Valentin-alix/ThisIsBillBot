from proto_schema_parser.ast import FieldCardinality
from pydantic import ConfigDict

from src.utils.dataclass_utils import AppModel


class PField(AppModel):
    model_config = ConfigDict(frozen=True)
    type_name: str
    name: str
    number: int
    cardinality: FieldCardinality | None = None

    def __hash__(self):
        return self.name.__hash__()


class PMapField(AppModel):
    model_config = ConfigDict(frozen=True)

    name: str
    number: int
    key_type: str
    value_p_field: PField

    def __hash__(self) -> int:
        return self.name.__hash__()


class POneOf(AppModel):
    model_config = ConfigDict(frozen=True)

    name: str
    elements: list[PField]

    def __hash__(self):
        return self.name.__hash__()


class PMessage(AppModel):
    model_config = ConfigDict(frozen=True)

    name: str
    elements: list[POneOf | PField | PMapField]
    namespace: str

    def __hash__(self):
        return self.namespace.__hash__()
