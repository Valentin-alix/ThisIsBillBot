from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AnomalySubareaInformationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AnomalySubareaInformationEvent(_message.Message):
    __slots__ = ("subareas",)
    class AnomalySubareaInformation(_message.Message):
        __slots__ = ("subarea_id", "reward_rate", "has_anomaly", "anomaly_closing_time")
        SUBAREA_ID_FIELD_NUMBER: _ClassVar[int]
        REWARD_RATE_FIELD_NUMBER: _ClassVar[int]
        HAS_ANOMALY_FIELD_NUMBER: _ClassVar[int]
        ANOMALY_CLOSING_TIME_FIELD_NUMBER: _ClassVar[int]
        subarea_id: int
        reward_rate: int
        has_anomaly: bool
        anomaly_closing_time: int
        def __init__(self, subarea_id: _Optional[int] = ..., reward_rate: _Optional[int] = ..., has_anomaly: bool = ..., anomaly_closing_time: _Optional[int] = ...) -> None: ...
    SUBAREAS_FIELD_NUMBER: _ClassVar[int]
    subareas: _containers.RepeatedCompositeFieldContainer[AnomalySubareaInformationEvent.AnomalySubareaInformation]
    def __init__(self, subareas: _Optional[_Iterable[_Union[AnomalySubareaInformationEvent.AnomalySubareaInformation, _Mapping]]] = ...) -> None: ...

class AnomalyStateEvent(_message.Message):
    __slots__ = ("subarea_id", "open", "closing_time")
    SUBAREA_ID_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    CLOSING_TIME_FIELD_NUMBER: _ClassVar[int]
    subarea_id: int
    open: bool
    closing_time: int
    def __init__(self, subarea_id: _Optional[int] = ..., open: bool = ..., closing_time: _Optional[int] = ...) -> None: ...

class AnomalyOpenedEvent(_message.Message):
    __slots__ = ("subarea_id",)
    SUBAREA_ID_FIELD_NUMBER: _ClassVar[int]
    subarea_id: int
    def __init__(self, subarea_id: _Optional[int] = ...) -> None: ...
