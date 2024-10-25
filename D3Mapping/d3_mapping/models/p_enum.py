from dataclasses import dataclass


@dataclass(frozen=True)
class PEnumElement:
    name: str
    value: int

    def __hash__(self):
        return self.name.__hash__()


@dataclass(frozen=True)
class PEnum:
    name: str
    namespace: str
    elements: list[PEnumElement]

    def __hash__(self):
        return self.name.__hash__()
