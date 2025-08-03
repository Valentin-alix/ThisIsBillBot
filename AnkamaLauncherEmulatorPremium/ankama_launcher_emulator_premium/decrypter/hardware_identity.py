import hashlib
import re
import secrets
from dataclasses import dataclass

_HARDWARE_ID_PATTERN = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class HardwareIdentity:
    """Group the persisted per-account identity and the value sent to Ankama."""

    hardware_id: str
    connection_hwid: str


def generate_hardware_id() -> str:
    """Create the per-account HWID seed stored in bot config.

    Dofus starts from a MAC-like random value and stores its SHA1 as the
    account hardware identity. Keeping this value stable per account lets later
    connection code derive the same client identity across sessions.
    """

    numeric_mac = "".join(str(secrets.randbelow(10)) for _ in range(12))
    hardware_id = hashlib.sha1(numeric_mac.encode("utf-8")).hexdigest()
    return hashlib.sha256(_normalize_hardware_id(hardware_id).encode()).hexdigest().upper()


def _normalize_hardware_id(hardware_id: str) -> str:
    """Validate a persisted/manual HWID seed before trusting it.

    The bot config should contain the Dofus-style SHA1 seed, not the final
    connection HWID. Normalizing it avoids treating casing or whitespace as a
    different machine identity.
    """

    normalized = hardware_id.strip().lower()
    if not _HARDWARE_ID_PATTERN.fullmatch(normalized):
        raise ValueError("hardware_id must be a 40-character hexadecimal SHA1 string")
    return normalized


def derive_connection_hwid(hardware_id: str) -> str:
    """Convert the stored HWID seed into Dofus's connection identifier.

    Dofus sends SHA512(hardware_id).ToUpperInvariant() as the login
    device_identifier and uses the same value in the client verification
    challenge. This function produces that network-facing form without changing
    the persisted seed.
    """

    normalized = _normalize_hardware_id(hardware_id)
    return hashlib.sha512(normalized.encode("utf-8")).hexdigest().upper()


def build_hardware_identity(hardware_id: str) -> HardwareIdentity:
    """Build both HWID forms when code needs config and connection values.

    Use this at integration boundaries to keep the stored per-account seed and
    Dofus's network-facing HWID explicit instead of passing bare strings with
    ambiguous meaning.
    """

    normalized = _normalize_hardware_id(hardware_id)
    return HardwareIdentity(
        hardware_id=normalized,
        connection_hwid=derive_connection_hwid(normalized),
    )
