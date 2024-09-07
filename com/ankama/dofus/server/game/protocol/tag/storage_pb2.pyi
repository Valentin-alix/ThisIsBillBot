from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AddTagStorageRequest(_message.Message):
    __slots__ = ("name", "picto")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PICTO_FIELD_NUMBER: _ClassVar[int]
    name: str
    picto: int
    def __init__(self, name: _Optional[str] = ..., picto: _Optional[int] = ...) -> None: ...

class AddTagStorageResponse(_message.Message):
    __slots__ = ("tag_storage_uuid",)
    TAG_STORAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    tag_storage_uuid: str
    def __init__(self, tag_storage_uuid: _Optional[str] = ...) -> None: ...

class RemoveTagStorageRequest(_message.Message):
    __slots__ = ("tag_storage_uuid",)
    TAG_STORAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    tag_storage_uuid: str
    def __init__(self, tag_storage_uuid: _Optional[str] = ...) -> None: ...

class RemoveTagStorageResponse(_message.Message):
    __slots__ = ("tag_storage_uuid",)
    TAG_STORAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    tag_storage_uuid: str
    def __init__(self, tag_storage_uuid: _Optional[str] = ...) -> None: ...

class AddTagObjectRequest(_message.Message):
    __slots__ = ("tag_object_update_content",)
    TAG_OBJECT_UPDATE_CONTENT_FIELD_NUMBER: _ClassVar[int]
    tag_object_update_content: _containers.RepeatedCompositeFieldContainer[TagObjectUpdateContent]
    def __init__(self, tag_object_update_content: _Optional[_Iterable[_Union[TagObjectUpdateContent, _Mapping]]] = ...) -> None: ...

class AddTagObjectResponse(_message.Message):
    __slots__ = ("object_ids",)
    OBJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    object_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, object_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class RemoveTagObjectRequest(_message.Message):
    __slots__ = ("tag_object_update_content",)
    TAG_OBJECT_UPDATE_CONTENT_FIELD_NUMBER: _ClassVar[int]
    tag_object_update_content: _containers.RepeatedCompositeFieldContainer[TagObjectUpdateContent]
    def __init__(self, tag_object_update_content: _Optional[_Iterable[_Union[TagObjectUpdateContent, _Mapping]]] = ...) -> None: ...

class RemoveTagObjectResponse(_message.Message):
    __slots__ = ("object_ids",)
    OBJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    object_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, object_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class TagObjectUpdateContent(_message.Message):
    __slots__ = ("tag_storage_uuid", "object_id")
    TAG_STORAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    tag_storage_uuid: str
    object_id: int
    def __init__(self, tag_storage_uuid: _Optional[str] = ..., object_id: _Optional[int] = ...) -> None: ...

class UpdateTagStorageContentRequest(_message.Message):
    __slots__ = ("tag_storage_data",)
    TAG_STORAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    tag_storage_data: TagStorageData
    def __init__(self, tag_storage_data: _Optional[_Union[TagStorageData, _Mapping]] = ...) -> None: ...

class UpdateTagStorageContentResponse(_message.Message):
    __slots__ = ("tag_storage_uuid",)
    TAG_STORAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    tag_storage_uuid: str
    def __init__(self, tag_storage_uuid: _Optional[str] = ...) -> None: ...

class TagStoragesRefreshEvent(_message.Message):
    __slots__ = ("tag_information",)
    TAG_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    tag_information: _containers.RepeatedCompositeFieldContainer[TagInformation]
    def __init__(self, tag_information: _Optional[_Iterable[_Union[TagInformation, _Mapping]]] = ...) -> None: ...

class TagInformation(_message.Message):
    __slots__ = ("tag_storage_data", "tag_object_data")
    TAG_STORAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    TAG_OBJECT_DATA_FIELD_NUMBER: _ClassVar[int]
    tag_storage_data: TagStorageData
    tag_object_data: TagObjectData
    def __init__(self, tag_storage_data: _Optional[_Union[TagStorageData, _Mapping]] = ..., tag_object_data: _Optional[_Union[TagObjectData, _Mapping]] = ...) -> None: ...

class TagStorageData(_message.Message):
    __slots__ = ("tag_storage_uuid", "name", "picto")
    TAG_STORAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PICTO_FIELD_NUMBER: _ClassVar[int]
    tag_storage_uuid: str
    name: str
    picto: int
    def __init__(self, tag_storage_uuid: _Optional[str] = ..., name: _Optional[str] = ..., picto: _Optional[int] = ...) -> None: ...

class TagObjectData(_message.Message):
    __slots__ = ("tag_object_uuids",)
    TAG_OBJECT_UUIDS_FIELD_NUMBER: _ClassVar[int]
    tag_object_uuids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, tag_object_uuids: _Optional[_Iterable[int]] = ...) -> None: ...
