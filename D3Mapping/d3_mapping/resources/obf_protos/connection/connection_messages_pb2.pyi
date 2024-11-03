from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class koi(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KOI_EMCO: _ClassVar[koi]
    KOI_EMCP: _ClassVar[koi]
    KOI_EMCQ: _ClassVar[koi]
    KOI_EMCR: _ClassVar[koi]
    KOI_EMCS: _ClassVar[koi]
    KOI_EMCT: _ClassVar[koi]
    KOI_EMCU: _ClassVar[koi]
KOI_EMCO: koi
KOI_EMCP: koi
KOI_EMCQ: koi
KOI_EMCR: koi
KOI_EMCS: koi
KOI_EMCT: koi
KOI_EMCU: koi

class kok(_message.Message):
    __slots__ = ("fgxs", "fgxt", "fgxu")
    FGXS_FIELD_NUMBER: _ClassVar[int]
    FGXT_FIELD_NUMBER: _ClassVar[int]
    FGXU_FIELD_NUMBER: _ClassVar[int]
    fgxs: kom
    fgxt: koo
    fgxu: koq
    def __init__(self, fgxs: _Optional[_Union[kom, _Mapping]] = ..., fgxt: _Optional[_Union[koo, _Mapping]] = ..., fgxu: _Optional[_Union[koq, _Mapping]] = ...) -> None: ...

class kom(_message.Message):
    __slots__ = ("fgxz", "fgya", "fgyb", "fgyc", "fgyd", "fgye", "fgyf", "fgyg")
    FGXZ_FIELD_NUMBER: _ClassVar[int]
    FGYA_FIELD_NUMBER: _ClassVar[int]
    FGYB_FIELD_NUMBER: _ClassVar[int]
    FGYC_FIELD_NUMBER: _ClassVar[int]
    FGYD_FIELD_NUMBER: _ClassVar[int]
    FGYE_FIELD_NUMBER: _ClassVar[int]
    FGYF_FIELD_NUMBER: _ClassVar[int]
    FGYG_FIELD_NUMBER: _ClassVar[int]
    fgxz: str
    fgya: kor
    fgyb: kov
    fgyc: kpj
    fgyd: kpy
    fgye: kqd
    fgyf: kqi
    fgyg: kqq
    def __init__(self, fgxz: _Optional[str] = ..., fgya: _Optional[_Union[kor, _Mapping]] = ..., fgyb: _Optional[_Union[kov, _Mapping]] = ..., fgyc: _Optional[_Union[kpj, _Mapping]] = ..., fgyd: _Optional[_Union[kpy, _Mapping]] = ..., fgye: _Optional[_Union[kqd, _Mapping]] = ..., fgyf: _Optional[_Union[kqi, _Mapping]] = ..., fgyg: _Optional[_Union[kqq, _Mapping]] = ...) -> None: ...

class koo(_message.Message):
    __slots__ = ("fgyl", "fgym", "fgyn", "fgyo", "fgyp", "fgyq", "fgyr")
    FGYL_FIELD_NUMBER: _ClassVar[int]
    FGYM_FIELD_NUMBER: _ClassVar[int]
    FGYN_FIELD_NUMBER: _ClassVar[int]
    FGYO_FIELD_NUMBER: _ClassVar[int]
    FGYP_FIELD_NUMBER: _ClassVar[int]
    FGYQ_FIELD_NUMBER: _ClassVar[int]
    FGYR_FIELD_NUMBER: _ClassVar[int]
    fgyl: str
    fgym: kos
    fgyn: kpi
    fgyo: kpo
    fgyp: kqa
    fgyq: kqp
    fgyr: kqx
    def __init__(self, fgyl: _Optional[str] = ..., fgym: _Optional[_Union[kos, _Mapping]] = ..., fgyn: _Optional[_Union[kpi, _Mapping]] = ..., fgyo: _Optional[_Union[kpo, _Mapping]] = ..., fgyp: _Optional[_Union[kqa, _Mapping]] = ..., fgyq: _Optional[_Union[kqp, _Mapping]] = ..., fgyr: _Optional[_Union[kqx, _Mapping]] = ...) -> None: ...

class koq(_message.Message):
    __slots__ = ("fgyw",)
    FGYW_FIELD_NUMBER: _ClassVar[int]
    fgyw: kot
    def __init__(self, fgyw: _Optional[_Union[kot, _Mapping]] = ...) -> None: ...

class kor(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class kos(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class kot(_message.Message):
    __slots__ = ("fgzh",)
    FGZH_FIELD_NUMBER: _ClassVar[int]
    fgzh: kpu
    def __init__(self, fgzh: _Optional[_Union[kpu, _Mapping]] = ...) -> None: ...

class kov(_message.Message):
    __slots__ = ("fgzl", "fgzo", "fgzm", "fgzn")
    FGZL_FIELD_NUMBER: _ClassVar[int]
    FGZO_FIELD_NUMBER: _ClassVar[int]
    FGZM_FIELD_NUMBER: _ClassVar[int]
    FGZN_FIELD_NUMBER: _ClassVar[int]
    fgzl: str
    fgzo: str
    fgzm: koy
    fgzn: koz
    def __init__(self, fgzl: _Optional[str] = ..., fgzo: _Optional[str] = ..., fgzm: _Optional[_Union[koy, _Mapping]] = ..., fgzn: _Optional[_Union[koz, _Mapping]] = ...) -> None: ...

class koy(_message.Message):
    __slots__ = ("fgzy", "fgzz")
    class kow(_message.Message):
        __slots__ = ("fgzt", "fgzu")
        FGZT_FIELD_NUMBER: _ClassVar[int]
        FGZU_FIELD_NUMBER: _ClassVar[int]
        fgzt: int
        fgzu: str
        def __init__(self, fgzt: _Optional[int] = ..., fgzu: _Optional[str] = ...) -> None: ...
    FGZY_FIELD_NUMBER: _ClassVar[int]
    FGZZ_FIELD_NUMBER: _ClassVar[int]
    fgzy: str
    fgzz: koy.kow
    def __init__(self, fgzy: _Optional[str] = ..., fgzz: _Optional[_Union[koy.kow, _Mapping]] = ...) -> None: ...

class koz(_message.Message):
    __slots__ = ("fhad",)
    FHAD_FIELD_NUMBER: _ClassVar[int]
    fhad: str
    def __init__(self, fhad: _Optional[str] = ...) -> None: ...

class kpi(_message.Message):
    __slots__ = ("fhbn", "fhbo")
    class kpd(_message.Message):
        __slots__ = ("fhas", "fhat", "fhau", "fhav", "fhaw", "fhax", "fhay", "fhba", "fhbb")
        class kpb(_message.Message):
            __slots__ = ("fhah", "fhai", "fhaj", "fhak", "fhal", "fham", "fhan", "fhao")
            FHAH_FIELD_NUMBER: _ClassVar[int]
            FHAI_FIELD_NUMBER: _ClassVar[int]
            FHAJ_FIELD_NUMBER: _ClassVar[int]
            FHAK_FIELD_NUMBER: _ClassVar[int]
            FHAL_FIELD_NUMBER: _ClassVar[int]
            FHAM_FIELD_NUMBER: _ClassVar[int]
            FHAN_FIELD_NUMBER: _ClassVar[int]
            FHAO_FIELD_NUMBER: _ClassVar[int]
            fhah: bool
            fhai: bool
            fhaj: bool
            fhak: bool
            fhal: bool
            fham: bool
            fhan: bool
            fhao: bool
            def __init__(self, fhah: bool = ..., fhai: bool = ..., fhaj: bool = ..., fhak: bool = ..., fhal: bool = ..., fham: bool = ..., fhan: bool = ..., fhao: bool = ...) -> None: ...
        FHAS_FIELD_NUMBER: _ClassVar[int]
        FHAT_FIELD_NUMBER: _ClassVar[int]
        FHAU_FIELD_NUMBER: _ClassVar[int]
        FHAV_FIELD_NUMBER: _ClassVar[int]
        FHAW_FIELD_NUMBER: _ClassVar[int]
        FHAX_FIELD_NUMBER: _ClassVar[int]
        FHAY_FIELD_NUMBER: _ClassVar[int]
        FHBA_FIELD_NUMBER: _ClassVar[int]
        FHBB_FIELD_NUMBER: _ClassVar[int]
        fhas: int
        fhat: str
        fhau: str
        fhav: kpr
        fhaw: str
        fhax: kpi.kpd.kpb
        fhay: int
        fhba: kqb
        fhbb: kqy
        def __init__(self, fhas: _Optional[int] = ..., fhat: _Optional[str] = ..., fhau: _Optional[str] = ..., fhav: _Optional[_Union[kpr, _Mapping]] = ..., fhaw: _Optional[str] = ..., fhax: _Optional[_Union[kpi.kpd.kpb, _Mapping]] = ..., fhay: _Optional[int] = ..., fhba: _Optional[_Union[kqb, _Mapping]] = ..., fhbb: _Optional[_Union[kqy, _Mapping]] = ...) -> None: ...
    class kpg(_message.Message):
        __slots__ = ("fhbf", "fhbg", "fhbi")
        class kpe(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            KPE_EMID: _ClassVar[kpi.kpg.kpe]
            KPE_EMIE: _ClassVar[kpi.kpg.kpe]
            KPE_EMIF: _ClassVar[kpi.kpg.kpe]
            KPE_EMIG: _ClassVar[kpi.kpg.kpe]
            KPE_EMIH: _ClassVar[kpi.kpg.kpe]
            KPE_EMII: _ClassVar[kpi.kpg.kpe]
            KPE_EMIJ: _ClassVar[kpi.kpg.kpe]
            KPE_EMIK: _ClassVar[kpi.kpg.kpe]
            KPE_EMIL: _ClassVar[kpi.kpg.kpe]
            KPE_EMIM: _ClassVar[kpi.kpg.kpe]
            KPE_EMIN: _ClassVar[kpi.kpg.kpe]
            KPE_EMIO: _ClassVar[kpi.kpg.kpe]
            KPE_EMIP: _ClassVar[kpi.kpg.kpe]
            KPE_EMIQ: _ClassVar[kpi.kpg.kpe]
        KPE_EMID: kpi.kpg.kpe
        KPE_EMIE: kpi.kpg.kpe
        KPE_EMIF: kpi.kpg.kpe
        KPE_EMIG: kpi.kpg.kpe
        KPE_EMIH: kpi.kpg.kpe
        KPE_EMII: kpi.kpg.kpe
        KPE_EMIJ: kpi.kpg.kpe
        KPE_EMIK: kpi.kpg.kpe
        KPE_EMIL: kpi.kpg.kpe
        KPE_EMIM: kpi.kpg.kpe
        KPE_EMIN: kpi.kpg.kpe
        KPE_EMIO: kpi.kpg.kpe
        KPE_EMIP: kpi.kpg.kpe
        KPE_EMIQ: kpi.kpg.kpe
        FHBF_FIELD_NUMBER: _ClassVar[int]
        FHBG_FIELD_NUMBER: _ClassVar[int]
        FHBI_FIELD_NUMBER: _ClassVar[int]
        fhbf: kpi.kpg.kpe
        fhbg: str
        fhbi: str
        def __init__(self, fhbf: _Optional[_Union[kpi.kpg.kpe, str]] = ..., fhbg: _Optional[str] = ..., fhbi: _Optional[str] = ...) -> None: ...
    FHBN_FIELD_NUMBER: _ClassVar[int]
    FHBO_FIELD_NUMBER: _ClassVar[int]
    fhbn: kpi.kpd
    fhbo: kpi.kpg
    def __init__(self, fhbn: _Optional[_Union[kpi.kpd, _Mapping]] = ..., fhbo: _Optional[_Union[kpi.kpg, _Mapping]] = ...) -> None: ...

class kpj(_message.Message):
    __slots__ = ("fhbt",)
    FHBT_FIELD_NUMBER: _ClassVar[int]
    fhbt: int
    def __init__(self, fhbt: _Optional[int] = ...) -> None: ...

class kpo(_message.Message):
    __slots__ = ("fhcd", "fhce")
    class kpl(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KPL_EMJO: _ClassVar[kpo.kpl]
        KPL_EMJP: _ClassVar[kpo.kpl]
        KPL_EMJQ: _ClassVar[kpo.kpl]
        KPL_EMJR: _ClassVar[kpo.kpl]
    KPL_EMJO: kpo.kpl
    KPL_EMJP: kpo.kpl
    KPL_EMJQ: kpo.kpl
    KPL_EMJR: kpo.kpl
    class kpm(_message.Message):
        __slots__ = ("fhbx", "fhby", "fhbz")
        FHBX_FIELD_NUMBER: _ClassVar[int]
        FHBY_FIELD_NUMBER: _ClassVar[int]
        FHBZ_FIELD_NUMBER: _ClassVar[int]
        fhbx: str
        fhby: str
        fhbz: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, fhbx: _Optional[str] = ..., fhby: _Optional[str] = ..., fhbz: _Optional[_Iterable[int]] = ...) -> None: ...
    FHCD_FIELD_NUMBER: _ClassVar[int]
    FHCE_FIELD_NUMBER: _ClassVar[int]
    fhcd: kpo.kpm
    fhce: kpo.kpl
    def __init__(self, fhcd: _Optional[_Union[kpo.kpm, _Mapping]] = ..., fhce: _Optional[_Union[kpo.kpl, str]] = ...) -> None: ...

class kpr(_message.Message):
    __slots__ = ("fhcp", "fhcq", "fhcr")
    class kpp(_message.Message):
        __slots__ = ("fhck", "fhcl")
        FHCK_FIELD_NUMBER: _ClassVar[int]
        FHCL_FIELD_NUMBER: _ClassVar[int]
        fhck: koi
        fhcl: int
        def __init__(self, fhck: _Optional[_Union[koi, str]] = ..., fhcl: _Optional[int] = ...) -> None: ...
    FHCP_FIELD_NUMBER: _ClassVar[int]
    FHCQ_FIELD_NUMBER: _ClassVar[int]
    FHCR_FIELD_NUMBER: _ClassVar[int]
    fhcp: _containers.RepeatedCompositeFieldContainer[kpu]
    fhcq: _containers.RepeatedCompositeFieldContainer[kpr.kpp]
    fhcr: bool
    def __init__(self, fhcp: _Optional[_Iterable[_Union[kpu, _Mapping]]] = ..., fhcq: _Optional[_Iterable[_Union[kpr.kpp, _Mapping]]] = ..., fhcr: bool = ...) -> None: ...

class kpu(_message.Message):
    __slots__ = ("fhcv", "fhcw", "fhcx")
    class kps(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KPS_EMKX: _ClassVar[kpu.kps]
        KPS_EMKY: _ClassVar[kpu.kps]
        KPS_EMKZ: _ClassVar[kpu.kps]
        KPS_EMLA: _ClassVar[kpu.kps]
    KPS_EMKX: kpu.kps
    KPS_EMKY: kpu.kps
    KPS_EMKZ: kpu.kps
    KPS_EMLA: kpu.kps
    FHCV_FIELD_NUMBER: _ClassVar[int]
    FHCW_FIELD_NUMBER: _ClassVar[int]
    FHCX_FIELD_NUMBER: _ClassVar[int]
    fhcv: kpx
    fhcw: kpu.kps
    fhcx: _containers.RepeatedCompositeFieldContainer[kqh]
    def __init__(self, fhcv: _Optional[_Union[kpx, _Mapping]] = ..., fhcw: _Optional[_Union[kpu.kps, str]] = ..., fhcx: _Optional[_Iterable[_Union[kqh, _Mapping]]] = ...) -> None: ...

class kpx(_message.Message):
    __slots__ = ("fhdb", "fhdc", "fhdd")
    class kpv(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KPV_EMLK: _ClassVar[kpx.kpv]
        KPV_EMLL: _ClassVar[kpx.kpv]
    KPV_EMLK: kpx.kpv
    KPV_EMLL: kpx.kpv
    FHDB_FIELD_NUMBER: _ClassVar[int]
    FHDC_FIELD_NUMBER: _ClassVar[int]
    FHDD_FIELD_NUMBER: _ClassVar[int]
    fhdb: int
    fhdc: kpx.kpv
    fhdd: koi
    def __init__(self, fhdb: _Optional[int] = ..., fhdc: _Optional[_Union[kpx.kpv, str]] = ..., fhdd: _Optional[_Union[koi, str]] = ...) -> None: ...

class kpy(_message.Message):
    __slots__ = ("fhdh",)
    FHDH_FIELD_NUMBER: _ClassVar[int]
    fhdh: int
    def __init__(self, fhdh: _Optional[int] = ...) -> None: ...

class kqa(_message.Message):
    __slots__ = ("fhdl", "fhdm")
    FHDL_FIELD_NUMBER: _ClassVar[int]
    FHDM_FIELD_NUMBER: _ClassVar[int]
    fhdl: kqb
    fhdm: kqc
    def __init__(self, fhdl: _Optional[_Union[kqb, _Mapping]] = ..., fhdm: _Optional[_Union[kqc, _Mapping]] = ...) -> None: ...

class kqb(_message.Message):
    __slots__ = ("fhdr", "fhds", "fhdt", "fhdu", "fhdv")
    FHDR_FIELD_NUMBER: _ClassVar[int]
    FHDS_FIELD_NUMBER: _ClassVar[int]
    FHDT_FIELD_NUMBER: _ClassVar[int]
    FHDU_FIELD_NUMBER: _ClassVar[int]
    FHDV_FIELD_NUMBER: _ClassVar[int]
    fhdr: bool
    fhds: int
    fhdt: str
    fhdu: str
    fhdv: kpr
    def __init__(self, fhdr: bool = ..., fhds: _Optional[int] = ..., fhdt: _Optional[str] = ..., fhdu: _Optional[str] = ..., fhdv: _Optional[_Union[kpr, _Mapping]] = ...) -> None: ...

class kqc(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class kqd(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class kqh(_message.Message):
    __slots__ = ("fhef", "fheg", "fheh", "fhei", "fhej")
    class kqf(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KQF_EMMZ: _ClassVar[kqh.kqf]
        KQF_EMNA: _ClassVar[kqh.kqf]
        KQF_EMNB: _ClassVar[kqh.kqf]
        KQF_EMNC: _ClassVar[kqh.kqf]
        KQF_EMND: _ClassVar[kqh.kqf]
        KQF_EMNE: _ClassVar[kqh.kqf]
        KQF_EMNF: _ClassVar[kqh.kqf]
        KQF_EMNG: _ClassVar[kqh.kqf]
        KQF_EMNH: _ClassVar[kqh.kqf]
        KQF_EMNI: _ClassVar[kqh.kqf]
        KQF_EMNJ: _ClassVar[kqh.kqf]
        KQF_EMNK: _ClassVar[kqh.kqf]
        KQF_EMNL: _ClassVar[kqh.kqf]
        KQF_EMNM: _ClassVar[kqh.kqf]
        KQF_EMNN: _ClassVar[kqh.kqf]
        KQF_EMNO: _ClassVar[kqh.kqf]
        KQF_EMNP: _ClassVar[kqh.kqf]
        KQF_EMNQ: _ClassVar[kqh.kqf]
        KQF_EMNR: _ClassVar[kqh.kqf]
    KQF_EMMZ: kqh.kqf
    KQF_EMNA: kqh.kqf
    KQF_EMNB: kqh.kqf
    KQF_EMNC: kqh.kqf
    KQF_EMND: kqh.kqf
    KQF_EMNE: kqh.kqf
    KQF_EMNF: kqh.kqf
    KQF_EMNG: kqh.kqf
    KQF_EMNH: kqh.kqf
    KQF_EMNI: kqh.kqf
    KQF_EMNJ: kqh.kqf
    KQF_EMNK: kqh.kqf
    KQF_EMNL: kqh.kqf
    KQF_EMNM: kqh.kqf
    KQF_EMNN: kqh.kqf
    KQF_EMNO: kqh.kqf
    KQF_EMNP: kqh.kqf
    KQF_EMNQ: kqh.kqf
    KQF_EMNR: kqh.kqf
    class kqe(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KQE_EMMX: _ClassVar[kqh.kqe]
        KQE_EMMY: _ClassVar[kqh.kqe]
    KQE_EMMX: kqh.kqe
    KQE_EMMY: kqh.kqe
    FHEF_FIELD_NUMBER: _ClassVar[int]
    FHEG_FIELD_NUMBER: _ClassVar[int]
    FHEH_FIELD_NUMBER: _ClassVar[int]
    FHEI_FIELD_NUMBER: _ClassVar[int]
    FHEJ_FIELD_NUMBER: _ClassVar[int]
    fhef: str
    fheg: kqh.kqf
    fheh: kqh.kqe
    fhei: int
    fhej: str
    def __init__(self, fhef: _Optional[str] = ..., fheg: _Optional[_Union[kqh.kqf, str]] = ..., fheh: _Optional[_Union[kqh.kqe, str]] = ..., fhei: _Optional[int] = ..., fhej: _Optional[str] = ...) -> None: ...

class kqi(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class kqp(_message.Message):
    __slots__ = ("fhfa", "fhfb")
    class kqk(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KQK_EMOJ: _ClassVar[kqp.kqk]
        KQK_EMOK: _ClassVar[kqp.kqk]
    KQK_EMOJ: kqp.kqk
    KQK_EMOK: kqp.kqk
    class kqn(_message.Message):
        __slots__ = ("fhew",)
        class kql(_message.Message):
            __slots__ = ("fheq", "fher", "fhes")
            FHEQ_FIELD_NUMBER: _ClassVar[int]
            FHER_FIELD_NUMBER: _ClassVar[int]
            FHES_FIELD_NUMBER: _ClassVar[int]
            fheq: str
            fher: str
            fhes: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, fheq: _Optional[str] = ..., fher: _Optional[str] = ..., fhes: _Optional[_Iterable[int]] = ...) -> None: ...
        FHEW_FIELD_NUMBER: _ClassVar[int]
        fhew: _containers.RepeatedCompositeFieldContainer[kqp.kqn.kql]
        def __init__(self, fhew: _Optional[_Iterable[_Union[kqp.kqn.kql, _Mapping]]] = ...) -> None: ...
    FHFA_FIELD_NUMBER: _ClassVar[int]
    FHFB_FIELD_NUMBER: _ClassVar[int]
    fhfa: kqp.kqn
    fhfb: kqp.kqk
    def __init__(self, fhfa: _Optional[_Union[kqp.kqn, _Mapping]] = ..., fhfb: _Optional[_Union[kqp.kqk, str]] = ...) -> None: ...

class kqq(_message.Message):
    __slots__ = ("fhfh", "fhfi")
    FHFH_FIELD_NUMBER: _ClassVar[int]
    FHFI_FIELD_NUMBER: _ClassVar[int]
    fhfh: str
    fhfi: str
    def __init__(self, fhfh: _Optional[str] = ..., fhfi: _Optional[str] = ...) -> None: ...

class kqx(_message.Message):
    __slots__ = ("fhfu", "fhfv")
    class kqs(_message.Message):
        __slots__ = ("fhfm",)
        FHFM_FIELD_NUMBER: _ClassVar[int]
        fhfm: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, fhfm: _Optional[_Iterable[int]] = ...) -> None: ...
    class kqv(_message.Message):
        __slots__ = ("fhfq",)
        class kqt(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            KQT_EMPT: _ClassVar[kqx.kqv.kqt]
            KQT_EMPU: _ClassVar[kqx.kqv.kqt]
            KQT_EMPV: _ClassVar[kqx.kqv.kqt]
            KQT_EMPW: _ClassVar[kqx.kqv.kqt]
        KQT_EMPT: kqx.kqv.kqt
        KQT_EMPU: kqx.kqv.kqt
        KQT_EMPV: kqx.kqv.kqt
        KQT_EMPW: kqx.kqv.kqt
        FHFQ_FIELD_NUMBER: _ClassVar[int]
        fhfq: kqx.kqv.kqt
        def __init__(self, fhfq: _Optional[_Union[kqx.kqv.kqt, str]] = ...) -> None: ...
    FHFU_FIELD_NUMBER: _ClassVar[int]
    FHFV_FIELD_NUMBER: _ClassVar[int]
    fhfu: kqx.kqs
    fhfv: kqx.kqv
    def __init__(self, fhfu: _Optional[_Union[kqx.kqs, _Mapping]] = ..., fhfv: _Optional[_Union[kqx.kqv, _Mapping]] = ...) -> None: ...

class kqy(_message.Message):
    __slots__ = ("fhga", "fhgb", "fhgc")
    FHGA_FIELD_NUMBER: _ClassVar[int]
    FHGB_FIELD_NUMBER: _ClassVar[int]
    FHGC_FIELD_NUMBER: _ClassVar[int]
    fhga: str
    fhgb: str
    fhgc: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, fhga: _Optional[str] = ..., fhgb: _Optional[str] = ..., fhgc: _Optional[_Iterable[int]] = ...) -> None: ...
