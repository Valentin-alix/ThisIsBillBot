import common_pb2 as _common_pb2
import cosmetic_pb2 as _cosmetic_pb2
import game_message_pb2 as _game_message_pb2
import preset_pb2 as _preset_pb2
import report_pb2 as _report_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownKxm(_message.Message):
    __slots__ = ("unknown_fzqb", "unknown_fzqc")
    class UnknownKxj(_message.Message):
        __slots__ = ("unknown_fzps",)
        UNKNOWN_FZPS_FIELD_NUMBER: _ClassVar[int]
        unknown_fzps: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, unknown_fzps: _Optional[_Iterable[int]] = ...) -> None: ...
    class UnknownKxk(_message.Message):
        __slots__ = ("unknown_fzpx",)
        UNKNOWN_FZPX_FIELD_NUMBER: _ClassVar[int]
        unknown_fzpx: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, unknown_fzpx: _Optional[_Iterable[int]] = ...) -> None: ...
    UNKNOWN_FZQB_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZQC_FIELD_NUMBER: _ClassVar[int]
    unknown_fzqb: UnknownKxm.UnknownKxj
    unknown_fzqc: UnknownKxm.UnknownKxk
    def __init__(self, unknown_fzqb: _Optional[_Union[UnknownKxm.UnknownKxj, _Mapping]] = ..., unknown_fzqc: _Optional[_Union[UnknownKxm.UnknownKxk, _Mapping]] = ...) -> None: ...

class UnknownKxr(_message.Message):
    __slots__ = ("unknown_fzqp", "unknown_fzqq")
    class UnknownKxo(_message.Message):
        __slots__ = ("unknown_fzqh",)
        UNKNOWN_FZQH_FIELD_NUMBER: _ClassVar[int]
        unknown_fzqh: int
        def __init__(self, unknown_fzqh: _Optional[int] = ...) -> None: ...
    class UnknownKxp(_message.Message):
        __slots__ = ("unknown_fzql",)
        UNKNOWN_FZQL_FIELD_NUMBER: _ClassVar[int]
        unknown_fzql: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, unknown_fzql: _Optional[_Iterable[int]] = ...) -> None: ...
    UNKNOWN_FZQP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZQQ_FIELD_NUMBER: _ClassVar[int]
    unknown_fzqp: UnknownKxr.UnknownKxp
    unknown_fzqq: UnknownKxr.UnknownKxo
    def __init__(self, unknown_fzqp: _Optional[_Union[UnknownKxr.UnknownKxp, _Mapping]] = ..., unknown_fzqq: _Optional[_Union[UnknownKxr.UnknownKxo, _Mapping]] = ...) -> None: ...

class UnknownKxs(_message.Message):
    __slots__ = ("unknown_fzqv",)
    UNKNOWN_FZQV_FIELD_NUMBER: _ClassVar[int]
    unknown_fzqv: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, unknown_fzqv: _Optional[_Iterable[int]] = ...) -> None: ...

class UnknownKyb(_message.Message):
    __slots__ = ("unknown_fzrp", "unknown_fzrq")
    class UnknownKxw(_message.Message):
        __slots__ = ("unknown_fzre",)
        UNKNOWN_FZRE_FIELD_NUMBER: _ClassVar[int]
        unknown_fzre: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, unknown_fzre: _Optional[_Iterable[int]] = ...) -> None: ...
    class UnknownKxz(_message.Message):
        __slots__ = ("unknown_fzri",)
        UNKNOWN_FZRI_FIELD_NUMBER: _ClassVar[int]
        unknown_fzri: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, unknown_fzri: _Optional[_Iterable[int]] = ...) -> None: ...
    UNKNOWN_FZRP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZRQ_FIELD_NUMBER: _ClassVar[int]
    unknown_fzrp: UnknownKyb.UnknownKxz
    unknown_fzrq: UnknownKyb.UnknownKxw
    def __init__(self, unknown_fzrp: _Optional[_Union[UnknownKyb.UnknownKxz, _Mapping]] = ..., unknown_fzrq: _Optional[_Union[UnknownKyb.UnknownKxw, _Mapping]] = ...) -> None: ...

