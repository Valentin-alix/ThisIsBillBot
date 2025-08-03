from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class ExcludedNonObfPackage(BaseModel):
    package: str = Field(min_length=1)
    """Lowercase namespace, e.g. `com.ankama.dofus.server.game.protocol.paddock`."""
    reason: str = Field(min_length=1)


class ExcludedNonObfConfig(BaseModel):
    """Packages kept out of matching because this build ships nothing they could pair with.

    The solver has to assign: a message with no real counterpart still takes the closest-looking
    obfuscated class, in whatever block that happens to be. Removing the `.proto` does not help,
    since the non-obfuscated dump.cs is what defines the message set. Listing the package here is
    the only way to stop it from holding a class that belongs to another protocol.
    """

    packages: list[ExcludedNonObfPackage] = Field(default_factory=list[ExcludedNonObfPackage])

    @model_validator(mode="after")
    def validate_unique_packages(self) -> ExcludedNonObfConfig:
        names = [entry.package.lower() for entry in self.packages]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate package in the non-obf exclusion list")
        return self

    @property
    def excluded_namespaces(self) -> frozenset[str]:
        return frozenset(entry.package.lower() for entry in self.packages)
