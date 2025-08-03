import common_pb2 as _common_pb2
import game_message_pb2 as _game_message_pb2
import report_pb2 as _report_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownIxf(_message.Message):
    __slots__ = ("unknown_fruz", "unknown_fruy", "unknown_frva")
    class UnknownIxc(_message.Message):
        __slots__ = ("unknown_frum",)
        UNKNOWN_FRUM_FIELD_NUMBER: _ClassVar[int]
        unknown_frum: int
        def __init__(self, unknown_frum: _Optional[int] = ...) -> None: ...
    class UnknownIxd(_message.Message):
        __slots__ = ("unknown_fruq", "unknown_frus", "unknown_frut", "unknown_fruu")
        UNKNOWN_FRUQ_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRUS_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRUT_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRUU_FIELD_NUMBER: _ClassVar[int]
        unknown_fruq: str
        unknown_frus: bool
        unknown_frut: int
        unknown_fruu: int
        def __init__(self, unknown_fruq: _Optional[str] = ..., unknown_frus: bool = ..., unknown_frut: _Optional[int] = ..., unknown_fruu: _Optional[int] = ...) -> None: ...
    UNKNOWN_FRUZ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRUY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRVA_FIELD_NUMBER: _ClassVar[int]
    unknown_fruz: UnknownIxf.UnknownIxd
    unknown_fruy: UnknownIxf.UnknownIxc
    unknown_frva: UnknownIxf.UnknownIxc
    def __init__(self, unknown_fruz: _Optional[_Union[UnknownIxf.UnknownIxd, _Mapping]] = ..., unknown_fruy: _Optional[_Union[UnknownIxf.UnknownIxc, _Mapping]] = ..., unknown_frva: _Optional[_Union[UnknownIxf.UnknownIxc, _Mapping]] = ...) -> None: ...

