import common_pb2 as _common_pb2
import game_message_pb2 as _game_message_pb2
import report_pb2 as _report_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownHvs(_message.Message):
    __slots__ = ("unknown_fnwf",)
    UNKNOWN_FNWF_FIELD_NUMBER: _ClassVar[int]
    unknown_fnwf: int
    def __init__(self, unknown_fnwf: _Optional[int] = ...) -> None: ...

class UnknownHvt(_message.Message):
    __slots__ = ("unknown_fnwj", "unknown_fnwk")
    UNKNOWN_FNWJ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNWK_FIELD_NUMBER: _ClassVar[int]
    unknown_fnwj: UnknownIbj
    unknown_fnwk: str
    def __init__(self, unknown_fnwj: _Optional[_Union[UnknownIbj, _Mapping]] = ..., unknown_fnwk: _Optional[str] = ...) -> None: ...

class UnknownIbj(_message.Message):
    __slots__ = ("unknown_fopy", "unknown_fopz", "unknown_foqa", "unknown_foqb", "unknown_foqd")
    class UnknownFopyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_FOPY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOPZ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOQA_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOQB_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOQD_FIELD_NUMBER: _ClassVar[int]
    unknown_fopy: _containers.ScalarMap[str, int]
    unknown_fopz: int
    unknown_foqa: str
    unknown_foqb: str
    unknown_foqd: UnknownIau
    def __init__(self, unknown_fopy: _Optional[_Mapping[str, int]] = ..., unknown_fopz: _Optional[int] = ..., unknown_foqa: _Optional[str] = ..., unknown_foqb: _Optional[str] = ..., unknown_foqd: _Optional[_Union[UnknownIau, _Mapping]] = ...) -> None: ...

class UnknownIau(_message.Message):
    __slots__ = ("unknown_foob", "unknown_fooc", "unknown_fooe", "unknown_foog")
    class UnknownFoocValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_FOOC_VALUE_UNSPECIFIED: _ClassVar[UnknownIau.UnknownFoocValue]
    UNKNOWN_FOOC_VALUE_UNSPECIFIED: UnknownIau.UnknownFoocValue
    class UnknownFoocEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: UnknownIau.UnknownFoocValue
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[UnknownIau.UnknownFoocValue, str]] = ...) -> None: ...
    class UnknownFoogEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_FOOB_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOOC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOOE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOOG_FIELD_NUMBER: _ClassVar[int]
    unknown_foob: int
    unknown_fooc: _containers.ScalarMap[int, UnknownIau.UnknownFoocValue]
    unknown_fooe: int
    unknown_foog: _containers.ScalarMap[int, int]
    def __init__(self, unknown_foob: _Optional[int] = ..., unknown_fooc: _Optional[_Mapping[int, UnknownIau.UnknownFoocValue]] = ..., unknown_fooe: _Optional[int] = ..., unknown_foog: _Optional[_Mapping[int, int]] = ...) -> None: ...

class UnknownHwa(_message.Message):
    __slots__ = ("unknown_fnwv",)
    UNKNOWN_FNWV_FIELD_NUMBER: _ClassVar[int]
    unknown_fnwv: int
    def __init__(self, unknown_fnwv: _Optional[int] = ...) -> None: ...

class UnknownHwe(_message.Message):
    __slots__ = ("unknown_fnxe",)
    UNKNOWN_FNXE_FIELD_NUMBER: _ClassVar[int]
    unknown_fnxe: int
    def __init__(self, unknown_fnxe: _Optional[int] = ...) -> None: ...

class UnknownHwh(_message.Message):
    __slots__ = ("unknown_fnxr", "unknown_fnxs", "unknown_fnxt")
    UNKNOWN_FNXR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNXS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNXT_FIELD_NUMBER: _ClassVar[int]
    unknown_fnxr: GuildRaidLadderCategory
    unknown_fnxs: int
    unknown_fnxt: GuildRaidLadderEntry
    def __init__(self, unknown_fnxr: _Optional[_Union[GuildRaidLadderCategory, _Mapping]] = ..., unknown_fnxs: _Optional[int] = ..., unknown_fnxt: _Optional[_Union[GuildRaidLadderEntry, _Mapping]] = ...) -> None: ...

class GuildRaidLadderCategory(_message.Message):
    __slots__ = ("unknown_fojn", "unknown_fojo")
    UNKNOWN_FOJN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOJO_FIELD_NUMBER: _ClassVar[int]
    unknown_fojn: int
    unknown_fojo: _containers.RepeatedCompositeFieldContainer[GuildRaidLadderEntry]
    def __init__(self, unknown_fojn: _Optional[int] = ..., unknown_fojo: _Optional[_Iterable[_Union[GuildRaidLadderEntry, _Mapping]]] = ...) -> None: ...

class GuildRaidLadderEntry(_message.Message):
    __slots__ = ("unknown_fojv", "unknown_fojw", "unknown_fojy", "unknown_foka")
    UNKNOWN_FOJV_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOJW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOJY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOKA_FIELD_NUMBER: _ClassVar[int]
    unknown_fojv: int
    unknown_fojw: int
    unknown_fojy: int
    unknown_foka: GuildRaidLadderGuild
    def __init__(self, unknown_fojv: _Optional[int] = ..., unknown_fojw: _Optional[int] = ..., unknown_fojy: _Optional[int] = ..., unknown_foka: _Optional[_Union[GuildRaidLadderGuild, _Mapping]] = ...) -> None: ...

