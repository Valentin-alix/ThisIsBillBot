import common_pb2 as _common_pb2
import game_message_pb2 as _game_message_pb2
import report_pb2 as _report_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownHql(_message.Message):
    __slots__ = ("unknown_fngc", "unknown_fngd")
    class UnknownFngdEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: UnknownHqu
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownHqu, _Mapping]] = ...) -> None: ...
    UNKNOWN_FNGC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNGD_FIELD_NUMBER: _ClassVar[int]
    unknown_fngc: UnknownHta
    unknown_fngd: _containers.MessageMap[str, UnknownHqu]
    def __init__(self, unknown_fngc: _Optional[_Union[UnknownHta, _Mapping]] = ..., unknown_fngd: _Optional[_Mapping[str, UnknownHqu]] = ...) -> None: ...

class UnknownHta(_message.Message):
    __slots__ = ("unknown_fnpc", "unknown_fnpd", "unknown_fnpe")
    class UnknownFnpeEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: UnknownHqu
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownHqu, _Mapping]] = ...) -> None: ...
    UNKNOWN_FNPC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNPD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNPE_FIELD_NUMBER: _ClassVar[int]
    unknown_fnpc: _containers.RepeatedCompositeFieldContainer[UnknownHtz]
    unknown_fnpd: _containers.RepeatedScalarFieldContainer[int]
    unknown_fnpe: _containers.MessageMap[str, UnknownHqu]
    def __init__(self, unknown_fnpc: _Optional[_Iterable[_Union[UnknownHtz, _Mapping]]] = ..., unknown_fnpd: _Optional[_Iterable[int]] = ..., unknown_fnpe: _Optional[_Mapping[str, UnknownHqu]] = ...) -> None: ...

class UnknownHtz(_message.Message):
    __slots__ = ("unknown_fnrw", "unknown_fnrx")
    UNKNOWN_FNRW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNRX_FIELD_NUMBER: _ClassVar[int]
    unknown_fnrw: int
    unknown_fnrx: int
    def __init__(self, unknown_fnrw: _Optional[int] = ..., unknown_fnrx: _Optional[int] = ...) -> None: ...

class UnknownHqu(_message.Message):
    __slots__ = ("unknown_fnhc", "unknown_fnhd", "unknown_fnhe", "unknown_fnhf", "unknown_fnhg", "unknown_fnhi", "unknown_fnhj", "unknown_fnhk", "unknown_fnhl", "unknown_fnhm", "unknown_fnhn", "unknown_fnho")
    class UnknownHqr(_message.Message):
        __slots__ = ("unknown_fngr", "unknown_fngt")
        UNKNOWN_FNGR_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNGT_FIELD_NUMBER: _ClassVar[int]
        unknown_fngr: int
        unknown_fngt: int
        def __init__(self, unknown_fngr: _Optional[int] = ..., unknown_fngt: _Optional[int] = ...) -> None: ...
    class UnknownHqs(_message.Message):
        __slots__ = ("unknown_fngx", "unknown_fngy")
        UNKNOWN_FNGX_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNGY_FIELD_NUMBER: _ClassVar[int]
        unknown_fngx: int
        unknown_fngy: int
        def __init__(self, unknown_fngx: _Optional[int] = ..., unknown_fngy: _Optional[int] = ...) -> None: ...
    UNKNOWN_FNHC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNHD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNHE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNHF_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNHG_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNHI_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNHJ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNHK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNHL_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNHM_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNHN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNHO_FIELD_NUMBER: _ClassVar[int]
    unknown_fnhc: int
    unknown_fnhd: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectEffect]
    unknown_fnhe: int
    unknown_fnhf: bool
    unknown_fnhg: str
    unknown_fnhi: _containers.RepeatedCompositeFieldContainer[UnknownHqu.UnknownHqr]
    unknown_fnhj: bool
    unknown_fnhk: _containers.RepeatedScalarFieldContainer[int]
    unknown_fnhl: UnknownHqu.UnknownHqs
    unknown_fnhm: bool
    unknown_fnhn: int
    unknown_fnho: int
    def __init__(self, unknown_fnhc: _Optional[int] = ..., unknown_fnhd: _Optional[_Iterable[_Union[_common_pb2.ObjectEffect, _Mapping]]] = ..., unknown_fnhe: _Optional[int] = ..., unknown_fnhf: bool = ..., unknown_fnhg: _Optional[str] = ..., unknown_fnhi: _Optional[_Iterable[_Union[UnknownHqu.UnknownHqr, _Mapping]]] = ..., unknown_fnhj: bool = ..., unknown_fnhk: _Optional[_Iterable[int]] = ..., unknown_fnhl: _Optional[_Union[UnknownHqu.UnknownHqs, _Mapping]] = ..., unknown_fnhm: bool = ..., unknown_fnhn: _Optional[int] = ..., unknown_fnho: _Optional[int] = ...) -> None: ...

