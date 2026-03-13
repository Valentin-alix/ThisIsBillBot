from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    access_token: str
    refresh_token: str