class GuildRaidLadderGuild(_message.Message):
    __slots__ = ("unknown_fokt", "unknown_foku", "unknown_fokv")
    UNKNOWN_FOKT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOKU_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOKV_FIELD_NUMBER: _ClassVar[int]
    unknown_fokt: str
    unknown_foku: _common_pb2.SocialEmblem
    unknown_fokv: str
    def __init__(self, unknown_fokt: _Optional[str] = ..., unknown_foku: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ..., unknown_fokv: _Optional[str] = ...) -> None: ...

class UnknownHwk(_message.Message):
    __slots__ = ("unknown_fnxx",)
    UNKNOWN_FNXX_FIELD_NUMBER: _ClassVar[int]
    unknown_fnxx: int
    def __init__(self, unknown_fnxx: _Optional[int] = ...) -> None: ...

class UnknownHwl(_message.Message):
    __slots__ = ("unknown_fnyb", "unknown_fnyc", "unknown_fnyd", "unknown_fnye")
    UNKNOWN_FNYB_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNYC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNYD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNYE_FIELD_NUMBER: _ClassVar[int]
    unknown_fnyb: int
    unknown_fnyc: _containers.RepeatedCompositeFieldContainer[UnknownHwr]
    unknown_fnyd: UnknownHyr
    unknown_fnye: str
    def __init__(self, unknown_fnyb: _Optional[int] = ..., unknown_fnyc: _Optional[_Iterable[_Union[UnknownHwr, _Mapping]]] = ..., unknown_fnyd: _Optional[_Union[UnknownHyr, _Mapping]] = ..., unknown_fnye: _Optional[str] = ...) -> None: ...

class UnknownHwr(_message.Message):
    __slots__ = ("unknown_fnyx", "unknown_fnyy", "unknown_fnyv", "unknown_fnza", "unknown_fnyz")
    UNKNOWN_FNYX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNYY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNYV_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNZA_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNYZ_FIELD_NUMBER: _ClassVar[int]
    unknown_fnyx: int
    unknown_fnyy: bool
    unknown_fnyv: bool
    unknown_fnza: UnknownHxd
    unknown_fnyz: bool
    def __init__(self, unknown_fnyx: _Optional[int] = ..., unknown_fnyy: bool = ..., unknown_fnyv: bool = ..., unknown_fnza: _Optional[_Union[UnknownHxd, _Mapping]] = ..., unknown_fnyz: bool = ...) -> None: ...

class UnknownHxd(_message.Message):
    __slots__ = ("unknown_foal", "unknown_foao", "unknown_foan")
    class UnknownHxb(_message.Message):
        __slots__ = ("unknown_foag",)
        UNKNOWN_FOAG_FIELD_NUMBER: _ClassVar[int]
        unknown_foag: str
        def __init__(self, unknown_foag: _Optional[str] = ...) -> None: ...
    UNKNOWN_FOAL_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOAO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOAN_FIELD_NUMBER: _ClassVar[int]
    unknown_foal: UnknownHys
    unknown_foao: UnknownHxd.UnknownHxb
    unknown_foan: UnknownHys
    def __init__(self, unknown_foal: _Optional[_Union[UnknownHys, _Mapping]] = ..., unknown_foao: _Optional[_Union[UnknownHxd.UnknownHxb, _Mapping]] = ..., unknown_foan: _Optional[_Union[UnknownHys, _Mapping]] = ...) -> None: ...

class UnknownHys(_message.Message):
    __slots__ = ("unknown_fofx", "unknown_fofy", "unknown_fofz", "unknown_fogb", "unknown_fogc", "unknown_fogd", "unknown_foge")
    UNKNOWN_FOFX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOFY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOFZ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOGB_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOGC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOGD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOGE_FIELD_NUMBER: _ClassVar[int]
    unknown_fofx: int
    unknown_fofy: int
    unknown_fofz: int
    unknown_fogb: int
    unknown_fogc: str
    unknown_fogd: _common_pb2.CharacterStatus
    unknown_foge: str
    def __init__(self, unknown_fofx: _Optional[int] = ..., unknown_fofy: _Optional[int] = ..., unknown_fofz: _Optional[int] = ..., unknown_fogb: _Optional[int] = ..., unknown_fogc: _Optional[str] = ..., unknown_fogd: _Optional[_Union[_common_pb2.CharacterStatus, _Mapping]] = ..., unknown_foge: _Optional[str] = ...) -> None: ...

class UnknownHyr(_message.Message):
    __slots__ = ("unknown_fofr", "unknown_fofs", "unknown_foft")
    class UnknownHyp(_message.Message):
        __slots__ = ("unknown_fofl", "unknown_fofm")
        UNKNOWN_FOFL_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOFM_FIELD_NUMBER: _ClassVar[int]
        unknown_fofl: int
        unknown_fofm: str
        def __init__(self, unknown_fofl: _Optional[int] = ..., unknown_fofm: _Optional[str] = ...) -> None: ...
    UNKNOWN_FOFR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOFS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOFT_FIELD_NUMBER: _ClassVar[int]
    unknown_fofr: UnknownHyr.UnknownHyp
    unknown_fofs: str
    unknown_foft: str
    def __init__(self, unknown_fofr: _Optional[_Union[UnknownHyr.UnknownHyp, _Mapping]] = ..., unknown_fofs: _Optional[str] = ..., unknown_foft: _Optional[str] = ...) -> None: ...

