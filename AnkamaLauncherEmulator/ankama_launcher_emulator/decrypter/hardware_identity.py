import hashlib
import secrets


def generate_hardware_id() -> str:
    """Keep the SHA1 of a random MAC-like seed stable per account across sessions."""

    numeric_mac = "".join(str(secrets.randbelow(10)) for _ in range(12))
    hardware_id = hashlib.sha1(numeric_mac.encode("utf-8")).hexdigest()
    return hashlib.sha256(hardware_id.encode()).hexdigest().upper()
