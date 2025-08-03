import common_pb2 as _common_pb2
import game_message_pb2 as _game_message_pb2
import report_pb2 as _report_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownKif(_message.Message):
    __slots__ = ("unknown_fxrd", "unknown_fxre", "unknown_fxrf", "unknown_fxrg")
    class UnknownKid(_message.Message):
        __slots__ = ("unknown_fxqw", "unknown_fxqx", "unknown_fxqy")
        UNKNOWN_FXQW_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FXQX_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FXQY_FIELD_NUMBER: _ClassVar[int]
        unknown_fxqw: int
        unknown_fxqx: int
        unknown_fxqy: int
        def __init__(self, unknown_fxqw: _Optional[int] = ..., unknown_fxqx: _Optional[int] = ..., unknown_fxqy: _Optional[int] = ...) -> None: ...
    UNKNOWN_FXRD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXRE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXRF_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXRG_FIELD_NUMBER: _ClassVar[int]
    unknown_fxrd: _containers.RepeatedCompositeFieldContainer[UnknownKif.UnknownKid]
    unknown_fxre: int
    unknown_fxrf: bool
    unknown_fxrg: int
    def __init__(self, unknown_fxrd: _Optional[_Iterable[_Union[UnknownKif.UnknownKid, _Mapping]]] = ..., unknown_fxre: _Optional[int] = ..., unknown_fxrf: bool = ..., unknown_fxrg: _Optional[int] = ...) -> None: ...

class UnknownKig(_message.Message):
    __slots__ = ("unknown_fxrl", "unknown_fxrm")
    UNKNOWN_FXRL_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXRM_FIELD_NUMBER: _ClassVar[int]
    unknown_fxrl: _containers.RepeatedScalarFieldContainer[bool]
    unknown_fxrm: int
    def __init__(self, unknown_fxrl: _Optional[_Iterable[bool]] = ..., unknown_fxrm: _Optional[int] = ...) -> None: ...

class UnknownKje(_message.Message):
    __slots__ = ("unknown_fxvf",)
    UNKNOWN_FXVF_FIELD_NUMBER: _ClassVar[int]
    unknown_fxvf: int
    def __init__(self, unknown_fxvf: _Optional[int] = ...) -> None: ...

class UnknownKjl(_message.Message):
    __slots__ = ("unknown_fxwc", "unknown_fxwd")
    class UnknownKji(_message.Message):
        __slots__ = ("unknown_fxvq",)
        UNKNOWN_FXVQ_FIELD_NUMBER: _ClassVar[int]
        unknown_fxvq: int
        def __init__(self, unknown_fxvq: _Optional[int] = ...) -> None: ...
    class UnknownKjj(_message.Message):
        __slots__ = ("unknown_fxvw",)
        UNKNOWN_FXVW_FIELD_NUMBER: _ClassVar[int]
        unknown_fxvw: bool
        def __init__(self, unknown_fxvw: bool = ...) -> None: ...
    UNKNOWN_FXWC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXWD_FIELD_NUMBER: _ClassVar[int]
    unknown_fxwc: UnknownKjl.UnknownKji
    unknown_fxwd: UnknownKjl.UnknownKjj
    def __init__(self, unknown_fxwc: _Optional[_Union[UnknownKjl.UnknownKji, _Mapping]] = ..., unknown_fxwd: _Optional[_Union[UnknownKjl.UnknownKjj, _Mapping]] = ...) -> None: ...

class UnknownKjs(_message.Message):
    __slots__ = ("unknown_fxws",)
    UNKNOWN_FXWS_FIELD_NUMBER: _ClassVar[int]
    unknown_fxws: bool
    def __init__(self, unknown_fxws: bool = ...) -> None: ...

class UnknownKjv(_message.Message):
    __slots__ = ("unknown_fxww",)
    UNKNOWN_FXWW_FIELD_NUMBER: _ClassVar[int]
    unknown_fxww: int
    def __init__(self, unknown_fxww: _Optional[int] = ...) -> None: ...

class GroupSearchStartRequest(_message.Message):
    __slots__ = ("unknown_fxxu", "unknown_fxxv", "unknown_fxxw")
    class UnknownKka(_message.Message):
        __slots__ = ("unknown_fxxh",)
        UNKNOWN_FXXH_FIELD_NUMBER: _ClassVar[int]
        unknown_fxxh: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, unknown_fxxh: _Optional[_Iterable[int]] = ...) -> None: ...
    class UnknownKkb(_message.Message):
        __slots__ = ("unknown_fxxl", "unknown_fxxm")
        UNKNOWN_FXXL_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FXXM_FIELD_NUMBER: _ClassVar[int]
        unknown_fxxl: str
        unknown_fxxm: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, unknown_fxxl: _Optional[str] = ..., unknown_fxxm: _Optional[_Iterable[int]] = ...) -> None: ...
    UNKNOWN_FXXU_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXXV_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXXW_FIELD_NUMBER: _ClassVar[int]
    unknown_fxxu: GroupSearchStartRequest.UnknownKka
    unknown_fxxv: GroupSearchStartRequest.UnknownKkb
    unknown_fxxw: int
    def __init__(self, unknown_fxxu: _Optional[_Union[GroupSearchStartRequest.UnknownKka, _Mapping]] = ..., unknown_fxxv: _Optional[_Union[GroupSearchStartRequest.UnknownKkb, _Mapping]] = ..., unknown_fxxw: _Optional[int] = ...) -> None: ...