class UnknownKyf(_message.Message):
    __slots__ = ("unknown_fzsh",)
    UNKNOWN_FZSH_FIELD_NUMBER: _ClassVar[int]
    unknown_fzsh: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, unknown_fzsh: _Optional[_Iterable[int]] = ...) -> None: ...

class UnknownKzl(_message.Message):
    __slots__ = ("unknown_fzxl", "unknown_fzxm")
    class UnknownKyi(_message.Message):
        __slots__ = ("unknown_fzsl", "unknown_fzsm", "unknown_fzsn", "unknown_fzso")
        UNKNOWN_FZSL_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZSM_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZSN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZSO_FIELD_NUMBER: _ClassVar[int]
        unknown_fzsl: UnknownKzl.UnknownKzi
        unknown_fzsm: UnknownKzl.UnknownKyu
        unknown_fzsn: UnknownKzl.UnknownKyr
        unknown_fzso: int
        def __init__(self, unknown_fzsl: _Optional[_Union[UnknownKzl.UnknownKzi, _Mapping]] = ..., unknown_fzsm: _Optional[_Union[UnknownKzl.UnknownKyu, _Mapping]] = ..., unknown_fzsn: _Optional[_Union[UnknownKzl.UnknownKyr, _Mapping]] = ..., unknown_fzso: _Optional[int] = ...) -> None: ...
    class UnknownKyl(_message.Message):
        __slots__ = ("unknown_fzst",)
        UNKNOWN_FZST_FIELD_NUMBER: _ClassVar[int]
        unknown_fzst: int
        def __init__(self, unknown_fzst: _Optional[int] = ...) -> None: ...
    class UnknownKyr(_message.Message):
        __slots__ = ("unknown_fztv", "unknown_fztx", "unknown_fztz", "unknown_fzua", "unknown_fzub", "unknown_fzuc", "unknown_fzud", "unknown_fzue")
        class UnknownFztzEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: int
            def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
        class UnknownKym(_message.Message):
            __slots__ = ("unknown_fzsz", "unknown_fzta")
            UNKNOWN_FZSZ_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FZTA_FIELD_NUMBER: _ClassVar[int]
            unknown_fzsz: int
            unknown_fzta: str
            def __init__(self, unknown_fzsz: _Optional[int] = ..., unknown_fzta: _Optional[str] = ...) -> None: ...
        class UnknownKyn(_message.Message):
            __slots__ = ("unknown_fzte", "unknown_fztf", "unknown_fztg")
            UNKNOWN_FZTE_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FZTF_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FZTG_FIELD_NUMBER: _ClassVar[int]
            unknown_fzte: int
            unknown_fztf: _common_pb2.SocialEmblem
            unknown_fztg: str
            def __init__(self, unknown_fzte: _Optional[int] = ..., unknown_fztf: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ..., unknown_fztg: _Optional[str] = ...) -> None: ...
        class UnknownKyo(_message.Message):
            __slots__ = ("unknown_fztk", "unknown_fztl", "unknown_fztm")
            UNKNOWN_FZTK_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FZTL_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FZTM_FIELD_NUMBER: _ClassVar[int]
            unknown_fztk: str
            unknown_fztl: str
            unknown_fztm: _common_pb2.SocialEmblem
            def __init__(self, unknown_fztk: _Optional[str] = ..., unknown_fztl: _Optional[str] = ..., unknown_fztm: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ...) -> None: ...
        class UnknownKyp(_message.Message):
            __slots__ = ("unknown_fztq",)
            UNKNOWN_FZTQ_FIELD_NUMBER: _ClassVar[int]
            unknown_fztq: _common_pb2.MapExtendedCoordinates
            def __init__(self, unknown_fztq: _Optional[_Union[_common_pb2.MapExtendedCoordinates, _Mapping]] = ...) -> None: ...
        UNKNOWN_FZTV_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZTX_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZTZ_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZUA_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZUB_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZUC_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZUD_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZUE_FIELD_NUMBER: _ClassVar[int]
        unknown_fztv: _common_pb2.UnknownLhp
        unknown_fztx: UnknownKzl.UnknownKyr.UnknownKyn
        unknown_fztz: _containers.ScalarMap[int, int]
        unknown_fzua: UnknownKzl.UnknownKyr.UnknownKym
        unknown_fzub: _containers.RepeatedScalarFieldContainer[int]
        unknown_fzuc: UnknownKzl.UnknownKyr.UnknownKyp
        unknown_fzud: UnknownKzl.UnknownKyr.UnknownKyo
        unknown_fzue: int
        def __init__(self, unknown_fztv: _Optional[_Union[_common_pb2.UnknownLhp, _Mapping]] = ..., unknown_fztx: _Optional[_Union[UnknownKzl.UnknownKyr.UnknownKyn, _Mapping]] = ..., unknown_fztz: _Optional[_Mapping[int, int]] = ..., unknown_fzua: _Optional[_Union[UnknownKzl.UnknownKyr.UnknownKym, _Mapping]] = ..., unknown_fzub: _Optional[_Iterable[int]] = ..., unknown_fzuc: _Optional[_Union[UnknownKzl.UnknownKyr.UnknownKyp, _Mapping]] = ..., unknown_fzud: _Optional[_Union[UnknownKzl.UnknownKyr.UnknownKyo, _Mapping]] = ..., unknown_fzue: _Optional[int] = ...) -> None: ...
    class UnknownKyu(_message.Message):
        __slots__ = ("unknown_fzun", "unknown_fzuo", "unknown_fzup")
        class UnknownFzunEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: int
            def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
        class UnknownFzuoEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: int
            def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
        UNKNOWN_FZUN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZUO_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZUP_FIELD_NUMBER: _ClassVar[int]
        unknown_fzun: _containers.ScalarMap[int, int]
        unknown_fzuo: _containers.ScalarMap[int, int]
        unknown_fzup: _preset_pb2.CharacteristicsInfo
        def __init__(self, unknown_fzun: _Optional[_Mapping[int, int]] = ..., unknown_fzuo: _Optional[_Mapping[int, int]] = ..., unknown_fzup: _Optional[_Union[_preset_pb2.CharacteristicsInfo, _Mapping]] = ...) -> None: ...
    class UnknownKzi(_message.Message):
        __slots__ = ("unknown_fzxd",)
        class UnknownKzg(_message.Message):
            __slots__ = ("unknown_fzwu", "unknown_fzwv", "unknown_fzww", "unknown_fzwx")
            class UnknownKyw(_message.Message):
                __slots__ = ("unknown_fzuu", "unknown_fzuv")
                UNKNOWN_FZUU_FIELD_NUMBER: _ClassVar[int]
                UNKNOWN_FZUV_FIELD_NUMBER: _ClassVar[int]
                unknown_fzuu: int
                unknown_fzuv: int
                def __init__(self, unknown_fzuu: _Optional[int] = ..., unknown_fzuv: _Optional[int] = ...) -> None: ...
            class UnknownKyx(_message.Message):
                __slots__ = ("unknown_fzuz", "unknown_fzva")
                UNKNOWN_FZUZ_FIELD_NUMBER: _ClassVar[int]
                UNKNOWN_FZVA_FIELD_NUMBER: _ClassVar[int]
                unknown_fzuz: int
                unknown_fzva: int
                def __init__(self, unknown_fzuz: _Optional[int] = ..., unknown_fzva: _Optional[int] = ...) -> None: ...
            class UnknownKyy(_message.Message):
                __slots__ = ("unknown_fzve", "unknown_fzvf", "unknown_fzvg", "unknown_fzvh")
                UNKNOWN_FZVE_FIELD_NUMBER: _ClassVar[int]
                UNKNOWN_FZVF_FIELD_NUMBER: _ClassVar[int]
                UNKNOWN_FZVG_FIELD_NUMBER: _ClassVar[int]
                UNKNOWN_FZVH_FIELD_NUMBER: _ClassVar[int]
                unknown_fzve: int
                unknown_fzvf: int
                unknown_fzvg: int
                unknown_fzvh: int
                def __init__(self, unknown_fzve: _Optional[int] = ..., unknown_fzvf: _Optional[int] = ..., unknown_fzvg: _Optional[int] = ..., unknown_fzvh: _Optional[int] = ...) -> None: ...
            class UnknownKze(_message.Message):
                __slots__ = ("unknown_fzwq",)
                UNKNOWN_FZWQ_FIELD_NUMBER: _ClassVar[int]
                unknown_fzwq: _containers.RepeatedScalarFieldContainer[int]
                def __init__(self, unknown_fzwq: _Optional[_Iterable[int]] = ...) -> None: ...
            UNKNOWN_FZWU_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FZWV_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FZWW_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FZWX_FIELD_NUMBER: _ClassVar[int]
            unknown_fzwu: UnknownKzl.UnknownKzi.UnknownKzg.UnknownKyy
            unknown_fzwv: UnknownKzl.UnknownKzi.UnknownKzg.UnknownKyw
            unknown_fzww: UnknownKzl.UnknownKzi.UnknownKzg.UnknownKze
            unknown_fzwx: UnknownKzl.UnknownKzi.UnknownKzg.UnknownKyx
            def __init__(self, unknown_fzwu: _Optional[_Union[UnknownKzl.UnknownKzi.UnknownKzg.UnknownKyy, _Mapping]] = ..., unknown_fzwv: _Optional[_Union[UnknownKzl.UnknownKzi.UnknownKzg.UnknownKyw, _Mapping]] = ..., unknown_fzww: _Optional[_Union[UnknownKzl.UnknownKzi.UnknownKzg.UnknownKze, _Mapping]] = ..., unknown_fzwx: _Optional[_Union[UnknownKzl.UnknownKzi.UnknownKzg.UnknownKyx, _Mapping]] = ...) -> None: ...
        UNKNOWN_FZXD_FIELD_NUMBER: _ClassVar[int]
        unknown_fzxd: _containers.RepeatedCompositeFieldContainer[UnknownKzl.UnknownKzi.UnknownKzg]
        def __init__(self, unknown_fzxd: _Optional[_Iterable[_Union[UnknownKzl.UnknownKzi.UnknownKzg, _Mapping]]] = ...) -> None: ...
    UNKNOWN_FZXL_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZXM_FIELD_NUMBER: _ClassVar[int]
    unknown_fzxl: UnknownKzl.UnknownKyi
    unknown_fzxm: UnknownKzl.UnknownKyl
    def __init__(self, unknown_fzxl: _Optional[_Union[UnknownKzl.UnknownKyi, _Mapping]] = ..., unknown_fzxm: _Optional[_Union[UnknownKzl.UnknownKyl, _Mapping]] = ...) -> None: ...

