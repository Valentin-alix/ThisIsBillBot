from pydantic import ConfigDict

from src.utils.dataclass_utils import AppModel


class PEnumElement(AppModel):
    model_config = ConfigDict(frozen=True)

    name: str
    value: int

    def __hash__(self):
        return self.name.__hash__()


class PEnum(AppModel):
    model_config = ConfigDict(frozen=True)

    name: str
    namespace: str
    elements: list[PEnumElement]

    def __hash__(self):
        return self.name.__hash__()
