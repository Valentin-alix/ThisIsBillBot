"""Pydantic models for Ankama release/distribution metadata files."""

from pydantic import BaseModel, ConfigDict


class ReleaseJson(BaseModel):
    """Schema for the Ankama ``release.json`` files under ``ZAAP_PATH``.

    These files have many fields (``buildVersion``, ``arch``, ...) that we
    don't care about, hence ``extra="allow"`` — every consumer only reads
    ``location``, ``version``, or ``repositoryVersion``.
    """

    model_config = ConfigDict(extra="allow")

    location: str
    version: str | None = None
    repositoryVersion: str | None = None


class PackageJson(BaseModel):
    """Schema for the Ankama Launcher ``package.json`` inside ``app.asar``."""

    model_config = ConfigDict(extra="ignore")

    version: str
