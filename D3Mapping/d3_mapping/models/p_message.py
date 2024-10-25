from dataclasses import dataclass

from proto_schema_parser.ast import FieldCardinality


@dataclass(frozen=True)
class PField:
    type_name: str
    name: str
    number: int
    cardinality: FieldCardinality | None = None

    def __hash__(self):
        return self.name.__hash__()


@dataclass(frozen=True)
class PMapField:
    name: str
    number: int
    key_type: str
    value_p_field: PField

    def __hash__(self) -> int:
        return self.name.__hash__()


@dataclass(frozen=True)
class POneOf:
    name: str
    elements: list[PField]

    def __hash__(self):
        return self.name.__hash__()


@dataclass(frozen=True)
class PMessage:
    name: str
    elements: list[POneOf | PField | PMapField]
    namespace: str

    def __hash__(self):
        return self.name.__hash__()
