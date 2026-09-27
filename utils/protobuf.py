from typing import TYPE_CHECKING

from google.protobuf.descriptor import FieldDescriptor

if TYPE_CHECKING:
    from google._upb._message import FieldDescriptor as UpbFieldDescriptor


def is_repeated_field(field_descriptor: "FieldDescriptor | UpbFieldDescriptor") -> bool:
    return getattr(field_descriptor, "label") == FieldDescriptor.LABEL_REPEATED
