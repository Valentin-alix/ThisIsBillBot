import hashlib
import secrets


def generate_hardware_id() -> str:
    """Create the per-account HWID seed stored in bot config.

    Dofus starts from a MAC-like random value and stores its SHA1 as the
    account hardware identity. Keeping this value stable per account lets later
    connection code derive the same client identity across sessions.
    """

    numeric_mac = "".join(str(secrets.randbelow(10)) for _ in range(12))
    hardware_id = hashlib.sha1(numeric_mac.encode("utf-8")).hexdigest()
    return hashlib.sha256(hardware_id.encode()).hexdigest().upper()
