import game_message_pb2 as _game_message_pb2
import report_pb2 as _report_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownJmv(_message.Message):
    __slots__ = ("unknown_fucy", "unknown_fucz")
    UNKNOWN_FUCY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUCZ_FIELD_NUMBER: _ClassVar[int]
    unknown_fucy: str
    unknown_fucz: bool
    def __init__(self, unknown_fucy: _Optional[str] = ..., unknown_fucz: bool = ...) -> None: ...

class UnknownJnc(_message.Message):
    __slots__ = ("unknown_fudx", "unknown_fudy")
    class UnknownJmz(_message.Message):
        __slots__ = ("unknown_fudo",)
        UNKNOWN_FUDO_FIELD_NUMBER: _ClassVar[int]
        unknown_fudo: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, unknown_fudo: _Optional[_Iterable[str]] = ...) -> None: ...
    UNKNOWN_FUDX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUDY_FIELD_NUMBER: _ClassVar[int]
    unknown_fudx: UnknownJnc.UnknownJmz
    unknown_fudy: int
    def __init__(self, unknown_fudx: _Optional[_Union[UnknownJnc.UnknownJmz, _Mapping]] = ..., unknown_fudy: _Optional[int] = ...) -> None: ...

class UnknownJnf(_message.Message):
    __slots__ = ("unknown_fuee", "unknown_fuef")
    UNKNOWN_FUEE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUEF_FIELD_NUMBER: _ClassVar[int]
    unknown_fuee: int
    unknown_fuef: str
    def __init__(self, unknown_fuee: _Optional[int] = ..., unknown_fuef: _Optional[str] = ...) -> None: ...

class UnknownJng(_message.Message):
    __slots__ = ("unknown_fuej",)
    UNKNOWN_FUEJ_FIELD_NUMBER: _ClassVar[int]
    unknown_fuej: UnknownJpn
    def __init__(self, unknown_fuej: _Optional[_Union[UnknownJpn, _Mapping]] = ...) -> None: ...

class UnknownJpn(_message.Message):
    __slots__ = ("unknown_fumn", "unknown_fumr", "unknown_fums")
    UNKNOWN_FUMN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUMR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUMS_FIELD_NUMBER: _ClassVar[int]
    unknown_fumn: _containers.RepeatedCompositeFieldContainer[UnknownJoa]
    unknown_fumr: UnknownJos
    unknown_fums: _containers.RepeatedCompositeFieldContainer[UnknownJoa]
    def __init__(self, unknown_fumn: _Optional[_Iterable[_Union[UnknownJoa, _Mapping]]] = ..., unknown_fumr: _Optional[_Union[UnknownJos, _Mapping]] = ..., unknown_fums: _Optional[_Iterable[_Union[UnknownJoa, _Mapping]]] = ...) -> None: ...

class UnknownJoa(_message.Message):
    __slots__ = ("unknown_fuhf", "unknown_fuhg", "unknown_fuhi", "unknown_fuhj", "unknown_fuhk", "unknown_fuhl", "unknown_fuhm")
    UNKNOWN_FUHF_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUHG_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUHI_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUHJ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUHK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUHL_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUHM_FIELD_NUMBER: _ClassVar[int]
    unknown_fuhf: int
    unknown_fuhg: str
    unknown_fuhi: int
    unknown_fuhj: int
    unknown_fuhk: str
    unknown_fuhl: int
    unknown_fuhm: str
    def __init__(self, unknown_fuhf: _Optional[int] = ..., unknown_fuhg: _Optional[str] = ..., unknown_fuhi: _Optional[int] = ..., unknown_fuhj: _Optional[int] = ..., unknown_fuhk: _Optional[str] = ..., unknown_fuhl: _Optional[int] = ..., unknown_fuhm: _Optional[str] = ...) -> None: ...