class UnknownHqp(_message.Message):
    __slots__ = ("unknown_fngk",)
    UNKNOWN_FNGK_FIELD_NUMBER: _ClassVar[int]
    unknown_fngk: int
    def __init__(self, unknown_fngk: _Optional[int] = ...) -> None: ...

class UnknownHqv(_message.Message):
    __slots__ = ("unknown_fnhs", "unknown_fnht")
    UNKNOWN_FNHS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNHT_FIELD_NUMBER: _ClassVar[int]
    unknown_fnhs: str
    unknown_fnht: str
    def __init__(self, unknown_fnhs: _Optional[str] = ..., unknown_fnht: _Optional[str] = ...) -> None: ...

class UnknownHqw(_message.Message):
    __slots__ = ("unknown_fnhx",)
    UNKNOWN_FNHX_FIELD_NUMBER: _ClassVar[int]
    unknown_fnhx: int
    def __init__(self, unknown_fnhx: _Optional[int] = ...) -> None: ...

class PaddockInformationEvent(_message.Message):
    __slots__ = ("unknown_fnin", "unknown_fnip")
    class UnknownHra(_message.Message):
        __slots__ = ("unknown_fnif", "unknown_fnig")
        class UnknownFnifValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_FNIF_VALUE_UNSPECIFIED: _ClassVar[PaddockInformationEvent.UnknownHra.UnknownFnifValue]
        UNKNOWN_FNIF_VALUE_UNSPECIFIED: PaddockInformationEvent.UnknownHra.UnknownFnifValue
        UNKNOWN_FNIF_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNIG_FIELD_NUMBER: _ClassVar[int]
        unknown_fnif: PaddockInformationEvent.UnknownHra.UnknownFnifValue
        unknown_fnig: UnknownHta
        def __init__(self, unknown_fnif: _Optional[_Union[PaddockInformationEvent.UnknownHra.UnknownFnifValue, str]] = ..., unknown_fnig: _Optional[_Union[UnknownHta, _Mapping]] = ...) -> None: ...
    UNKNOWN_FNIN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNIP_FIELD_NUMBER: _ClassVar[int]
    unknown_fnin: int
    unknown_fnip: PaddockInformationEvent.UnknownHra
    def __init__(self, unknown_fnin: _Optional[int] = ..., unknown_fnip: _Optional[_Union[PaddockInformationEvent.UnknownHra, _Mapping]] = ...) -> None: ...

class UnknownHrh(_message.Message):
    __slots__ = ("unknown_fniz", "unknown_fnja")
    class UnknownHrf(_message.Message):
        __slots__ = ("unknown_fniv",)
        UNKNOWN_FNIV_FIELD_NUMBER: _ClassVar[int]
        unknown_fniv: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, unknown_fniv: _Optional[_Iterable[str]] = ...) -> None: ...
    UNKNOWN_FNIZ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNJA_FIELD_NUMBER: _ClassVar[int]
    unknown_fniz: UnknownHrh.UnknownHrf
    unknown_fnja: int
    def __init__(self, unknown_fniz: _Optional[_Union[UnknownHrh.UnknownHrf, _Mapping]] = ..., unknown_fnja: _Optional[int] = ...) -> None: ...

class PaddockInformationRequest(_message.Message):
    __slots__ = ("unknown_fnjj", "unknown_fnjk")
    UNKNOWN_FNJJ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNJK_FIELD_NUMBER: _ClassVar[int]
    unknown_fnjj: int
    unknown_fnjk: int
    def __init__(self, unknown_fnjj: _Optional[int] = ..., unknown_fnjk: _Optional[int] = ...) -> None: ...