class UnknownIxj(_message.Message):
    __slots__ = ("unknown_frvl", "unknown_frvp", "unknown_frvn", "unknown_frvo", "unknown_frvm", "unknown_frvq")
    class UnknownIxh(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_FRVL_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRVP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRVN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRVO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRVM_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRVQ_FIELD_NUMBER: _ClassVar[int]
    unknown_frvl: str
    unknown_frvp: int
    unknown_frvn: int
    unknown_frvo: int
    unknown_frvm: _common_pb2.Gender
    unknown_frvq: UnknownIxj.UnknownIxh
    def __init__(self, unknown_frvl: _Optional[str] = ..., unknown_frvp: _Optional[int] = ..., unknown_frvn: _Optional[int] = ..., unknown_frvo: _Optional[int] = ..., unknown_frvm: _Optional[_Union[_common_pb2.Gender, str]] = ..., unknown_frvq: _Optional[_Union[UnknownIxj.UnknownIxh, _Mapping]] = ...) -> None: ...

class UnknownIxn(_message.Message):
    __slots__ = ("unknown_frwn",)
    UNKNOWN_FRWN_FIELD_NUMBER: _ClassVar[int]
    unknown_frwn: str
    def __init__(self, unknown_frwn: _Optional[str] = ...) -> None: ...

class UnknownIya(_message.Message):
    __slots__ = ("unknown_frxx", "unknown_frxy", "unknown_frxz", "unknown_fryd", "unknown_frya", "unknown_fryb", "unknown_fryc", "unknown_fryh", "unknown_fryi", "unknown_fryj", "unknown_fryk", "unknown_frxw", "unknown_fryf", "unknown_fryg", "unknown_fryl", "unknown_frym", "unknown_fryn", "unknown_fryo")
    class UnknownIxw(_message.Message):
        __slots__ = ("unknown_frxd", "unknown_frxe", "unknown_frxf")
        UNKNOWN_FRXD_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRXE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRXF_FIELD_NUMBER: _ClassVar[int]
        unknown_frxd: _containers.RepeatedCompositeFieldContainer[UnknownIya.UnknownIxy]
        unknown_frxe: int
        unknown_frxf: int
        def __init__(self, unknown_frxd: _Optional[_Iterable[_Union[UnknownIya.UnknownIxy, _Mapping]]] = ..., unknown_frxe: _Optional[int] = ..., unknown_frxf: _Optional[int] = ...) -> None: ...
    class UnknownIxx(_message.Message):
        __slots__ = ("unknown_frxj", "unknown_frxk")
        UNKNOWN_FRXJ_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRXK_FIELD_NUMBER: _ClassVar[int]
        unknown_frxj: str
        unknown_frxk: int
        def __init__(self, unknown_frxj: _Optional[str] = ..., unknown_frxk: _Optional[int] = ...) -> None: ...
    class UnknownIxy(_message.Message):
        __slots__ = ("unknown_frxo", "unknown_frxs", "unknown_frxp", "unknown_frxr")
        UNKNOWN_FRXO_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRXS_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRXP_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRXR_FIELD_NUMBER: _ClassVar[int]
        unknown_frxo: UnknownIxj
        unknown_frxs: int
        unknown_frxp: str
        unknown_frxr: UnknownIxj
        def __init__(self, unknown_frxo: _Optional[_Union[UnknownIxj, _Mapping]] = ..., unknown_frxs: _Optional[int] = ..., unknown_frxp: _Optional[str] = ..., unknown_frxr: _Optional[_Union[UnknownIxj, _Mapping]] = ...) -> None: ...
    UNKNOWN_FRXX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRXY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRXZ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYA_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYB_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYH_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYI_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYJ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRXW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYF_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYG_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYL_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYM_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRYO_FIELD_NUMBER: _ClassVar[int]
    unknown_frxx: int
    unknown_frxy: int
    unknown_frxz: int
    unknown_fryd: int
    unknown_frya: str
    unknown_fryb: _containers.RepeatedCompositeFieldContainer[UnknownIyw]
    unknown_fryc: _containers.RepeatedCompositeFieldContainer[UnknownIzi]
    unknown_fryh: int
    unknown_fryi: int
    unknown_fryj: int
    unknown_fryk: int
    unknown_frxw: int
    unknown_fryf: bool
    unknown_fryg: int
    unknown_fryl: int
    unknown_frym: UnknownIxj
    unknown_fryn: UnknownIya.UnknownIxw
    unknown_fryo: UnknownIya.UnknownIxx
    def __init__(self, unknown_frxx: _Optional[int] = ..., unknown_frxy: _Optional[int] = ..., unknown_frxz: _Optional[int] = ..., unknown_fryd: _Optional[int] = ..., unknown_frya: _Optional[str] = ..., unknown_fryb: _Optional[_Iterable[_Union[UnknownIyw, _Mapping]]] = ..., unknown_fryc: _Optional[_Iterable[_Union[UnknownIzi, _Mapping]]] = ..., unknown_fryh: _Optional[int] = ..., unknown_fryi: _Optional[int] = ..., unknown_fryj: _Optional[int] = ..., unknown_fryk: _Optional[int] = ..., unknown_frxw: _Optional[int] = ..., unknown_fryf: bool = ..., unknown_fryg: _Optional[int] = ..., unknown_fryl: _Optional[int] = ..., unknown_frym: _Optional[_Union[UnknownIxj, _Mapping]] = ..., unknown_fryn: _Optional[_Union[UnknownIya.UnknownIxw, _Mapping]] = ..., unknown_fryo: _Optional[_Union[UnknownIya.UnknownIxx, _Mapping]] = ...) -> None: ...

class UnknownIyw(_message.Message):
    __slots__ = ("unknown_fsbn", "unknown_fsbo", "unknown_fsbp", "unknown_fsbq")
    class UnknownFsbnEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class UnknownFsbqEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_FSBN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSBO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSBP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSBQ_FIELD_NUMBER: _ClassVar[int]
    unknown_fsbn: _containers.ScalarMap[str, int]
    unknown_fsbo: int
    unknown_fsbp: _containers.RepeatedScalarFieldContainer[str]
    unknown_fsbq: _containers.ScalarMap[str, int]
    def __init__(self, unknown_fsbn: _Optional[_Mapping[str, int]] = ..., unknown_fsbo: _Optional[int] = ..., unknown_fsbp: _Optional[_Iterable[str]] = ..., unknown_fsbq: _Optional[_Mapping[str, int]] = ...) -> None: ...

class UnknownIzi(_message.Message):
    __slots__ = ("unknown_fsef", "unknown_fseg", "unknown_fseh")
    UNKNOWN_FSEF_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSEG_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSEH_FIELD_NUMBER: _ClassVar[int]
    unknown_fsef: _common_pb2.ObjectEffect
    unknown_fseg: int
    unknown_fseh: int
    def __init__(self, unknown_fsef: _Optional[_Union[_common_pb2.ObjectEffect, _Mapping]] = ..., unknown_fseg: _Optional[int] = ..., unknown_fseh: _Optional[int] = ...) -> None: ...

class UnknownIyj(_message.Message):
    __slots__ = ("unknown_fsab",)
    class UnknownIyh(_message.Message):
        __slots__ = ("unknown_frzf", "unknown_frzg", "unknown_frzh", "unknown_frzi", "unknown_frzj", "unknown_frzm", "unknown_frzn", "unknown_frzp", "unknown_frzq", "unknown_frzt", "unknown_frzu", "unknown_frzr", "unknown_frzv", "unknown_frzw", "unknown_frzx")
        UNKNOWN_FRZF_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZG_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZH_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZI_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZJ_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZM_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZP_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZQ_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZT_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZU_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZR_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZV_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZW_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FRZX_FIELD_NUMBER: _ClassVar[int]
        unknown_frzf: int
        unknown_frzg: int
        unknown_frzh: str
        unknown_frzi: int
        unknown_frzj: str
        unknown_frzm: _containers.RepeatedCompositeFieldContainer[UnknownIzi]
        unknown_frzn: int
        unknown_frzp: int
        unknown_frzq: bool
        unknown_frzt: int
        unknown_frzu: bool
        unknown_frzr: int
        unknown_frzv: bool
        unknown_frzw: str
        unknown_frzx: _containers.RepeatedCompositeFieldContainer[UnknownIyw]
        def __init__(self, unknown_frzf: _Optional[int] = ..., unknown_frzg: _Optional[int] = ..., unknown_frzh: _Optional[str] = ..., unknown_frzi: _Optional[int] = ..., unknown_frzj: _Optional[str] = ..., unknown_frzm: _Optional[_Iterable[_Union[UnknownIzi, _Mapping]]] = ..., unknown_frzn: _Optional[int] = ..., unknown_frzp: _Optional[int] = ..., unknown_frzq: bool = ..., unknown_frzt: _Optional[int] = ..., unknown_frzu: bool = ..., unknown_frzr: _Optional[int] = ..., unknown_frzv: bool = ..., unknown_frzw: _Optional[str] = ..., unknown_frzx: _Optional[_Iterable[_Union[UnknownIyw, _Mapping]]] = ...) -> None: ...
    UNKNOWN_FSAB_FIELD_NUMBER: _ClassVar[int]
    unknown_fsab: UnknownIyj.UnknownIyh
    def __init__(self, unknown_fsab: _Optional[_Union[UnknownIyj.UnknownIyh, _Mapping]] = ...) -> None: ...

class UnknownIzm(_message.Message):
    __slots__ = ("unknown_fsfb", "unknown_fsfc", "unknown_fsfd", "unknown_fsff", "unknown_fsfe")
    class UnknownIzk(_message.Message):
        __slots__ = ("unknown_fseq", "unknown_fser", "unknown_fses", "unknown_fset", "unknown_fseu", "unknown_fsev", "unknown_fsew", "unknown_fsex")
        class UnknownFseqEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: int
            def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
        class UnknownFsesEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: bool
            value: str
            def __init__(self, key: bool = ..., value: _Optional[str] = ...) -> None: ...
        UNKNOWN_FSEQ_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FSER_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FSES_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FSET_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FSEU_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FSEV_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FSEW_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FSEX_FIELD_NUMBER: _ClassVar[int]
        unknown_fseq: _containers.ScalarMap[int, int]
        unknown_fser: _containers.RepeatedScalarFieldContainer[int]
        unknown_fses: _containers.ScalarMap[bool, str]
        unknown_fset: _containers.RepeatedScalarFieldContainer[int]
        unknown_fseu: _containers.RepeatedScalarFieldContainer[str]
        unknown_fsev: _containers.RepeatedScalarFieldContainer[str]
        unknown_fsew: str
        unknown_fsex: bool
        def __init__(self, unknown_fseq: _Optional[_Mapping[int, int]] = ..., unknown_fser: _Optional[_Iterable[int]] = ..., unknown_fses: _Optional[_Mapping[bool, str]] = ..., unknown_fset: _Optional[_Iterable[int]] = ..., unknown_fseu: _Optional[_Iterable[str]] = ..., unknown_fsev: _Optional[_Iterable[str]] = ..., unknown_fsew: _Optional[str] = ..., unknown_fsex: bool = ...) -> None: ...
    UNKNOWN_FSFB_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSFC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSFD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSFF_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSFE_FIELD_NUMBER: _ClassVar[int]
    unknown_fsfb: str
    unknown_fsfc: int
    unknown_fsfd: int
    unknown_fsff: float
    unknown_fsfe: UnknownIzm.UnknownIzk
    def __init__(self, unknown_fsfb: _Optional[str] = ..., unknown_fsfc: _Optional[int] = ..., unknown_fsfd: _Optional[int] = ..., unknown_fsff: _Optional[float] = ..., unknown_fsfe: _Optional[_Union[UnknownIzm.UnknownIzk, _Mapping]] = ...) -> None: ...

class InfiniteDreamEnterRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownIww(_message.Message):
    __slots__ = ("unknown_frtn", "unknown_frtp", "unknown_frtr", "unknown_frts", "unknown_frtu", "unknown_frtw", "unknown_frty", "unknown_frua", "unknown_frub", "unknown_fruc")
    class UnknownFrtwEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_FRTN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRTP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRTR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRTS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRTU_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRTW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRTY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRUA_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRUB_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FRUC_FIELD_NUMBER: _ClassVar[int]
    unknown_frtn: int
    unknown_frtp: int
    unknown_frtr: _containers.RepeatedCompositeFieldContainer[UnknownIzi]
    unknown_frts: int
    unknown_frtu: int
    unknown_frtw: _containers.ScalarMap[int, int]
    unknown_frty: int
    unknown_frua: int
    unknown_frub: int
    unknown_fruc: bool
    def __init__(self, unknown_frtn: _Optional[int] = ..., unknown_frtp: _Optional[int] = ..., unknown_frtr: _Optional[_Iterable[_Union[UnknownIzi, _Mapping]]] = ..., unknown_frts: _Optional[int] = ..., unknown_frtu: _Optional[int] = ..., unknown_frtw: _Optional[_Mapping[int, int]] = ..., unknown_frty: _Optional[int] = ..., unknown_frua: _Optional[int] = ..., unknown_frub: _Optional[int] = ..., unknown_fruc: bool = ...) -> None: ...

class InfiniteDreamEnterResponse(_message.Message):
    __slots__ = ("unknown_fsda", "unknown_fsdc", "unknown_fsdd", "unknown_fsde", "unknown_fsdf", "unknown_fsdg", "unknown_fsdh", "unknown_fsdi", "unknown_fsdk", "unknown_fsdm", "unknown_fsdn", "unknown_fsdo", "unknown_fsdp", "unknown_fsdq", "unknown_fsdr", "unknown_fsds", "unknown_fsdt", "unknown_fsdu", "unknown_fsdv", "unknown_fsdw", "unknown_fsdx", "unknown_fsdy")
    class UnknownIze(_message.Message):
        __slots__ = ("unknown_fscs", "unknown_fscu", "unknown_fscv", "unknown_fscw")
        class UnknownFscwEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: int
            def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
        UNKNOWN_FSCS_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FSCU_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FSCV_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FSCW_FIELD_NUMBER: _ClassVar[int]
        unknown_fscs: int
        unknown_fscu: int
        unknown_fscv: int
        unknown_fscw: _containers.ScalarMap[int, int]
        def __init__(self, unknown_fscs: _Optional[int] = ..., unknown_fscu: _Optional[int] = ..., unknown_fscv: _Optional[int] = ..., unknown_fscw: _Optional[_Mapping[int, int]] = ...) -> None: ...
    class UnknownIzd(_message.Message):
        __slots__ = ("unknown_fsck", "unknown_fscn", "unknown_fsco", "unknown_fscm")
        class UnknownFscnValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_FSCN_VALUE_UNSPECIFIED: _ClassVar[InfiniteDreamEnterResponse.UnknownIzd.UnknownFscnValue]
        UNKNOWN_FSCN_VALUE_UNSPECIFIED: InfiniteDreamEnterResponse.UnknownIzd.UnknownFscnValue
        class UnknownFscoValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_FSCO_VALUE_UNSPECIFIED: _ClassVar[InfiniteDreamEnterResponse.UnknownIzd.UnknownFscoValue]
        UNKNOWN_FSCO_VALUE_UNSPECIFIED: InfiniteDreamEnterResponse.UnknownIzd.UnknownFscoValue
        class UnknownIzb(_message.Message):
            __slots__ = ("unknown_fsbx", "unknown_fsbz", "unknown_fsca", "unknown_fscb", "unknown_fscd", "unknown_fsce", "unknown_fscf", "unknown_fscg")
            class UnknownFscaEntry(_message.Message):
                __slots__ = ("key", "value")
                KEY_FIELD_NUMBER: _ClassVar[int]
                VALUE_FIELD_NUMBER: _ClassVar[int]
                key: int
                value: bool
                def __init__(self, key: _Optional[int] = ..., value: bool = ...) -> None: ...
            UNKNOWN_FSBX_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FSBZ_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FSCA_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FSCB_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FSCD_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FSCE_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FSCF_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FSCG_FIELD_NUMBER: _ClassVar[int]
            unknown_fsbx: int
            unknown_fsbz: _containers.RepeatedScalarFieldContainer[int]
            unknown_fsca: _containers.ScalarMap[int, bool]
            unknown_fscb: int
            unknown_fscd: str
            unknown_fsce: _containers.RepeatedScalarFieldContainer[int]
            unknown_fscf: int
            unknown_fscg: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, unknown_fsbx: _Optional[int] = ..., unknown_fsbz: _Optional[_Iterable[int]] = ..., unknown_fsca: _Optional[_Mapping[int, bool]] = ..., unknown_fscb: _Optional[int] = ..., unknown_fscd: _Optional[str] = ..., unknown_fsce: _Optional[_Iterable[int]] = ..., unknown_fscf: _Optional[int] = ..., unknown_fscg: _Optional[_Iterable[int]] = ...) -> None: ...
        UNKNOWN_FSCK_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FSCN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FSCO_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FSCM_FIELD_NUMBER: _ClassVar[int]
        unknown_fsck: str
        unknown_fscn: InfiniteDreamEnterResponse.UnknownIzd.UnknownFscnValue
        unknown_fsco: InfiniteDreamEnterResponse.UnknownIzd.UnknownFscoValue
        unknown_fscm: InfiniteDreamEnterResponse.UnknownIzd.UnknownIzb
        def __init__(self, unknown_fsck: _Optional[str] = ..., unknown_fscn: _Optional[_Union[InfiniteDreamEnterResponse.UnknownIzd.UnknownFscnValue, str]] = ..., unknown_fsco: _Optional[_Union[InfiniteDreamEnterResponse.UnknownIzd.UnknownFscoValue, str]] = ..., unknown_fscm: _Optional[_Union[InfiniteDreamEnterResponse.UnknownIzd.UnknownIzb, _Mapping]] = ...) -> None: ...
    UNKNOWN_FSDA_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDF_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDG_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDH_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDI_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDM_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDQ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDU_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDV_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSDY_FIELD_NUMBER: _ClassVar[int]
    unknown_fsda: UnknownIxj
    unknown_fsdc: _containers.RepeatedCompositeFieldContainer[InfiniteDreamEnterResponse.UnknownIze]
    unknown_fsdd: _containers.RepeatedCompositeFieldContainer[InfiniteDreamEnterResponse.UnknownIzd]
    unknown_fsde: _containers.RepeatedCompositeFieldContainer[UnknownIxj]
    unknown_fsdf: _containers.RepeatedCompositeFieldContainer[UnknownIww]
    unknown_fsdg: int
    unknown_fsdh: int
    unknown_fsdi: str
    unknown_fsdk: int
    unknown_fsdm: int
    unknown_fsdn: int
    unknown_fsdo: str
    unknown_fsdp: int
    unknown_fsdq: _containers.RepeatedCompositeFieldContainer[UnknownIzi]
    unknown_fsdr: _containers.RepeatedCompositeFieldContainer[UnknownIyw]
    unknown_fsds: int
    unknown_fsdt: bool
    unknown_fsdu: bool
    unknown_fsdv: int
    unknown_fsdw: bool
    unknown_fsdx: int
    unknown_fsdy: bool
    def __init__(self, unknown_fsda: _Optional[_Union[UnknownIxj, _Mapping]] = ..., unknown_fsdc: _Optional[_Iterable[_Union[InfiniteDreamEnterResponse.UnknownIze, _Mapping]]] = ..., unknown_fsdd: _Optional[_Iterable[_Union[InfiniteDreamEnterResponse.UnknownIzd, _Mapping]]] = ..., unknown_fsde: _Optional[_Iterable[_Union[UnknownIxj, _Mapping]]] = ..., unknown_fsdf: _Optional[_Iterable[_Union[UnknownIww, _Mapping]]] = ..., unknown_fsdg: _Optional[int] = ..., unknown_fsdh: _Optional[int] = ..., unknown_fsdi: _Optional[str] = ..., unknown_fsdk: _Optional[int] = ..., unknown_fsdm: _Optional[int] = ..., unknown_fsdn: _Optional[int] = ..., unknown_fsdo: _Optional[str] = ..., unknown_fsdp: _Optional[int] = ..., unknown_fsdq: _Optional[_Iterable[_Union[UnknownIzi, _Mapping]]] = ..., unknown_fsdr: _Optional[_Iterable[_Union[UnknownIyw, _Mapping]]] = ..., unknown_fsds: _Optional[int] = ..., unknown_fsdt: bool = ..., unknown_fsdu: bool = ..., unknown_fsdv: _Optional[int] = ..., unknown_fsdw: bool = ..., unknown_fsdx: _Optional[int] = ..., unknown_fsdy: bool = ...) -> None: ...