class UnknownJos(_message.Message):
    __slots__ = ("unknown_fujz", "unknown_fuka", "unknown_fukc", "unknown_fukd", "unknown_fuke", "unknown_fukf", "unknown_fukg", "unknown_fukh", "unknown_fuki", "unknown_fukj", "unknown_fukk", "unknown_fukl")
    UNKNOWN_FUJZ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUKA_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUKC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUKD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUKE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUKF_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUKG_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUKH_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUKI_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUKJ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUKK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUKL_FIELD_NUMBER: _ClassVar[int]
    unknown_fujz: int
    unknown_fuka: int
    unknown_fukc: int
    unknown_fukd: bool
    unknown_fuke: str
    unknown_fukf: _containers.RepeatedScalarFieldContainer[int]
    unknown_fukg: _containers.RepeatedScalarFieldContainer[int]
    unknown_fukh: str
    unknown_fuki: int
    unknown_fukj: UnknownJoa
    unknown_fukk: _containers.RepeatedCompositeFieldContainer[UnknownJoa]
    unknown_fukl: str
    def __init__(self, unknown_fujz: _Optional[int] = ..., unknown_fuka: _Optional[int] = ..., unknown_fukc: _Optional[int] = ..., unknown_fukd: bool = ..., unknown_fuke: _Optional[str] = ..., unknown_fukf: _Optional[_Iterable[int]] = ..., unknown_fukg: _Optional[_Iterable[int]] = ..., unknown_fukh: _Optional[str] = ..., unknown_fuki: _Optional[int] = ..., unknown_fukj: _Optional[_Union[UnknownJoa, _Mapping]] = ..., unknown_fukk: _Optional[_Iterable[_Union[UnknownJoa, _Mapping]]] = ..., unknown_fukl: _Optional[str] = ...) -> None: ...

class UnknownJnh(_message.Message):
    __slots__ = ("unknown_fueo",)
    UNKNOWN_FUEO_FIELD_NUMBER: _ClassVar[int]
    unknown_fueo: str
    def __init__(self, unknown_fueo: _Optional[str] = ...) -> None: ...

class UnknownJnk(_message.Message):
    __slots__ = ("unknown_fues",)
    UNKNOWN_FUES_FIELD_NUMBER: _ClassVar[int]
    unknown_fues: int
    def __init__(self, unknown_fues: _Optional[int] = ...) -> None: ...

class UnknownJnn(_message.Message):
    __slots__ = ("unknown_fuew",)
    UNKNOWN_FUEW_FIELD_NUMBER: _ClassVar[int]
    unknown_fuew: int
    def __init__(self, unknown_fuew: _Optional[int] = ...) -> None: ...

class UnknownJnr(_message.Message):
    __slots__ = ("unknown_fufh", "unknown_fufi")
    UNKNOWN_FUFH_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUFI_FIELD_NUMBER: _ClassVar[int]
    unknown_fufh: int
    unknown_fufi: str
    def __init__(self, unknown_fufh: _Optional[int] = ..., unknown_fufi: _Optional[str] = ...) -> None: ...

class UnknownJnt(_message.Message):
    __slots__ = ("unknown_fufq", "unknown_fufr", "unknown_fufs")
    UNKNOWN_FUFQ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUFR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUFS_FIELD_NUMBER: _ClassVar[int]
    unknown_fufq: str
    unknown_fufr: str
    unknown_fufs: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, unknown_fufq: _Optional[str] = ..., unknown_fufr: _Optional[str] = ..., unknown_fufs: _Optional[_Iterable[int]] = ...) -> None: ...

class LobbyCreateRequest(_message.Message):
    __slots__ = ("unknown_fufz", "unknown_fuga", "unknown_fugb", "unknown_fugc", "unknown_fugd", "unknown_fuge", "unknown_fugf", "unknown_fugg", "unknown_fugh")
    UNKNOWN_FUFZ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUGA_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUGB_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUGC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUGD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUGE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUGF_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUGG_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUGH_FIELD_NUMBER: _ClassVar[int]
    unknown_fufz: _containers.RepeatedScalarFieldContainer[int]
    unknown_fuga: bool
    unknown_fugb: int
    unknown_fugc: str
    unknown_fugd: int
    unknown_fuge: _containers.RepeatedScalarFieldContainer[int]
    unknown_fugf: int
    unknown_fugg: bool
    unknown_fugh: int
    def __init__(self, unknown_fufz: _Optional[_Iterable[int]] = ..., unknown_fuga: bool = ..., unknown_fugb: _Optional[int] = ..., unknown_fugc: _Optional[str] = ..., unknown_fugd: _Optional[int] = ..., unknown_fuge: _Optional[_Iterable[int]] = ..., unknown_fugf: _Optional[int] = ..., unknown_fugg: bool = ..., unknown_fugh: _Optional[int] = ...) -> None: ...