class UnknownHwo(_message.Message):
    __slots__ = ("unknown_fnyi", "unknown_fnyj", "unknown_fnyk")
    UNKNOWN_FNYI_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNYJ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNYK_FIELD_NUMBER: _ClassVar[int]
    unknown_fnyi: str
    unknown_fnyj: str
    unknown_fnyk: int
    def __init__(self, unknown_fnyi: _Optional[str] = ..., unknown_fnyj: _Optional[str] = ..., unknown_fnyk: _Optional[int] = ...) -> None: ...

class GuildRaidLadderEvent(_message.Message):
    __slots__ = ("unknown_fnze", "unknown_fnzf", "unknown_fnzg", "unknown_fnzh")
    class UnknownFnzeEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: GuildRaidLadderCategory
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[GuildRaidLadderCategory, _Mapping]] = ...) -> None: ...
    class UnknownFnzfEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: GuildRaidLadderCategory
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[GuildRaidLadderCategory, _Mapping]] = ...) -> None: ...
    class UnknownFnzgEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: GuildRaidLadderEntry
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[GuildRaidLadderEntry, _Mapping]] = ...) -> None: ...
    class UnknownFnzhEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: GuildRaidLadderEntry
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[GuildRaidLadderEntry, _Mapping]] = ...) -> None: ...
    UNKNOWN_FNZE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNZF_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNZG_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNZH_FIELD_NUMBER: _ClassVar[int]
    unknown_fnze: _containers.MessageMap[int, GuildRaidLadderCategory]
    unknown_fnzf: _containers.MessageMap[int, GuildRaidLadderCategory]
    unknown_fnzg: _containers.MessageMap[int, GuildRaidLadderEntry]
    unknown_fnzh: _containers.MessageMap[int, GuildRaidLadderEntry]
    def __init__(self, unknown_fnze: _Optional[_Mapping[int, GuildRaidLadderCategory]] = ..., unknown_fnzf: _Optional[_Mapping[int, GuildRaidLadderCategory]] = ..., unknown_fnzg: _Optional[_Mapping[int, GuildRaidLadderEntry]] = ..., unknown_fnzh: _Optional[_Mapping[int, GuildRaidLadderEntry]] = ...) -> None: ...

class UnknownHxm(_message.Message):
    __slots__ = ("unknown_focc", "unknown_foce", "unknown_focf", "unknown_focg")
    class UnknownFoccEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class UnknownFoceEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: UnknownHxm.UnknownHxj
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[UnknownHxm.UnknownHxj, _Mapping]] = ...) -> None: ...
    class UnknownHxj(_message.Message):
        __slots__ = ("unknown_fobr", "unknown_fobs")
        UNKNOWN_FOBR_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOBS_FIELD_NUMBER: _ClassVar[int]
        unknown_fobr: _containers.RepeatedScalarFieldContainer[int]
        unknown_fobs: int
        def __init__(self, unknown_fobr: _Optional[_Iterable[int]] = ..., unknown_fobs: _Optional[int] = ...) -> None: ...
    class UnknownHxk(_message.Message):
        __slots__ = ("unknown_fobx", "unknown_fobw", "unknown_foby")
        UNKNOWN_FOBX_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOBW_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOBY_FIELD_NUMBER: _ClassVar[int]
        unknown_fobx: _containers.RepeatedScalarFieldContainer[int]
        unknown_fobw: int
        unknown_foby: int
        def __init__(self, unknown_fobx: _Optional[_Iterable[int]] = ..., unknown_fobw: _Optional[int] = ..., unknown_foby: _Optional[int] = ...) -> None: ...
    UNKNOWN_FOCC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOCE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOCF_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOCG_FIELD_NUMBER: _ClassVar[int]
    unknown_focc: _containers.ScalarMap[str, int]
    unknown_foce: _containers.MessageMap[int, UnknownHxm.UnknownHxj]
    unknown_focf: UnknownIcl
    unknown_focg: UnknownHxm.UnknownHxk
    def __init__(self, unknown_focc: _Optional[_Mapping[str, int]] = ..., unknown_foce: _Optional[_Mapping[int, UnknownHxm.UnknownHxj]] = ..., unknown_focf: _Optional[_Union[UnknownIcl, _Mapping]] = ..., unknown_focg: _Optional[_Union[UnknownHxm.UnknownHxk, _Mapping]] = ...) -> None: ...

