from pydantic import BaseModel, ConfigDict


class AppModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
