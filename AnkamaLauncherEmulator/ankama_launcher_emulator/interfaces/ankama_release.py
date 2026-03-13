from pydantic import BaseModel, ConfigDict


class ReleaseJson(BaseModel):
    model_config = ConfigDict(extra="allow")

    location: str
    version: str | None = None
    repositoryVersion: str | None = None


class PackageJson(BaseModel):
    model_config = ConfigDict(extra="ignore")

    version: str