class UnknownIcl(_message.Message):
    __slots__ = ("unknown_fota", "unknown_fotb", "unknown_fotd", "unknown_fote", "unknown_fotf")
    UNKNOWN_FOTA_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOTB_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOTD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOTE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOTF_FIELD_NUMBER: _ClassVar[int]
    unknown_fota: GuildRaidLadderGuild
    unknown_fotb: str
    unknown_fotd: UnknownHwl
    unknown_fote: UnknownIbg
    unknown_fotf: UnknownHyx
    def __init__(self, unknown_fota: _Optional[_Union[GuildRaidLadderGuild, _Mapping]] = ..., unknown_fotb: _Optional[str] = ..., unknown_fotd: _Optional[_Union[UnknownHwl, _Mapping]] = ..., unknown_fote: _Optional[_Union[UnknownIbg, _Mapping]] = ..., unknown_fotf: _Optional[_Union[UnknownHyx, _Mapping]] = ...) -> None: ...

class UnknownIbg(_message.Message):
    __slots__ = ("unknown_foph", "unknown_fopi", "unknown_fopj", "unknown_fopk")
    UNKNOWN_FOPH_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOPI_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOPJ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOPK_FIELD_NUMBER: _ClassVar[int]
    unknown_foph: UnknownHyr
    unknown_fopi: _containers.RepeatedCompositeFieldContainer[UnknownHwr]
    unknown_fopj: int
    unknown_fopk: _containers.RepeatedCompositeFieldContainer[UnknownHys]
    def __init__(self, unknown_foph: _Optional[_Union[UnknownHyr, _Mapping]] = ..., unknown_fopi: _Optional[_Iterable[_Union[UnknownHwr, _Mapping]]] = ..., unknown_fopj: _Optional[int] = ..., unknown_fopk: _Optional[_Iterable[_Union[UnknownHys, _Mapping]]] = ...) -> None: ...

class UnknownHyx(_message.Message):
    __slots__ = ("unknown_fogr", "unknown_fogt", "unknown_fogu", "unknown_fogv", "unknown_fogw")
    UNKNOWN_FOGR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOGT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOGU_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOGV_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOGW_FIELD_NUMBER: _ClassVar[int]
    unknown_fogr: _containers.RepeatedScalarFieldContainer[str]
    unknown_fogt: str
    unknown_fogu: _containers.RepeatedCompositeFieldContainer[UnknownHwr]
    unknown_fogv: int
    unknown_fogw: UnknownHyr
    def __init__(self, unknown_fogr: _Optional[_Iterable[str]] = ..., unknown_fogt: _Optional[str] = ..., unknown_fogu: _Optional[_Iterable[_Union[UnknownHwr, _Mapping]]] = ..., unknown_fogv: _Optional[int] = ..., unknown_fogw: _Optional[_Union[UnknownHyr, _Mapping]] = ...) -> None: ...

class UnknownHxt(_message.Message):
    __slots__ = ("unknown_focw", "unknown_focx", "unknown_focy", "unknown_focz")
    class UnknownHxq(_message.Message):
        __slots__ = ("unknown_foco",)
        UNKNOWN_FOCO_FIELD_NUMBER: _ClassVar[int]
        unknown_foco: _containers.RepeatedCompositeFieldContainer[UnknownHxd]
        def __init__(self, unknown_foco: _Optional[_Iterable[_Union[UnknownHxd, _Mapping]]] = ...) -> None: ...
    class UnknownHxr(_message.Message):
        __slots__ = ("unknown_focs",)
        UNKNOWN_FOCS_FIELD_NUMBER: _ClassVar[int]
        unknown_focs: _containers.RepeatedCompositeFieldContainer[UnknownHxd]
        def __init__(self, unknown_focs: _Optional[_Iterable[_Union[UnknownHxd, _Mapping]]] = ...) -> None: ...
    UNKNOWN_FOCW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOCX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOCY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOCZ_FIELD_NUMBER: _ClassVar[int]
    unknown_focw: UnknownHxt.UnknownHxr
    unknown_focx: int
    unknown_focy: UnknownHxt.UnknownHxq
    unknown_focz: int
    def __init__(self, unknown_focw: _Optional[_Union[UnknownHxt.UnknownHxr, _Mapping]] = ..., unknown_focx: _Optional[int] = ..., unknown_focy: _Optional[_Union[UnknownHxt.UnknownHxq, _Mapping]] = ..., unknown_focz: _Optional[int] = ...) -> None: ...

class UnknownHxu(_message.Message):
    __slots__ = ("unknown_fodf", "unknown_fodg")
    UNKNOWN_FODF_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FODG_FIELD_NUMBER: _ClassVar[int]
    unknown_fodf: str
    unknown_fodg: str
    def __init__(self, unknown_fodf: _Optional[str] = ..., unknown_fodg: _Optional[str] = ...) -> None: ...

class UnknownHxx(_message.Message):
    __slots__ = ("unknown_fodl",)
    UNKNOWN_FODL_FIELD_NUMBER: _ClassVar[int]
    unknown_fodl: int
    def __init__(self, unknown_fodl: _Optional[int] = ...) -> None: ...

class UnknownHya(_message.Message):
    __slots__ = ("unknown_fodq", "unknown_fodr")
    UNKNOWN_FODQ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FODR_FIELD_NUMBER: _ClassVar[int]
    unknown_fodq: UnknownIbg
    unknown_fodr: str
    def __init__(self, unknown_fodq: _Optional[_Union[UnknownIbg, _Mapping]] = ..., unknown_fodr: _Optional[str] = ...) -> None: ...