class InfiniteDreamRoomLootEvent(_message.Message):
    __slots__ = ("unknown_fsfj", "unknown_fsfk")
    UNKNOWN_FSFJ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSFK_FIELD_NUMBER: _ClassVar[int]
    unknown_fsfj: bool
    unknown_fsfk: _containers.RepeatedCompositeFieldContainer[UnknownIzm]
    def __init__(self, unknown_fsfj: bool = ..., unknown_fsfk: _Optional[_Iterable[_Union[UnknownIzm, _Mapping]]] = ...) -> None: ...

class InfiniteDreamRoomLootRequest(_message.Message):
    __slots__ = ("unknown_frws",)
    UNKNOWN_FRWS_FIELD_NUMBER: _ClassVar[int]
    unknown_frws: int
    def __init__(self, unknown_frws: _Optional[int] = ...) -> None: ...

class InfiniteDreamExitRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class InfiniteDreamRerollMonstersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownIxg(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownIyb(_message.Message):
    __slots__ = ("unknown_fryt",)
    UNKNOWN_FRYT_FIELD_NUMBER: _ClassVar[int]
    unknown_fryt: bool
    def __init__(self, unknown_fryt: bool = ...) -> None: ...

class UnknownIzj(_message.Message):
    __slots__ = ("unknown_fsel", "unknown_fsem")
    UNKNOWN_FSEL_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FSEM_FIELD_NUMBER: _ClassVar[int]
    unknown_fsel: bool
    unknown_fsem: bool
    def __init__(self, unknown_fsel: bool = ..., unknown_fsem: bool = ...) -> None: ...