class UnknownKkk(_message.Message):
    __slots__ = ("unknown_fxyp", "unknown_fxyr", "unknown_fxys", "unknown_fxyt")
    class UnknownKkg(_message.Message):
        __slots__ = ("unknown_fxyd",)
        UNKNOWN_FXYD_FIELD_NUMBER: _ClassVar[int]
        unknown_fxyd: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, unknown_fxyd: _Optional[_Iterable[int]] = ...) -> None: ...
    UNKNOWN_FXYP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXYR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXYS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXYT_FIELD_NUMBER: _ClassVar[int]
    unknown_fxyp: int
    unknown_fxyr: UnknownKkk.UnknownKkg
    unknown_fxys: int
    unknown_fxyt: int
    def __init__(self, unknown_fxyp: _Optional[int] = ..., unknown_fxyr: _Optional[_Union[UnknownKkk.UnknownKkg, _Mapping]] = ..., unknown_fxys: _Optional[int] = ..., unknown_fxyt: _Optional[int] = ...) -> None: ...

class UnknownKkq(_message.Message):
    __slots__ = ("unknown_fxzl",)
    UNKNOWN_FXZL_FIELD_NUMBER: _ClassVar[int]
    unknown_fxzl: int
    def __init__(self, unknown_fxzl: _Optional[int] = ...) -> None: ...

class UnknownKjx(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GroupSearchStartResponse(_message.Message):
    __slots__ = ("unknown_fxuy", "unknown_fxuz", "unknown_fxva")
    class UnknownKiv(_message.Message):
        __slots__ = ("unknown_fxtw",)
        UNKNOWN_FXTW_FIELD_NUMBER: _ClassVar[int]
        unknown_fxtw: int
        def __init__(self, unknown_fxtw: _Optional[int] = ...) -> None: ...
    class UnknownKiy(_message.Message):
        __slots__ = ("unknown_fxuo", "unknown_fxup")
        UNKNOWN_FXUO_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FXUP_FIELD_NUMBER: _ClassVar[int]
        unknown_fxuo: int
        unknown_fxup: int
        def __init__(self, unknown_fxuo: _Optional[int] = ..., unknown_fxup: _Optional[int] = ...) -> None: ...
    class UnknownKiz(_message.Message):
        __slots__ = ("unknown_fxuu",)
        UNKNOWN_FXUU_FIELD_NUMBER: _ClassVar[int]
        unknown_fxuu: int
        def __init__(self, unknown_fxuu: _Optional[int] = ...) -> None: ...
    UNKNOWN_FXUY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXUZ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXVA_FIELD_NUMBER: _ClassVar[int]
    unknown_fxuy: GroupSearchStartResponse.UnknownKiy
    unknown_fxuz: GroupSearchStartResponse.UnknownKiv
    unknown_fxva: GroupSearchStartResponse.UnknownKiz
    def __init__(self, unknown_fxuy: _Optional[_Union[GroupSearchStartResponse.UnknownKiy, _Mapping]] = ..., unknown_fxuz: _Optional[_Union[GroupSearchStartResponse.UnknownKiv, _Mapping]] = ..., unknown_fxva: _Optional[_Union[GroupSearchStartResponse.UnknownKiz, _Mapping]] = ...) -> None: ...

class UnknownKis(_message.Message):
    __slots__ = ("unknown_fxto", "unknown_fxtp", "unknown_fxtr", "unknown_fxts")
    class UnknownKip(_message.Message):
        __slots__ = ("unknown_fxsy", "unknown_fxsz")
        class UnknownKin(_message.Message):
            __slots__ = ("unknown_fxst",)
            UNKNOWN_FXST_FIELD_NUMBER: _ClassVar[int]
            unknown_fxst: str
            def __init__(self, unknown_fxst: _Optional[str] = ...) -> None: ...
        UNKNOWN_FXSY_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FXSZ_FIELD_NUMBER: _ClassVar[int]
        unknown_fxsy: _common_pb2.FightResultListEntry.FighterListEntry.PlayerListEntry.FightResultAdditionalData.PvpData
        unknown_fxsz: UnknownKis.UnknownKip.UnknownKin
        def __init__(self, unknown_fxsy: _Optional[_Union[_common_pb2.FightResultListEntry.FighterListEntry.PlayerListEntry.FightResultAdditionalData.PvpData, _Mapping]] = ..., unknown_fxsz: _Optional[_Union[UnknownKis.UnknownKip.UnknownKin, _Mapping]] = ...) -> None: ...
    class UnknownKiq(_message.Message):
        __slots__ = ("unknown_fxte", "unknown_fxtf", "unknown_fxth", "unknown_fxtj", "unknown_fxtk")
        UNKNOWN_FXTE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FXTF_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FXTH_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FXTJ_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FXTK_FIELD_NUMBER: _ClassVar[int]
        unknown_fxte: _containers.RepeatedScalarFieldContainer[int]
        unknown_fxtf: int
        unknown_fxth: int
        unknown_fxtj: int
        unknown_fxtk: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, unknown_fxte: _Optional[_Iterable[int]] = ..., unknown_fxtf: _Optional[int] = ..., unknown_fxth: _Optional[int] = ..., unknown_fxtj: _Optional[int] = ..., unknown_fxtk: _Optional[_Iterable[int]] = ...) -> None: ...
    UNKNOWN_FXTO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXTP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXTR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FXTS_FIELD_NUMBER: _ClassVar[int]
    unknown_fxto: _containers.RepeatedCompositeFieldContainer[UnknownKis.UnknownKip]
    unknown_fxtp: int
    unknown_fxtr: _containers.RepeatedCompositeFieldContainer[UnknownKis.UnknownKiq]
    unknown_fxts: int
    def __init__(self, unknown_fxto: _Optional[_Iterable[_Union[UnknownKis.UnknownKip, _Mapping]]] = ..., unknown_fxtp: _Optional[int] = ..., unknown_fxtr: _Optional[_Iterable[_Union[UnknownKis.UnknownKiq, _Mapping]]] = ..., unknown_fxts: _Optional[int] = ...) -> None: ...