class UnknownHyb(_message.Message):
    __slots__ = ("unknown_fodv", "unknown_fodw", "unknown_fodx")
    UNKNOWN_FODV_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FODW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FODX_FIELD_NUMBER: _ClassVar[int]
    unknown_fodv: str
    unknown_fodw: str
    unknown_fodx: bool
    def __init__(self, unknown_fodv: _Optional[str] = ..., unknown_fodw: _Optional[str] = ..., unknown_fodx: bool = ...) -> None: ...

class UnknownHyg(_message.Message):
    __slots__ = ("unknown_foeh", "unknown_foef", "unknown_foei", "unknown_foej", "unknown_foek", "unknown_foee")
    class UnknownFoekValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_FOEK_VALUE_UNSPECIFIED: _ClassVar[UnknownHyg.UnknownFoekValue]
    UNKNOWN_FOEK_VALUE_UNSPECIFIED: UnknownHyg.UnknownFoekValue
    class UnknownFoekEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: UnknownHyg.UnknownFoekValue
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[UnknownHyg.UnknownFoekValue, str]] = ...) -> None: ...
    UNKNOWN_FOEH_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOEF_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOEI_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOEJ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOEK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOEE_FIELD_NUMBER: _ClassVar[int]
    unknown_foeh: int
    unknown_foef: int
    unknown_foei: _containers.RepeatedScalarFieldContainer[int]
    unknown_foej: bool
    unknown_foek: _containers.ScalarMap[int, UnknownHyg.UnknownFoekValue]
    unknown_foee: int
    def __init__(self, unknown_foeh: _Optional[int] = ..., unknown_foef: _Optional[int] = ..., unknown_foei: _Optional[_Iterable[int]] = ..., unknown_foej: bool = ..., unknown_foek: _Optional[_Mapping[int, UnknownHyg.UnknownFoekValue]] = ..., unknown_foee: _Optional[int] = ...) -> None: ...

class UnknownHyj(_message.Message):
    __slots__ = ("unknown_foeo",)
    class UnknownFoeoValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_FOEO_VALUE_UNSPECIFIED: _ClassVar[UnknownHyj.UnknownFoeoValue]
    UNKNOWN_FOEO_VALUE_UNSPECIFIED: UnknownHyj.UnknownFoeoValue
    UNKNOWN_FOEO_FIELD_NUMBER: _ClassVar[int]
    unknown_foeo: UnknownHyj.UnknownFoeoValue
    def __init__(self, unknown_foeo: _Optional[_Union[UnknownHyj.UnknownFoeoValue, str]] = ...) -> None: ...

class UnknownHyt(_message.Message):
    __slots__ = ("unknown_fogi",)
    UNKNOWN_FOGI_FIELD_NUMBER: _ClassVar[int]
    unknown_fogi: int
    def __init__(self, unknown_fogi: _Optional[int] = ...) -> None: ...

class UnknownHyw(_message.Message):
    __slots__ = ("unknown_fogm",)
    class UnknownFogmValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_FOGM_VALUE_UNSPECIFIED: _ClassVar[UnknownHyw.UnknownFogmValue]
    UNKNOWN_FOGM_VALUE_UNSPECIFIED: UnknownHyw.UnknownFogmValue
    UNKNOWN_FOGM_FIELD_NUMBER: _ClassVar[int]
    unknown_fogm: UnknownHyw.UnknownFogmValue
    def __init__(self, unknown_fogm: _Optional[_Union[UnknownHyw.UnknownFogmValue, str]] = ...) -> None: ...

class UnknownHzb(_message.Message):
    __slots__ = ("unknown_fohk", "unknown_fohm")
    UNKNOWN_FOHK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOHM_FIELD_NUMBER: _ClassVar[int]
    unknown_fohk: int
    unknown_fohm: UnknownIcl
    def __init__(self, unknown_fohk: _Optional[int] = ..., unknown_fohm: _Optional[_Union[UnknownIcl, _Mapping]] = ...) -> None: ...

class UnknownHzd(_message.Message):
    __slots__ = ("unknown_foht",)
    UNKNOWN_FOHT_FIELD_NUMBER: _ClassVar[int]
    unknown_foht: bool
    def __init__(self, unknown_foht: bool = ...) -> None: ...

class UnknownHzg(_message.Message):
    __slots__ = ("unknown_fohx", "unknown_fohz")
    UNKNOWN_FOHX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOHZ_FIELD_NUMBER: _ClassVar[int]
    unknown_fohx: UnknownIau
    unknown_fohz: str
    def __init__(self, unknown_fohx: _Optional[_Union[UnknownIau, _Mapping]] = ..., unknown_fohz: _Optional[str] = ...) -> None: ...

class UnknownHzh(_message.Message):
    __slots__ = ("unknown_foid", "unknown_foie")
    UNKNOWN_FOID_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOIE_FIELD_NUMBER: _ClassVar[int]
    unknown_foid: str
    unknown_foie: str
    def __init__(self, unknown_foid: _Optional[str] = ..., unknown_foie: _Optional[str] = ...) -> None: ...

