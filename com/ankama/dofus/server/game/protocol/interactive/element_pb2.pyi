from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InteractiveUseRequest(_message.Message):
    __slots__ = ("element_id", "skill_instance_uid", "specific_instance_id")
    ELEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SKILL_INSTANCE_UID_FIELD_NUMBER: _ClassVar[int]
    SPECIFIC_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    element_id: int
    skill_instance_uid: int
    specific_instance_id: int
    def __init__(self, element_id: _Optional[int] = ..., skill_instance_uid: _Optional[int] = ..., specific_instance_id: _Optional[int] = ...) -> None: ...

class InteractiveUseErrorEvent(_message.Message):
    __slots__ = ("element_id", "skill_instance_uid")
    ELEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SKILL_INSTANCE_UID_FIELD_NUMBER: _ClassVar[int]
    element_id: int
    skill_instance_uid: int
    def __init__(self, element_id: _Optional[int] = ..., skill_instance_uid: _Optional[int] = ...) -> None: ...

class InteractiveUsedEvent(_message.Message):
    __slots__ = ("entity_id", "element_id", "skill_id", "duration", "can_move")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SKILL_ID_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    CAN_MOVE_FIELD_NUMBER: _ClassVar[int]
    entity_id: int
    element_id: int
    skill_id: int
    duration: int
    can_move: bool
    def __init__(self, entity_id: _Optional[int] = ..., element_id: _Optional[int] = ..., skill_id: _Optional[int] = ..., duration: _Optional[int] = ..., can_move: bool = ...) -> None: ...

class InteractiveUseEndedEvent(_message.Message):
    __slots__ = ("element_id", "skill_id")
    ELEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    SKILL_ID_FIELD_NUMBER: _ClassVar[int]
    element_id: int
    skill_id: int
    def __init__(self, element_id: _Optional[int] = ..., skill_id: _Optional[int] = ...) -> None: ...

class InteractiveMapUpdateEvent(_message.Message):
    __slots__ = ("interactive_elements",)
    INTERACTIVE_ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    interactive_elements: _containers.RepeatedCompositeFieldContainer[_common_pb2.InteractiveElement]
    def __init__(self, interactive_elements: _Optional[_Iterable[_Union[_common_pb2.InteractiveElement, _Mapping]]] = ...) -> None: ...

class StatedMapUpdateEvent(_message.Message):
    __slots__ = ("stated_elements",)
    STATED_ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    stated_elements: _containers.RepeatedCompositeFieldContainer[_common_pb2.StatedElement]
    def __init__(self, stated_elements: _Optional[_Iterable[_Union[_common_pb2.StatedElement, _Mapping]]] = ...) -> None: ...

class InteractiveElementUpdatedEvent(_message.Message):
    __slots__ = ("interactive_element",)
    INTERACTIVE_ELEMENT_FIELD_NUMBER: _ClassVar[int]
    interactive_element: _common_pb2.InteractiveElement
    def __init__(self, interactive_element: _Optional[_Union[_common_pb2.InteractiveElement, _Mapping]] = ...) -> None: ...

class StatedElementUpdatedEvent(_message.Message):
    __slots__ = ("stated_element",)
    STATED_ELEMENT_FIELD_NUMBER: _ClassVar[int]
    stated_element: _common_pb2.StatedElement
    def __init__(self, stated_element: _Optional[_Union[_common_pb2.StatedElement, _Mapping]] = ...) -> None: ...