class UnknownKzs(_message.Message):
    __slots__ = ("unknown_fzyc", "unknown_fzyd")
    class UnknownKzn(_message.Message):
        __slots__ = ("unknown_fzxs",)
        UNKNOWN_FZXS_FIELD_NUMBER: _ClassVar[int]
        unknown_fzxs: _cosmetic_pb2.Outfit
        def __init__(self, unknown_fzxs: _Optional[_Union[_cosmetic_pb2.Outfit, _Mapping]] = ...) -> None: ...
    UNKNOWN_FZYC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZYD_FIELD_NUMBER: _ClassVar[int]
    unknown_fzyc: UnknownKzs.UnknownKzn
    unknown_fzyd: int
    def __init__(self, unknown_fzyc: _Optional[_Union[UnknownKzs.UnknownKzn, _Mapping]] = ..., unknown_fzyd: _Optional[int] = ...) -> None: ...

class UnknownKzu(_message.Message):
    __slots__ = ("unknown_fzym", "unknown_fzyp", "unknown_fzyr", "unknown_fzyt", "unknown_fzyu", "unknown_fzyv", "unknown_fzyw", "unknown_fzyx", "unknown_fzyy", "unknown_fzyz", "unknown_fzzc")
    UNKNOWN_FZYM_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZYP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZYR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZYT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZYU_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZYV_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZYW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZYX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZYY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZYZ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZZC_FIELD_NUMBER: _ClassVar[int]
    unknown_fzym: int
    unknown_fzyp: int
    unknown_fzyr: int
    unknown_fzyt: bool
    unknown_fzyu: int
    unknown_fzyv: _common_pb2.EntityLook
    unknown_fzyw: int
    unknown_fzyx: int
    unknown_fzyy: str
    unknown_fzyz: int
    unknown_fzzc: _common_pb2.EntityLook
    def __init__(self, unknown_fzym: _Optional[int] = ..., unknown_fzyp: _Optional[int] = ..., unknown_fzyr: _Optional[int] = ..., unknown_fzyt: bool = ..., unknown_fzyu: _Optional[int] = ..., unknown_fzyv: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ..., unknown_fzyw: _Optional[int] = ..., unknown_fzyx: _Optional[int] = ..., unknown_fzyy: _Optional[str] = ..., unknown_fzyz: _Optional[int] = ..., unknown_fzzc: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ...) -> None: ...