class UnknownHrz(_message.Message):
    __slots__ = ("unknown_fnlk", "unknown_fnll")
    class UnknownHrq(_message.Message):
        __slots__ = ("unknown_fnjt", "unknown_fnju", "unknown_fnjv", "unknown_fnjw", "unknown_fnjx", "unknown_fnjz", "unknown_fnka")
        UNKNOWN_FNJT_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNJU_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNJV_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNJW_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNJX_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNJZ_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNKA_FIELD_NUMBER: _ClassVar[int]
        unknown_fnjt: UnknownHrz.UnknownHrx
        unknown_fnju: _containers.RepeatedCompositeFieldContainer[UnknownHrz.UnknownHrt]
        unknown_fnjv: _containers.RepeatedCompositeFieldContainer[UnknownHrz.UnknownHrt]
        unknown_fnjw: int
        unknown_fnjx: _containers.RepeatedCompositeFieldContainer[UnknownHrz.UnknownHru]
        unknown_fnjz: bool
        unknown_fnka: int
        def __init__(self, unknown_fnjt: _Optional[_Union[UnknownHrz.UnknownHrx, _Mapping]] = ..., unknown_fnju: _Optional[_Iterable[_Union[UnknownHrz.UnknownHrt, _Mapping]]] = ..., unknown_fnjv: _Optional[_Iterable[_Union[UnknownHrz.UnknownHrt, _Mapping]]] = ..., unknown_fnjw: _Optional[int] = ..., unknown_fnjx: _Optional[_Iterable[_Union[UnknownHrz.UnknownHru, _Mapping]]] = ..., unknown_fnjz: bool = ..., unknown_fnka: _Optional[int] = ...) -> None: ...
    class UnknownHrt(_message.Message):
        __slots__ = ("unknown_fnkp", "unknown_fnkq")
        UNKNOWN_FNKP_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNKQ_FIELD_NUMBER: _ClassVar[int]
        unknown_fnkp: float
        unknown_fnkq: int
        def __init__(self, unknown_fnkp: _Optional[float] = ..., unknown_fnkq: _Optional[int] = ...) -> None: ...
    class UnknownHru(_message.Message):
        __slots__ = ("unknown_fnku", "unknown_fnkv", "unknown_fnkw")
        UNKNOWN_FNKU_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNKV_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNKW_FIELD_NUMBER: _ClassVar[int]
        unknown_fnku: bool
        unknown_fnkv: int
        unknown_fnkw: float
        def __init__(self, unknown_fnku: bool = ..., unknown_fnkv: _Optional[int] = ..., unknown_fnkw: _Optional[float] = ...) -> None: ...
    class UnknownHrx(_message.Message):
        __slots__ = ("unknown_fnla", "unknown_fnlc", "unknown_fnld", "unknown_fnle")
        UNKNOWN_FNLA_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNLC_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNLD_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNLE_FIELD_NUMBER: _ClassVar[int]
        unknown_fnla: int
        unknown_fnlc: int
        unknown_fnld: int
        unknown_fnle: int
        def __init__(self, unknown_fnla: _Optional[int] = ..., unknown_fnlc: _Optional[int] = ..., unknown_fnld: _Optional[int] = ..., unknown_fnle: _Optional[int] = ...) -> None: ...
    UNKNOWN_FNLK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNLL_FIELD_NUMBER: _ClassVar[int]
    unknown_fnlk: UnknownHrz.UnknownHrq
    unknown_fnll: int
    def __init__(self, unknown_fnlk: _Optional[_Union[UnknownHrz.UnknownHrq, _Mapping]] = ..., unknown_fnll: _Optional[int] = ...) -> None: ...

class UnknownHsa(_message.Message):
    __slots__ = ("unknown_fnlr", "unknown_fnls", "unknown_fnlt", "unknown_fnlv")
    UNKNOWN_FNLR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNLS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNLT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNLV_FIELD_NUMBER: _ClassVar[int]
    unknown_fnlr: str
    unknown_fnls: str
    unknown_fnlt: int
    unknown_fnlv: str
    def __init__(self, unknown_fnlr: _Optional[str] = ..., unknown_fnls: _Optional[str] = ..., unknown_fnlt: _Optional[int] = ..., unknown_fnlv: _Optional[str] = ...) -> None: ...

class UnknownHsb(_message.Message):
    __slots__ = ("unknown_fnlz",)
    UNKNOWN_FNLZ_FIELD_NUMBER: _ClassVar[int]
    unknown_fnlz: int
    def __init__(self, unknown_fnlz: _Optional[int] = ...) -> None: ...

class UnknownHse(_message.Message):
    __slots__ = ("unknown_fnmh", "unknown_fnmj")
    UNKNOWN_FNMH_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNMJ_FIELD_NUMBER: _ClassVar[int]
    unknown_fnmh: _containers.RepeatedScalarFieldContainer[int]
    unknown_fnmj: int
    def __init__(self, unknown_fnmh: _Optional[_Iterable[int]] = ..., unknown_fnmj: _Optional[int] = ...) -> None: ...