class UnknownHzi(_message.Message):
    __slots__ = ("unknown_foik", "unknown_foim")
    UNKNOWN_FOIK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOIM_FIELD_NUMBER: _ClassVar[int]
    unknown_foik: int
    unknown_foim: str
    def __init__(self, unknown_foik: _Optional[int] = ..., unknown_foim: _Optional[str] = ...) -> None: ...

class UnknownHzj(_message.Message):
    __slots__ = ("unknown_foit",)
    UNKNOWN_FOIT_FIELD_NUMBER: _ClassVar[int]
    unknown_foit: int
    def __init__(self, unknown_foit: _Optional[int] = ...) -> None: ...

class UnknownHzk(_message.Message):
    __slots__ = ("unknown_foiy", "unknown_foiz")
    UNKNOWN_FOIY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOIZ_FIELD_NUMBER: _ClassVar[int]
    unknown_foiy: str
    unknown_foiz: str
    def __init__(self, unknown_foiy: _Optional[str] = ..., unknown_foiz: _Optional[str] = ...) -> None: ...

class UnknownHzn(_message.Message):
    __slots__ = ("unknown_fojd",)
    UNKNOWN_FOJD_FIELD_NUMBER: _ClassVar[int]
    unknown_fojd: int
    def __init__(self, unknown_fojd: _Optional[int] = ...) -> None: ...

class UnknownHzo(_message.Message):
    __slots__ = ("unknown_fojh", "unknown_foji")
    class UnknownFojhEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: GuildRaidLadderEntry
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[GuildRaidLadderEntry, _Mapping]] = ...) -> None: ...
    class UnknownFojiEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: GuildRaidLadderCategory
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[GuildRaidLadderCategory, _Mapping]] = ...) -> None: ...
    UNKNOWN_FOJH_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOJI_FIELD_NUMBER: _ClassVar[int]
    unknown_fojh: _containers.MessageMap[int, GuildRaidLadderEntry]
    unknown_foji: _containers.MessageMap[int, GuildRaidLadderCategory]
    def __init__(self, unknown_fojh: _Optional[_Mapping[int, GuildRaidLadderEntry]] = ..., unknown_foji: _Optional[_Mapping[int, GuildRaidLadderCategory]] = ...) -> None: ...

class UnknownHzv(_message.Message):
    __slots__ = ("unknown_fokf",)
    UNKNOWN_FOKF_FIELD_NUMBER: _ClassVar[int]
    unknown_fokf: int
    def __init__(self, unknown_fokf: _Optional[int] = ...) -> None: ...

class UnknownHzy(_message.Message):
    __slots__ = ("unknown_fokz",)
    UNKNOWN_FOKZ_FIELD_NUMBER: _ClassVar[int]
    unknown_fokz: UnknownIcl
    def __init__(self, unknown_fokz: _Optional[_Union[UnknownIcl, _Mapping]] = ...) -> None: ...

class UnknownIag(_message.Message):
    __slots__ = ("unknown_folx",)
    UNKNOWN_FOLX_FIELD_NUMBER: _ClassVar[int]
    unknown_folx: bool
    def __init__(self, unknown_folx: bool = ...) -> None: ...

class UnknownIai(_message.Message):
    __slots__ = ("unknown_fomb", "unknown_fomc", "unknown_fomd", "unknown_fome", "unknown_fomf")
    UNKNOWN_FOMB_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOMC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOMD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOME_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOMF_FIELD_NUMBER: _ClassVar[int]
    unknown_fomb: str
    unknown_fomc: UnknownHwl
    unknown_fomd: UnknownHyx
    unknown_fome: UnknownIak
    unknown_fomf: UnknownIbg
    def __init__(self, unknown_fomb: _Optional[str] = ..., unknown_fomc: _Optional[_Union[UnknownHwl, _Mapping]] = ..., unknown_fomd: _Optional[_Union[UnknownHyx, _Mapping]] = ..., unknown_fome: _Optional[_Union[UnknownIak, _Mapping]] = ..., unknown_fomf: _Optional[_Union[UnknownIbg, _Mapping]] = ...) -> None: ...

class UnknownIak(_message.Message):
    __slots__ = ("unknown_fomo", "unknown_fomp", "unknown_fomq", "unknown_fomr", "unknown_foms", "unknown_fomt", "unknown_fomu")
    UNKNOWN_FOMO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOMP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOMQ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOMR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOMS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOMT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOMU_FIELD_NUMBER: _ClassVar[int]
    unknown_fomo: str
    unknown_fomp: _containers.RepeatedCompositeFieldContainer[UnknownHwr]
    unknown_fomq: int
    unknown_fomr: int
    unknown_foms: _containers.RepeatedScalarFieldContainer[int]
    unknown_fomt: int
    unknown_fomu: UnknownHyr
    def __init__(self, unknown_fomo: _Optional[str] = ..., unknown_fomp: _Optional[_Iterable[_Union[UnknownHwr, _Mapping]]] = ..., unknown_fomq: _Optional[int] = ..., unknown_fomr: _Optional[int] = ..., unknown_foms: _Optional[_Iterable[int]] = ..., unknown_fomt: _Optional[int] = ..., unknown_fomu: _Optional[_Union[UnknownHyr, _Mapping]] = ...) -> None: ...