class PlayerInfoEvent(_message.Message):
    __slots__ = ("unknown_fzzu", "unknown_fzzv")
    class UnknownKzy(_message.Message):
        __slots__ = ("unknown_fzzg", "unknown_fzzj", "unknown_fzzk")
        UNKNOWN_FZZG_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZZJ_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FZZK_FIELD_NUMBER: _ClassVar[int]
        unknown_fzzg: _containers.RepeatedScalarFieldContainer[int]
        unknown_fzzj: str
        unknown_fzzk: UnknownKzu
        def __init__(self, unknown_fzzg: _Optional[_Iterable[int]] = ..., unknown_fzzj: _Optional[str] = ..., unknown_fzzk: _Optional[_Union[UnknownKzu, _Mapping]] = ...) -> None: ...
    class UnknownLab(_message.Message):
        __slots__ = ("unknown_fzzp",)
        UNKNOWN_FZZP_FIELD_NUMBER: _ClassVar[int]
        unknown_fzzp: int
        def __init__(self, unknown_fzzp: _Optional[int] = ...) -> None: ...
    UNKNOWN_FZZU_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZZV_FIELD_NUMBER: _ClassVar[int]
    unknown_fzzu: PlayerInfoEvent.UnknownLab
    unknown_fzzv: PlayerInfoEvent.UnknownKzy
    def __init__(self, unknown_fzzu: _Optional[_Union[PlayerInfoEvent.UnknownLab, _Mapping]] = ..., unknown_fzzv: _Optional[_Union[PlayerInfoEvent.UnknownKzy, _Mapping]] = ...) -> None: ...

class UnknownLag(_message.Message):
    __slots__ = ("unknown_gaab", "unknown_gaac")
    UNKNOWN_GAAB_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GAAC_FIELD_NUMBER: _ClassVar[int]
    unknown_gaab: int
    unknown_gaac: int
    def __init__(self, unknown_gaab: _Optional[int] = ..., unknown_gaac: _Optional[int] = ...) -> None: ...

class PlayerInfoRequest(_message.Message):
    __slots__ = ("unknown_fzpm",)
    UNKNOWN_FZPM_FIELD_NUMBER: _ClassVar[int]
    unknown_fzpm: int
    def __init__(self, unknown_fzpm: _Optional[int] = ...) -> None: ...
