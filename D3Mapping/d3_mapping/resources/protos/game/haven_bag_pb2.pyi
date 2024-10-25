import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HavenBagEnterRequest(_message.Message):
    __slots__ = ("owner",)
    OWNER_FIELD_NUMBER: _ClassVar[int]
    owner: int
    def __init__(self, owner: _Optional[int] = ...) -> None: ...

class HavenBagChangeRoomRequest(_message.Message):
    __slots__ = ("room_id",)
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    room_id: int
    def __init__(self, room_id: _Optional[int] = ...) -> None: ...

class HavenBagExitRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HavenBagEditRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HavenBagEditCancelRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HavenBagThemeChangeRequest(_message.Message):
    __slots__ = ("theme",)
    THEME_FIELD_NUMBER: _ClassVar[int]
    theme: int
    def __init__(self, theme: _Optional[int] = ...) -> None: ...

class HavenBagFurnitureOpenRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HavenBagFurnitureRequest(_message.Message):
    __slots__ = ("furniture",)
    FURNITURE_FIELD_NUMBER: _ClassVar[int]
    furniture: _containers.RepeatedCompositeFieldContainer[Element]
    def __init__(self, furniture: _Optional[_Iterable[_Union[Element, _Mapping]]] = ...) -> None: ...

class HavenBagFurnitureCloseRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HavenBagKickRequest(_message.Message):
    __slots__ = ("guest_id",)
    GUEST_ID_FIELD_NUMBER: _ClassVar[int]
    guest_id: int
    def __init__(self, guest_id: _Optional[int] = ...) -> None: ...

class HavenBagPermissionsUpdateRequest(_message.Message):
    __slots__ = ("permissions",)
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    permissions: int
    def __init__(self, permissions: _Optional[int] = ...) -> None: ...

class HavenBagInvitationAnswerRequest(_message.Message):
    __slots__ = ("accepted",)
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    def __init__(self, accepted: bool = ...) -> None: ...

class HavenBagInvitationRequest(_message.Message):
    __slots__ = ("guest_id",)
    GUEST_ID_FIELD_NUMBER: _ClassVar[int]
    guest_id: int
    def __init__(self, guest_id: _Optional[int] = ...) -> None: ...

class HavenBagRoomUpdateEvent(_message.Message):
    __slots__ = ("action", "preview")
    class HavenBagRoomAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        HAVEN_BAG_ROOM_DISPATCH: _ClassVar[HavenBagRoomUpdateEvent.HavenBagRoomAction]
        HAVEN_BAG_ROOM_UPDATE: _ClassVar[HavenBagRoomUpdateEvent.HavenBagRoomAction]
    HAVEN_BAG_ROOM_DISPATCH: HavenBagRoomUpdateEvent.HavenBagRoomAction
    HAVEN_BAG_ROOM_UPDATE: HavenBagRoomUpdateEvent.HavenBagRoomAction
    class HavenBagRoomPreview(_message.Message):
        __slots__ = ("room_id", "theme_id")
        ROOM_ID_FIELD_NUMBER: _ClassVar[int]
        THEME_ID_FIELD_NUMBER: _ClassVar[int]
        room_id: int
        theme_id: int
        def __init__(self, room_id: _Optional[int] = ..., theme_id: _Optional[int] = ...) -> None: ...
    ACTION_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    action: HavenBagRoomUpdateEvent.HavenBagRoomAction
    preview: _containers.RepeatedCompositeFieldContainer[HavenBagRoomUpdateEvent.HavenBagRoomPreview]
    def __init__(self, action: _Optional[_Union[HavenBagRoomUpdateEvent.HavenBagRoomAction, str]] = ..., preview: _Optional[_Iterable[_Union[HavenBagRoomUpdateEvent.HavenBagRoomPreview, _Mapping]]] = ...) -> None: ...

class HavenBagPackListEvent(_message.Message):
    __slots__ = ("packs_id",)
    PACKS_ID_FIELD_NUMBER: _ClassVar[int]
    packs_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, packs_id: _Optional[_Iterable[int]] = ...) -> None: ...

class HavenBagEditStartEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HavenBagEditFinishedEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HavenBagDailyLotteryEvent(_message.Message):
    __slots__ = ("result", "game_action_id")
    class DailyLotteryResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        HAVEN_BAG_DAILY_LOTTERY_OK: _ClassVar[HavenBagDailyLotteryEvent.DailyLotteryResult]
        HAVEN_BAG_DAILY_LOTTERY_ALREADY_USED: _ClassVar[HavenBagDailyLotteryEvent.DailyLotteryResult]
        HAVEN_BAG_DAILY_LOTTERY_ERROR: _ClassVar[HavenBagDailyLotteryEvent.DailyLotteryResult]
    HAVEN_BAG_DAILY_LOTTERY_OK: HavenBagDailyLotteryEvent.DailyLotteryResult
    HAVEN_BAG_DAILY_LOTTERY_ALREADY_USED: HavenBagDailyLotteryEvent.DailyLotteryResult
    HAVEN_BAG_DAILY_LOTTERY_ERROR: HavenBagDailyLotteryEvent.DailyLotteryResult
    RESULT_FIELD_NUMBER: _ClassVar[int]
    GAME_ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    result: HavenBagDailyLotteryEvent.DailyLotteryResult
    game_action_id: int
    def __init__(self, result: _Optional[_Union[HavenBagDailyLotteryEvent.DailyLotteryResult, str]] = ..., game_action_id: _Optional[int] = ...) -> None: ...

class HavenBagFurnitureEvent(_message.Message):
    __slots__ = ("furniture",)
    FURNITURE_FIELD_NUMBER: _ClassVar[int]
    furniture: _containers.RepeatedCompositeFieldContainer[Element]
    def __init__(self, furniture: _Optional[_Iterable[_Union[Element, _Mapping]]] = ...) -> None: ...

class HavenBagPermissionsUpdateEvent(_message.Message):
    __slots__ = ("permissions",)
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    permissions: int
    def __init__(self, permissions: _Optional[int] = ...) -> None: ...

class HavenBagInvitationClosedEvent(_message.Message):
    __slots__ = ("host_information",)
    HOST_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    host_information: _common_pb2.Character
    def __init__(self, host_information: _Optional[_Union[_common_pb2.Character, _Mapping]] = ...) -> None: ...

class HavenBagInvitationEvent(_message.Message):
    __slots__ = ("guest_information", "accepted")
    GUEST_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    guest_information: _common_pb2.Character
    accepted: bool
    def __init__(self, guest_information: _Optional[_Union[_common_pb2.Character, _Mapping]] = ..., accepted: bool = ...) -> None: ...

class HavenBagInvitationOfferedEvent(_message.Message):
    __slots__ = ("host_information", "time_before_cancel")
    HOST_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    TIME_BEFORE_CANCEL_FIELD_NUMBER: _ClassVar[int]
    host_information: _common_pb2.Character
    time_before_cancel: int
    def __init__(self, host_information: _Optional[_Union[_common_pb2.Character, _Mapping]] = ..., time_before_cancel: _Optional[int] = ...) -> None: ...

class Element(_message.Message):
    __slots__ = ("cell_id", "element_id", "orientation")
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    cell_id: int
    element_id: int
    orientation: int
    def __init__(self, cell_id: _Optional[int] = ..., element_id: _Optional[int] = ..., orientation: _Optional[int] = ...) -> None: ...