class UnknownJny(_message.Message):
    __slots__ = ("unknown_fugw",)
    UNKNOWN_FUGW_FIELD_NUMBER: _ClassVar[int]
    unknown_fugw: str
    def __init__(self, unknown_fugw: _Optional[str] = ...) -> None: ...

class UnknownJnz(_message.Message):
    __slots__ = ("unknown_fuhb",)
    UNKNOWN_FUHB_FIELD_NUMBER: _ClassVar[int]
    unknown_fuhb: str
    def __init__(self, unknown_fuhb: _Optional[str] = ...) -> None: ...

class UnknownJoc(_message.Message):
    __slots__ = ("unknown_fuhq",)
    UNKNOWN_FUHQ_FIELD_NUMBER: _ClassVar[int]
    unknown_fuhq: str
    def __init__(self, unknown_fuhq: _Optional[str] = ...) -> None: ...

class UnknownJof(_message.Message):
    __slots__ = ("unknown_fuhz",)
    UNKNOWN_FUHZ_FIELD_NUMBER: _ClassVar[int]
    unknown_fuhz: str
    def __init__(self, unknown_fuhz: _Optional[str] = ...) -> None: ...

class UnknownJog(_message.Message):
    __slots__ = ("unknown_fuid", "unknown_fuie")
    UNKNOWN_FUID_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUIE_FIELD_NUMBER: _ClassVar[int]
    unknown_fuid: str
    unknown_fuie: str
    def __init__(self, unknown_fuid: _Optional[str] = ..., unknown_fuie: _Optional[str] = ...) -> None: ...

class UnknownJoh(_message.Message):
    __slots__ = ("unknown_fuii",)
    UNKNOWN_FUII_FIELD_NUMBER: _ClassVar[int]
    unknown_fuii: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, unknown_fuii: _Optional[_Iterable[str]] = ...) -> None: ...

class UnknownJol(_message.Message):
    __slots__ = ("unknown_fuis",)
    UNKNOWN_FUIS_FIELD_NUMBER: _ClassVar[int]
    unknown_fuis: int
    def __init__(self, unknown_fuis: _Optional[int] = ...) -> None: ...

class UnknownJom(_message.Message):
    __slots__ = ("unknown_fuiw", "unknown_fuix")
    UNKNOWN_FUIW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUIX_FIELD_NUMBER: _ClassVar[int]
    unknown_fuiw: str
    unknown_fuix: bool
    def __init__(self, unknown_fuiw: _Optional[str] = ..., unknown_fuix: bool = ...) -> None: ...

class LobbyCreateResponse(_message.Message):
    __slots__ = ("unknown_fujm", "unknown_fujn")
    UNKNOWN_FUJM_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUJN_FIELD_NUMBER: _ClassVar[int]
    unknown_fujm: int
    unknown_fujn: str
    def __init__(self, unknown_fujm: _Optional[int] = ..., unknown_fujn: _Optional[str] = ...) -> None: ...

class UnknownJor(_message.Message):
    __slots__ = ("unknown_fujs", "unknown_fuju")
    UNKNOWN_FUJS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUJU_FIELD_NUMBER: _ClassVar[int]
    unknown_fujs: str
    unknown_fuju: str
    def __init__(self, unknown_fujs: _Optional[str] = ..., unknown_fuju: _Optional[str] = ...) -> None: ...

class UnknownJov(_message.Message):
    __slots__ = ("unknown_fuks", "unknown_fukt", "unknown_fuku")
    class UnknownFukuEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    UNKNOWN_FUKS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUKT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUKU_FIELD_NUMBER: _ClassVar[int]
    unknown_fuks: _containers.RepeatedScalarFieldContainer[int]
    unknown_fukt: str
    unknown_fuku: _containers.ScalarMap[str, str]
    def __init__(self, unknown_fuks: _Optional[_Iterable[int]] = ..., unknown_fukt: _Optional[str] = ..., unknown_fuku: _Optional[_Mapping[str, str]] = ...) -> None: ...

