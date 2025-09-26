from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ShowCellTagOwnerEvent(_message.Message):
    __slots__ = ("owner_id", "cell_id")
    OWNER_ID_FIELD_NUMBER: _ClassVar[int]
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    owner_id: int
    cell_id: int
    def __init__(self, owner_id: _Optional[int] = ..., cell_id: _Optional[int] = ...) -> None: ...

class ShowCellTagRequest(_message.Message):
    __slots__ = ("cell_id", "tag_type")
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    TAG_TYPE_FIELD_NUMBER: _ClassVar[int]
    cell_id: int
    tag_type: int
    def __init__(self, cell_id: _Optional[int] = ..., tag_type: _Optional[int] = ...) -> None: ...

class ShowCellTagsEvent(_message.Message):
    __slots__ = ("tag_type_by_entity_id", "tag_type_by_cell_id")
    class TagTypeByEntityIdEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    class TagTypeByCellIdEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    TAG_TYPE_BY_ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    TAG_TYPE_BY_CELL_ID_FIELD_NUMBER: _ClassVar[int]
    tag_type_by_entity_id: _containers.ScalarMap[int, int]
    tag_type_by_cell_id: _containers.ScalarMap[int, int]
    def __init__(self, tag_type_by_entity_id: _Optional[_Mapping[int, int]] = ..., tag_type_by_cell_id: _Optional[_Mapping[int, int]] = ...) -> None: ...

class UnknownFourHundredNineteen(_message.Message):
    __slots__ = ("unknown_seven_hundred_fifty_seven",)
    UNKNOWN_SEVEN_HUNDRED_FIFTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    unknown_seven_hundred_fifty_seven: int
    def __init__(self, unknown_seven_hundred_fifty_seven: _Optional[int] = ...) -> None: ...

class UnknownFourHundredTwenty(_message.Message):
    __slots__ = ("unknown_seven_hundred_fifty_eight",)
    UNKNOWN_SEVEN_HUNDRED_FIFTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    unknown_seven_hundred_fifty_eight: int
    def __init__(self, unknown_seven_hundred_fifty_eight: _Optional[int] = ...) -> None: ...