class UnknownHsm(_message.Message):
    __slots__ = ("unknown_fnmx", "unknown_fnmy")
    class UnknownHsk(_message.Message):
        __slots__ = ("unknown_fnmr", "unknown_fnms")
        UNKNOWN_FNMR_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNMS_FIELD_NUMBER: _ClassVar[int]
        unknown_fnmr: UnknownHqu
        unknown_fnms: str
        def __init__(self, unknown_fnmr: _Optional[_Union[UnknownHqu, _Mapping]] = ..., unknown_fnms: _Optional[str] = ...) -> None: ...
    UNKNOWN_FNMX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNMY_FIELD_NUMBER: _ClassVar[int]
    unknown_fnmx: UnknownHsm.UnknownHsk
    unknown_fnmy: int
    def __init__(self, unknown_fnmx: _Optional[_Union[UnknownHsm.UnknownHsk, _Mapping]] = ..., unknown_fnmy: _Optional[int] = ...) -> None: ...

class UnknownHsn(_message.Message):
    __slots__ = ("unknown_fnne", "unknown_fnnf")
    UNKNOWN_FNNE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNNF_FIELD_NUMBER: _ClassVar[int]
    unknown_fnne: int
    unknown_fnnf: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, unknown_fnne: _Optional[int] = ..., unknown_fnnf: _Optional[_Iterable[str]] = ...) -> None: ...

class UnknownHsu(_message.Message):
    __slots__ = ("unknown_fnnt", "unknown_fnnv")
    class UnknownHss(_message.Message):
        __slots__ = ("unknown_fnnj", "unknown_fnnk", "unknown_fnnl", "unknown_fnnm", "unknown_fnnn")
        class UnknownFnnkEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: UnknownHqu
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownHqu, _Mapping]] = ...) -> None: ...
        class UnknownFnnnEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: UnknownHqu
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownHqu, _Mapping]] = ...) -> None: ...
        UNKNOWN_FNNJ_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNNK_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNNL_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNNM_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNNN_FIELD_NUMBER: _ClassVar[int]
        unknown_fnnj: int
        unknown_fnnk: _containers.MessageMap[str, UnknownHqu]
        unknown_fnnl: int
        unknown_fnnm: bool
        unknown_fnnn: _containers.MessageMap[str, UnknownHqu]
        def __init__(self, unknown_fnnj: _Optional[int] = ..., unknown_fnnk: _Optional[_Mapping[str, UnknownHqu]] = ..., unknown_fnnl: _Optional[int] = ..., unknown_fnnm: bool = ..., unknown_fnnn: _Optional[_Mapping[str, UnknownHqu]] = ...) -> None: ...
    UNKNOWN_FNNT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNNV_FIELD_NUMBER: _ClassVar[int]
    unknown_fnnt: int
    unknown_fnnv: UnknownHsu.UnknownHss
    def __init__(self, unknown_fnnt: _Optional[int] = ..., unknown_fnnv: _Optional[_Union[UnknownHsu.UnknownHss, _Mapping]] = ...) -> None: ...

class UnknownHsv(_message.Message):
    __slots__ = ("unknown_fnoa",)
    UNKNOWN_FNOA_FIELD_NUMBER: _ClassVar[int]
    unknown_fnoa: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, unknown_fnoa: _Optional[_Iterable[str]] = ...) -> None: ...

class UnknownHsy(_message.Message):
    __slots__ = ("unknown_fnou",)
    class UnknownFnouEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: bool
        def __init__(self, key: _Optional[int] = ..., value: bool = ...) -> None: ...
    UNKNOWN_FNOU_FIELD_NUMBER: _ClassVar[int]
    unknown_fnou: _containers.ScalarMap[int, bool]
    def __init__(self, unknown_fnou: _Optional[_Mapping[int, bool]] = ...) -> None: ...

class UnknownHsz(_message.Message):
    __slots__ = ("unknown_fnoy",)
    UNKNOWN_FNOY_FIELD_NUMBER: _ClassVar[int]
    unknown_fnoy: int
    def __init__(self, unknown_fnoy: _Optional[int] = ...) -> None: ...

