from __future__ import annotations


def encode_field_address(class_name: str, offset: int) -> str:
    """Encode a (class, field_offset) pair as a string for field_address tracking."""
    return f"{class_name}\x00{offset}"


def decode_field_address(encoded: str) -> tuple[str, int]:
    """Decode a field_address tracking string back to (class_name, field_offset)."""
    cls, off = encoded.split("\x00", 1)
    return cls, int(off)


def encode_object_offset(class_name: str, offset: int) -> str:
    """Encode a tracked object pointer after arithmetic displacement has been applied."""
    return f"{class_name}\x00{offset}"


def decode_object_offset(encoded: str) -> tuple[str, int]:
    """Decode object_offset tracking string back to (class_name, accumulated_offset)."""
    cls, off = encoded.split("\x00", 1)
    return cls, int(off)
