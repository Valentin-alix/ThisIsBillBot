from pydantic import ConfigDict

from D3Mapping.d3_mapping.models.p_enum import PEnum
from D3Mapping.d3_mapping.models.p_message import PMessage
from src.utils.dataclass_utils import AppModel


class PFile(AppModel):
    model_config = ConfigDict(frozen=True)
    filename: str
    package: str | None
    imports: list[str]
    messages: list[PMessage]
    enums: list[PEnum]

    def __hash__(self):
        return self.filename.__hash__()