class UnknownJpb(_message.Message):
    __slots__ = ("unknown_fulk", "unknown_fulm")
    class UnknownJoy(_message.Message):
        __slots__ = ("unknown_fukz",)
        UNKNOWN_FUKZ_FIELD_NUMBER: _ClassVar[int]
        unknown_fukz: _containers.RepeatedCompositeFieldContainer[UnknownJpb.UnknownJoz]
        def __init__(self, unknown_fukz: _Optional[_Iterable[_Union[UnknownJpb.UnknownJoz, _Mapping]]] = ...) -> None: ...
    class UnknownJoz(_message.Message):
        __slots__ = ("unknown_fulf", "unknown_fulg")
        UNKNOWN_FULF_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FULG_FIELD_NUMBER: _ClassVar[int]
        unknown_fulf: bool
        unknown_fulg: str
        def __init__(self, unknown_fulf: bool = ..., unknown_fulg: _Optional[str] = ...) -> None: ...
    UNKNOWN_FULK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FULM_FIELD_NUMBER: _ClassVar[int]
    unknown_fulk: int
    unknown_fulm: UnknownJpb.UnknownJoy
    def __init__(self, unknown_fulk: _Optional[int] = ..., unknown_fulm: _Optional[_Union[UnknownJpb.UnknownJoy, _Mapping]] = ...) -> None: ...

class UnknownJpe(_message.Message):
    __slots__ = ("unknown_fulr",)
    UNKNOWN_FULR_FIELD_NUMBER: _ClassVar[int]
    unknown_fulr: int
    def __init__(self, unknown_fulr: _Optional[int] = ...) -> None: ...

class UnknownJpi(_message.Message):
    __slots__ = ("unknown_fuma",)
    UNKNOWN_FUMA_FIELD_NUMBER: _ClassVar[int]
    unknown_fuma: int
    def __init__(self, unknown_fuma: _Optional[int] = ...) -> None: ...

class UnknownJpj(_message.Message):
    __slots__ = ("unknown_fume",)
    UNKNOWN_FUME_FIELD_NUMBER: _ClassVar[int]
    unknown_fume: UnknownJoa
    def __init__(self, unknown_fume: _Optional[_Union[UnknownJoa, _Mapping]] = ...) -> None: ...

class UnknownJpk(_message.Message):
    __slots__ = ("unknown_fumi", "unknown_fumj")
    UNKNOWN_FUMI_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUMJ_FIELD_NUMBER: _ClassVar[int]
    unknown_fumi: UnknownJoa
    unknown_fumj: str
    def __init__(self, unknown_fumi: _Optional[_Union[UnknownJoa, _Mapping]] = ..., unknown_fumj: _Optional[str] = ...) -> None: ...

class UnknownJpq(_message.Message):
    __slots__ = ("unknown_fumw",)
    UNKNOWN_FUMW_FIELD_NUMBER: _ClassVar[int]
    unknown_fumw: UnknownJoa
    def __init__(self, unknown_fumw: _Optional[_Union[UnknownJoa, _Mapping]] = ...) -> None: ...

class UnknownJps(_message.Message):
    __slots__ = ("unknown_fung",)
    UNKNOWN_FUNG_FIELD_NUMBER: _ClassVar[int]
    unknown_fung: int
    def __init__(self, unknown_fung: _Optional[int] = ...) -> None: ...

class UnknownJpx(_message.Message):
    __slots__ = ("unknown_funp", "unknown_funq")
    class UnknownJpv(_message.Message):
        __slots__ = ("unknown_funk", "unknown_funl")
        UNKNOWN_FUNK_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FUNL_FIELD_NUMBER: _ClassVar[int]
        unknown_funk: _containers.RepeatedCompositeFieldContainer[UnknownJos]
        unknown_funl: _containers.RepeatedCompositeFieldContainer[UnknownJnf]
        def __init__(self, unknown_funk: _Optional[_Iterable[_Union[UnknownJos, _Mapping]]] = ..., unknown_funl: _Optional[_Iterable[_Union[UnknownJnf, _Mapping]]] = ...) -> None: ...
    UNKNOWN_FUNP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FUNQ_FIELD_NUMBER: _ClassVar[int]
    unknown_funp: UnknownJpx.UnknownJpv
    unknown_funq: int
    def __init__(self, unknown_funp: _Optional[_Union[UnknownJpx.UnknownJpv, _Mapping]] = ..., unknown_funq: _Optional[int] = ...) -> None: ...

class UnknownJpz(_message.Message):
    __slots__ = ("unknown_fuob",)
    UNKNOWN_FUOB_FIELD_NUMBER: _ClassVar[int]
    unknown_fuob: str
    def __init__(self, unknown_fuob: _Optional[str] = ...) -> None: ...

class UnknownJmu(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownJpr(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LobbyStopListeningRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LobbyStopListeningResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
