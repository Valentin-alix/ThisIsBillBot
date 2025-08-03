import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MountReleaseRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MountSterilizeRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MountToggleRidingRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MountRenameRequest(_message.Message):
    __slots__ = ("name", "mount_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    MOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    mount_id: int
    def __init__(self, name: _Optional[str] = ..., mount_id: _Optional[int] = ...) -> None: ...

class MountFeedRequest(_message.Message):
    __slots__ = ("mount_id", "mount_location", "mount_food_uid", "quantity")
    class MountLocation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        EQUIPPED: _ClassVar[MountFeedRequest.MountLocation]
        INVENTORY: _ClassVar[MountFeedRequest.MountLocation]
        STABLED: _ClassVar[MountFeedRequest.MountLocation]
        MAP: _ClassVar[MountFeedRequest.MountLocation]
    EQUIPPED: MountFeedRequest.MountLocation
    INVENTORY: MountFeedRequest.MountLocation
    STABLED: MountFeedRequest.MountLocation
    MAP: MountFeedRequest.MountLocation
    MOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    MOUNT_LOCATION_FIELD_NUMBER: _ClassVar[int]
    MOUNT_FOOD_UID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    mount_id: int
    mount_location: MountFeedRequest.MountLocation
    mount_food_uid: int
    quantity: int
    def __init__(self, mount_id: _Optional[int] = ..., mount_location: _Optional[_Union[MountFeedRequest.MountLocation, str]] = ..., mount_food_uid: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class MountSetXpRatioRequest(_message.Message):
    __slots__ = ("xp_ratio",)
    XP_RATIO_FIELD_NUMBER: _ClassVar[int]
    xp_ratio: int
    def __init__(self, xp_ratio: _Optional[int] = ...) -> None: ...

class MountInformationRequest(_message.Message):
    __slots__ = ("mount_id", "time")
    MOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    mount_id: int
    time: int
    def __init__(self, mount_id: _Optional[int] = ..., time: _Optional[int] = ...) -> None: ...

class MountInformationInPaddockRequest(_message.Message):
    __slots__ = ("mount_id",)
    MOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    mount_id: int
    def __init__(self, mount_id: _Optional[int] = ...) -> None: ...

class MountHarnessDissociateRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MountHarnessColorsUpdateRequest(_message.Message):
    __slots__ = ("use_harness_colors",)
    USE_HARNESS_COLORS_FIELD_NUMBER: _ClassVar[int]
    use_harness_colors: bool
    def __init__(self, use_harness_colors: bool = ...) -> None: ...

class MountSterilizedEvent(_message.Message):
    __slots__ = ("mount_id",)
    MOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    mount_id: int
    def __init__(self, mount_id: _Optional[int] = ...) -> None: ...

class MountReleasedEvent(_message.Message):
    __slots__ = ("mount_id",)
    MOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    mount_id: int
    def __init__(self, mount_id: _Optional[int] = ...) -> None: ...

class MountRenamedEvent(_message.Message):
    __slots__ = ("mount_id", "name")
    MOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    mount_id: int
    name: str
    def __init__(self, mount_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class MountRenamedErrorEvent(_message.Message):
    __slots__ = ("mount_id",)
    MOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    mount_id: int
    def __init__(self, mount_id: _Optional[int] = ...) -> None: ...

class MountXpRatioEvent(_message.Message):
    __slots__ = ("ratio",)
    RATIO_FIELD_NUMBER: _ClassVar[int]
    ratio: int
    def __init__(self, ratio: _Optional[int] = ...) -> None: ...

class MountDataEvent(_message.Message):
    __slots__ = ("mount_data",)
    MOUNT_DATA_FIELD_NUMBER: _ClassVar[int]
    mount_data: _common_pb2.MountData
    def __init__(self, mount_data: _Optional[_Union[_common_pb2.MountData, _Mapping]] = ...) -> None: ...

class MountDataErrorEvent(_message.Message):
    __slots__ = ("reason",)
    class MountDataError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[MountDataErrorEvent.MountDataError]
        NOT_FOUND: _ClassVar[MountDataErrorEvent.MountDataError]
        SOMEONE_ELSE_PRIVATE_FARM: _ClassVar[MountDataErrorEvent.MountDataError]
        SOMEONE_ELSE_MOUNT: _ClassVar[MountDataErrorEvent.MountDataError]
    UNKNOWN: MountDataErrorEvent.MountDataError
    NOT_FOUND: MountDataErrorEvent.MountDataError
    SOMEONE_ELSE_PRIVATE_FARM: MountDataErrorEvent.MountDataError
    SOMEONE_ELSE_MOUNT: MountDataErrorEvent.MountDataError
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: MountDataErrorEvent.MountDataError
    def __init__(self, reason: _Optional[_Union[MountDataErrorEvent.MountDataError, str]] = ...) -> None: ...

class MountEquippedEvent(_message.Message):
    __slots__ = ("mount_data",)
    MOUNT_DATA_FIELD_NUMBER: _ClassVar[int]
    mount_data: _common_pb2.MountData
    def __init__(self, mount_data: _Optional[_Union[_common_pb2.MountData, _Mapping]] = ...) -> None: ...

class MountUnequippedEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MountEquippedErrorEvent(_message.Message):
    __slots__ = ("error",)
    class MountEquippedError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNEQUIPPED: _ClassVar[MountEquippedErrorEvent.MountEquippedError]
        EQUIPPED: _ClassVar[MountEquippedErrorEvent.MountEquippedError]
        RIDING: _ClassVar[MountEquippedErrorEvent.MountEquippedError]
    UNEQUIPPED: MountEquippedErrorEvent.MountEquippedError
    EQUIPPED: MountEquippedErrorEvent.MountEquippedError
    RIDING: MountEquippedErrorEvent.MountEquippedError
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: MountEquippedErrorEvent.MountEquippedError
    def __init__(self, error: _Optional[_Union[MountEquippedErrorEvent.MountEquippedError, str]] = ...) -> None: ...

class MountRidingEvent(_message.Message):
    __slots__ = ("is_riding",)
    IS_RIDING_FIELD_NUMBER: _ClassVar[int]
    is_riding: bool
    def __init__(self, is_riding: bool = ...) -> None: ...

class MountEmoteIconUsedEvent(_message.Message):
    __slots__ = ("mount_id", "reaction")
    MOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    REACTION_FIELD_NUMBER: _ClassVar[int]
    mount_id: int
    reaction: int
    def __init__(self, mount_id: _Optional[int] = ..., reaction: _Optional[int] = ...) -> None: ...

class MountUpdateCharacteristicsEvent(_message.Message):
    __slots__ = ("ride_id", "updated_characteristics")
    class MountCharacteristicUpdate(_message.Message):
        __slots__ = ("characteristic", "int_value")
        CHARACTERISTIC_FIELD_NUMBER: _ClassVar[int]
        INT_VALUE_FIELD_NUMBER: _ClassVar[int]
        characteristic: _common_pb2.MountCharacteristic
        int_value: int
        def __init__(self, characteristic: _Optional[_Union[_common_pb2.MountCharacteristic, str]] = ..., int_value: _Optional[int] = ...) -> None: ...
    RIDE_ID_FIELD_NUMBER: _ClassVar[int]
    UPDATED_CHARACTERISTICS_FIELD_NUMBER: _ClassVar[int]
    ride_id: int
    updated_characteristics: _containers.RepeatedCompositeFieldContainer[MountUpdateCharacteristicsEvent.MountCharacteristicUpdate]
    def __init__(self, ride_id: _Optional[int] = ..., updated_characteristics: _Optional[_Iterable[_Union[MountUpdateCharacteristicsEvent.MountCharacteristicUpdate, _Mapping]]] = ...) -> None: ...

class DisplayNumericalValuePaddockEvent(_message.Message):
    __slots__ = ("mount_id", "value", "type")
    MOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    mount_id: int
    value: int
    type: _common_pb2.MountCharacteristic
    def __init__(self, mount_id: _Optional[int] = ..., value: _Optional[int] = ..., type: _Optional[_Union[_common_pb2.MountCharacteristic, str]] = ...) -> None: ...