class UnknownHtf(_message.Message):
    __slots__ = ("unknown_fnpn", "unknown_fnpp")
    class UnknownHtd(_message.Message):
        __slots__ = ("unknown_fnpi",)
        UNKNOWN_FNPI_FIELD_NUMBER: _ClassVar[int]
        unknown_fnpi: _containers.RepeatedCompositeFieldContainer[UnknownHtz]
        def __init__(self, unknown_fnpi: _Optional[_Iterable[_Union[UnknownHtz, _Mapping]]] = ...) -> None: ...
    UNKNOWN_FNPN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNPP_FIELD_NUMBER: _ClassVar[int]
    unknown_fnpn: int
    unknown_fnpp: UnknownHtf.UnknownHtd
    def __init__(self, unknown_fnpn: _Optional[int] = ..., unknown_fnpp: _Optional[_Union[UnknownHtf.UnknownHtd, _Mapping]] = ...) -> None: ...

class UnknownHti(_message.Message):
    __slots__ = ("unknown_fnpu",)
    class UnknownFnpuEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_FNPU_FIELD_NUMBER: _ClassVar[int]
    unknown_fnpu: _containers.ScalarMap[str, int]
    def __init__(self, unknown_fnpu: _Optional[_Mapping[str, int]] = ...) -> None: ...

class UnknownHtl(_message.Message):
    __slots__ = ("unknown_fnpy",)
    class UnknownFnpyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_FNPY_FIELD_NUMBER: _ClassVar[int]
    unknown_fnpy: _containers.ScalarMap[int, int]
    def __init__(self, unknown_fnpy: _Optional[_Mapping[int, int]] = ...) -> None: ...

class MountBoostResponse(_message.Message):
    __slots__ = ("unknown_fnqw", "unknown_fnqx")
    class UnknownHtp(_message.Message):
        __slots__ = ("unknown_fnqq",)
        UNKNOWN_FNQQ_FIELD_NUMBER: _ClassVar[int]
        unknown_fnqq: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, unknown_fnqq: _Optional[_Iterable[int]] = ...) -> None: ...
    UNKNOWN_FNQW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNQX_FIELD_NUMBER: _ClassVar[int]
    unknown_fnqw: MountBoostResponse.UnknownHtp
    unknown_fnqx: int
    def __init__(self, unknown_fnqw: _Optional[_Union[MountBoostResponse.UnknownHtp, _Mapping]] = ..., unknown_fnqx: _Optional[int] = ...) -> None: ...

class UnknownHtu(_message.Message):
    __slots__ = ("unknown_fnrd", "unknown_fnre", "unknown_fnrg", "unknown_fnri")
    UNKNOWN_FNRD_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNRE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNRG_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNRI_FIELD_NUMBER: _ClassVar[int]
    unknown_fnrd: str
    unknown_fnre: int
    unknown_fnrg: str
    unknown_fnri: str
    def __init__(self, unknown_fnrd: _Optional[str] = ..., unknown_fnre: _Optional[int] = ..., unknown_fnrg: _Optional[str] = ..., unknown_fnri: _Optional[str] = ...) -> None: ...

class UnknownHty(_message.Message):
    __slots__ = ("unknown_fnrr", "unknown_fnrs")
    class UnknownFnrrEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    class UnknownFnrsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_FNRR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNRS_FIELD_NUMBER: _ClassVar[int]
    unknown_fnrr: _containers.ScalarMap[int, int]
    unknown_fnrs: _containers.ScalarMap[int, int]
    def __init__(self, unknown_fnrr: _Optional[_Mapping[int, int]] = ..., unknown_fnrs: _Optional[_Mapping[int, int]] = ...) -> None: ...

class UnknownHua(_message.Message):
    __slots__ = ("unknown_fnsb",)
    UNKNOWN_FNSB_FIELD_NUMBER: _ClassVar[int]
    unknown_fnsb: UnknownHta
    def __init__(self, unknown_fnsb: _Optional[_Union[UnknownHta, _Mapping]] = ...) -> None: ...

class UnknownHub(_message.Message):
    __slots__ = ("unknown_fnsg",)
    class UnknownFnsgEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_FNSG_FIELD_NUMBER: _ClassVar[int]
    unknown_fnsg: _containers.ScalarMap[int, int]
    def __init__(self, unknown_fnsg: _Optional[_Mapping[int, int]] = ...) -> None: ...

class UnknownHuh(_message.Message):
    __slots__ = ("unknown_fnsu", "unknown_fnsv", "unknown_fnsx")
    UNKNOWN_FNSU_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNSV_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNSX_FIELD_NUMBER: _ClassVar[int]
    unknown_fnsu: _containers.RepeatedScalarFieldContainer[str]
    unknown_fnsv: int
    unknown_fnsx: str
    def __init__(self, unknown_fnsu: _Optional[_Iterable[str]] = ..., unknown_fnsv: _Optional[int] = ..., unknown_fnsx: _Optional[str] = ...) -> None: ...