class UnknownIaj(_message.Message):
    __slots__ = ("unknown_fomk",)
    UNKNOWN_FOMK_FIELD_NUMBER: _ClassVar[int]
    unknown_fomk: str
    def __init__(self, unknown_fomk: _Optional[str] = ...) -> None: ...

class UnknownIav(_message.Message):
    __slots__ = ("unknown_fook", "unknown_fool", "unknown_foom")
    UNKNOWN_FOOK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOOL_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOOM_FIELD_NUMBER: _ClassVar[int]
    unknown_fook: str
    unknown_fool: str
    unknown_foom: _common_pb2.CharacterStatus
    def __init__(self, unknown_fook: _Optional[str] = ..., unknown_fool: _Optional[str] = ..., unknown_foom: _Optional[_Union[_common_pb2.CharacterStatus, _Mapping]] = ...) -> None: ...

class UnknownIbc(_message.Message):
    __slots__ = ("unknown_fooy",)
    UNKNOWN_FOOY_FIELD_NUMBER: _ClassVar[int]
    unknown_fooy: int
    def __init__(self, unknown_fooy: _Optional[int] = ...) -> None: ...

class UnknownIbk(_message.Message):
    __slots__ = ("unknown_foqh", "unknown_foqi")
    class UnknownFoqiEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_FOQH_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOQI_FIELD_NUMBER: _ClassVar[int]
    unknown_foqh: str
    unknown_foqi: _containers.ScalarMap[str, int]
    def __init__(self, unknown_foqh: _Optional[str] = ..., unknown_foqi: _Optional[_Mapping[str, int]] = ...) -> None: ...

class UnknownIbl(_message.Message):
    __slots__ = ("unknown_foqm",)
    UNKNOWN_FOQM_FIELD_NUMBER: _ClassVar[int]
    unknown_foqm: _containers.RepeatedScalarFieldContainer[bool]
    def __init__(self, unknown_foqm: _Optional[_Iterable[bool]] = ...) -> None: ...

class UnknownIbo(_message.Message):
    __slots__ = ("unknown_foqr", "unknown_foqs")
    UNKNOWN_FOQR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOQS_FIELD_NUMBER: _ClassVar[int]
    unknown_foqr: GuildRaidLadderGuild
    unknown_foqs: int
    def __init__(self, unknown_foqr: _Optional[_Union[GuildRaidLadderGuild, _Mapping]] = ..., unknown_foqs: _Optional[int] = ...) -> None: ...

class UnknownIbs(_message.Message):
    __slots__ = ("unknown_forg",)
    UNKNOWN_FORG_FIELD_NUMBER: _ClassVar[int]
    unknown_forg: _containers.RepeatedCompositeFieldContainer[UnknownHzj]
    def __init__(self, unknown_forg: _Optional[_Iterable[_Union[UnknownHzj, _Mapping]]] = ...) -> None: ...

class UnknownIbv(_message.Message):
    __slots__ = ("unknown_fork", "unknown_forl")
    UNKNOWN_FORK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FORL_FIELD_NUMBER: _ClassVar[int]
    unknown_fork: str
    unknown_forl: UnknownIbj
    def __init__(self, unknown_fork: _Optional[str] = ..., unknown_forl: _Optional[_Union[UnknownIbj, _Mapping]] = ...) -> None: ...

class UnknownIbw(_message.Message):
    __slots__ = ("unknown_forr",)
    UNKNOWN_FORR_FIELD_NUMBER: _ClassVar[int]
    unknown_forr: int
    def __init__(self, unknown_forr: _Optional[int] = ...) -> None: ...

class UnknownIce(_message.Message):
    __slots__ = ("unknown_fosi", "unknown_fosj")
    class UnknownIcc(_message.Message):
        __slots__ = ("unknown_forz", "unknown_fosa", "unknown_fosc", "unknown_fosd")
        class UnknownForzEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: UnknownIbg
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownIbg, _Mapping]] = ...) -> None: ...
        class UnknownFosaEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: UnknownHwl
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownHwl, _Mapping]] = ...) -> None: ...
        class UnknownFoscEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: UnknownHyx
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownHyx, _Mapping]] = ...) -> None: ...
        class UnknownFosdEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: UnknownIak
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownIak, _Mapping]] = ...) -> None: ...
        UNKNOWN_FORZ_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOSA_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOSC_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOSD_FIELD_NUMBER: _ClassVar[int]
        unknown_forz: _containers.MessageMap[str, UnknownIbg]
        unknown_fosa: _containers.MessageMap[str, UnknownHwl]
        unknown_fosc: _containers.MessageMap[str, UnknownHyx]
        unknown_fosd: _containers.MessageMap[str, UnknownIak]
        def __init__(self, unknown_forz: _Optional[_Mapping[str, UnknownIbg]] = ..., unknown_fosa: _Optional[_Mapping[str, UnknownHwl]] = ..., unknown_fosc: _Optional[_Mapping[str, UnknownHyx]] = ..., unknown_fosd: _Optional[_Mapping[str, UnknownIak]] = ...) -> None: ...
    UNKNOWN_FOSI_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOSJ_FIELD_NUMBER: _ClassVar[int]
    unknown_fosi: UnknownIce.UnknownIcc
    unknown_fosj: int
    def __init__(self, unknown_fosi: _Optional[_Union[UnknownIce.UnknownIcc, _Mapping]] = ..., unknown_fosj: _Optional[int] = ...) -> None: ...