class UnknownHum(_message.Message):
    __slots__ = ("unknown_fnth", "unknown_fntj")
    class UnknownHuk(_message.Message):
        __slots__ = ("unknown_fntc",)
        UNKNOWN_FNTC_FIELD_NUMBER: _ClassVar[int]
        unknown_fntc: _containers.RepeatedCompositeFieldContainer[UnknownHtz]
        def __init__(self, unknown_fntc: _Optional[_Iterable[_Union[UnknownHtz, _Mapping]]] = ...) -> None: ...
    UNKNOWN_FNTH_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNTJ_FIELD_NUMBER: _ClassVar[int]
    unknown_fnth: int
    unknown_fntj: UnknownHum.UnknownHuk
    def __init__(self, unknown_fnth: _Optional[int] = ..., unknown_fntj: _Optional[_Union[UnknownHum.UnknownHuk, _Mapping]] = ...) -> None: ...

class MountBoostRequest(_message.Message):
    __slots__ = ("unknown_fnto",)
    UNKNOWN_FNTO_FIELD_NUMBER: _ClassVar[int]
    unknown_fnto: int
    def __init__(self, unknown_fnto: _Optional[int] = ...) -> None: ...

class UnknownHur(_message.Message):
    __slots__ = ("unknown_fnuc",)
    class UnknownFnucEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_FNUC_FIELD_NUMBER: _ClassVar[int]
    unknown_fnuc: _containers.ScalarMap[str, int]
    def __init__(self, unknown_fnuc: _Optional[_Mapping[str, int]] = ...) -> None: ...

class PaddockSlotsEvent(_message.Message):
    __slots__ = ("unknown_fnug",)
    class UnknownFnugEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: bool
        def __init__(self, key: _Optional[int] = ..., value: bool = ...) -> None: ...
    UNKNOWN_FNUG_FIELD_NUMBER: _ClassVar[int]
    unknown_fnug: _containers.ScalarMap[int, bool]
    def __init__(self, unknown_fnug: _Optional[_Mapping[int, bool]] = ...) -> None: ...

class UnknownHut(_message.Message):
    __slots__ = ("unknown_fnuk", "unknown_fnul", "unknown_fnum")
    UNKNOWN_FNUK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNUL_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNUM_FIELD_NUMBER: _ClassVar[int]
    unknown_fnuk: str
    unknown_fnul: int
    unknown_fnum: str
    def __init__(self, unknown_fnuk: _Optional[str] = ..., unknown_fnul: _Optional[int] = ..., unknown_fnum: _Optional[str] = ...) -> None: ...

class PaddockMountsEvent(_message.Message):
    __slots__ = ("unknown_fnux", "unknown_fnuz")
    class UnknownFnuxValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_FNUX_VALUE_UNSPECIFIED: _ClassVar[PaddockMountsEvent.UnknownFnuxValue]
    UNKNOWN_FNUX_VALUE_UNSPECIFIED: PaddockMountsEvent.UnknownFnuxValue
    class UnknownHux(_message.Message):
        __slots__ = ("unknown_fnut",)
        class UnknownFnutEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: UnknownHqu
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownHqu, _Mapping]] = ...) -> None: ...
        UNKNOWN_FNUT_FIELD_NUMBER: _ClassVar[int]
        unknown_fnut: _containers.MessageMap[str, UnknownHqu]
        def __init__(self, unknown_fnut: _Optional[_Mapping[str, UnknownHqu]] = ...) -> None: ...
    UNKNOWN_FNUX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNUZ_FIELD_NUMBER: _ClassVar[int]
    unknown_fnux: PaddockMountsEvent.UnknownFnuxValue
    unknown_fnuz: PaddockMountsEvent.UnknownHux
    def __init__(self, unknown_fnux: _Optional[_Union[PaddockMountsEvent.UnknownFnuxValue, str]] = ..., unknown_fnuz: _Optional[_Union[PaddockMountsEvent.UnknownHux, _Mapping]] = ...) -> None: ...

class PaddockListenStartRequest(_message.Message):
    __slots__ = ("unknown_fnib",)
    UNKNOWN_FNIB_FIELD_NUMBER: _ClassVar[int]
    unknown_fnib: bool
    def __init__(self, unknown_fnib: bool = ...) -> None: ...

class PaddockSlotsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PaddockListenStopRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PaddockListenStopEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