class UnknownIcj(_message.Message):
    __slots__ = ("unknown_fost", "unknown_fosu")
    class UnknownIch(_message.Message):
        __slots__ = ("unknown_fosp",)
        UNKNOWN_FOSP_FIELD_NUMBER: _ClassVar[int]
        unknown_fosp: UnknownIbj
        def __init__(self, unknown_fosp: _Optional[_Union[UnknownIbj, _Mapping]] = ...) -> None: ...
    UNKNOWN_FOST_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOSU_FIELD_NUMBER: _ClassVar[int]
    unknown_fost: UnknownIcj.UnknownIch
    unknown_fosu: int
    def __init__(self, unknown_fost: _Optional[_Union[UnknownIcj.UnknownIch, _Mapping]] = ..., unknown_fosu: _Optional[int] = ...) -> None: ...

class UnknownIcz(_message.Message):
    __slots__ = ("unknown_foum", "unknown_foun", "unknown_fouo", "unknown_foup", "unknown_fouq")
    class UnknownIcp(_message.Message):
        __slots__ = ("unknown_fotq",)
        UNKNOWN_FOTQ_FIELD_NUMBER: _ClassVar[int]
        unknown_fotq: UnknownHxd
        def __init__(self, unknown_fotq: _Optional[_Union[UnknownHxd, _Mapping]] = ...) -> None: ...
    class UnknownIcq(_message.Message):
        __slots__ = ("unknown_fotu",)
        UNKNOWN_FOTU_FIELD_NUMBER: _ClassVar[int]
        unknown_fotu: _containers.RepeatedCompositeFieldContainer[UnknownHxd]
        def __init__(self, unknown_fotu: _Optional[_Iterable[_Union[UnknownHxd, _Mapping]]] = ...) -> None: ...
    class UnknownIcu(_message.Message):
        __slots__ = ("unknown_foue",)
        UNKNOWN_FOUE_FIELD_NUMBER: _ClassVar[int]
        unknown_foue: _containers.RepeatedCompositeFieldContainer[UnknownHxd]
        def __init__(self, unknown_foue: _Optional[_Iterable[_Union[UnknownHxd, _Mapping]]] = ...) -> None: ...
    UNKNOWN_FOUM_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUQ_FIELD_NUMBER: _ClassVar[int]
    unknown_foum: int
    unknown_foun: UnknownIcz.UnknownIcu
    unknown_fouo: UnknownIcz.UnknownIcp
    unknown_foup: UnknownIcz.UnknownIcq
    unknown_fouq: int
    def __init__(self, unknown_foum: _Optional[int] = ..., unknown_foun: _Optional[_Union[UnknownIcz.UnknownIcu, _Mapping]] = ..., unknown_fouo: _Optional[_Union[UnknownIcz.UnknownIcp, _Mapping]] = ..., unknown_foup: _Optional[_Union[UnknownIcz.UnknownIcq, _Mapping]] = ..., unknown_fouq: _Optional[int] = ...) -> None: ...

class UnknownIda(_message.Message):
    __slots__ = ("unknown_fouw", "unknown_foux")
    UNKNOWN_FOUW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUX_FIELD_NUMBER: _ClassVar[int]
    unknown_fouw: str
    unknown_foux: str
    def __init__(self, unknown_fouw: _Optional[str] = ..., unknown_foux: _Optional[str] = ...) -> None: ...

class UnknownIde(_message.Message):
    __slots__ = ("unknown_fovd",)
    UNKNOWN_FOVD_FIELD_NUMBER: _ClassVar[int]
    unknown_fovd: int
    def __init__(self, unknown_fovd: _Optional[int] = ...) -> None: ...

class UnknownIdf(_message.Message):
    __slots__ = ("unknown_fovh", "unknown_fovi")
    UNKNOWN_FOVH_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOVI_FIELD_NUMBER: _ClassVar[int]
    unknown_fovh: int
    unknown_fovi: str
    def __init__(self, unknown_fovh: _Optional[int] = ..., unknown_fovi: _Optional[str] = ...) -> None: ...

class UnknownIdi(_message.Message):
    __slots__ = ("unknown_fovm",)
    UNKNOWN_FOVM_FIELD_NUMBER: _ClassVar[int]
    unknown_fovm: int
    def __init__(self, unknown_fovm: _Optional[int] = ...) -> None: ...

class UnknownIdm(_message.Message):
    __slots__ = ("unknown_fovv", "unknown_fovx")
    UNKNOWN_FOVV_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOVX_FIELD_NUMBER: _ClassVar[int]
    unknown_fovv: int
    unknown_fovx: int
    def __init__(self, unknown_fovv: _Optional[int] = ..., unknown_fovx: _Optional[int] = ...) -> None: ...

class GuildRaidLadderRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownHvx(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownHwb(_message.Message):
    __slots__ = ("unknown_fnxa",)
    UNKNOWN_FNXA_FIELD_NUMBER: _ClassVar[int]
    unknown_fnxa: int
    def __init__(self, unknown_fnxa: _Optional[int] = ...) -> None: ...
