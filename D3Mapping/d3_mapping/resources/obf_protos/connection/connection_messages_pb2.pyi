from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class bpry(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BPRY_ECYD: _ClassVar[bpry]
    BPRY_ECYE: _ClassVar[bpry]
    BPRY_ECYF: _ClassVar[bpry]
    BPRY_ECYG: _ClassVar[bpry]
    BPRY_ECYH: _ClassVar[bpry]
    BPRY_ECYI: _ClassVar[bpry]
    BPRY_ECYJ: _ClassVar[bpry]
BPRY_ECYD: bpry
BPRY_ECYE: bpry
BPRY_ECYF: bpry
BPRY_ECYG: bpry
BPRY_ECYH: bpry
BPRY_ECYI: bpry
BPRY_ECYJ: bpry

class bpsa(_message.Message):
    __slots__ = ("eqjc", "eqjd", "eqje")
    EQJC_FIELD_NUMBER: _ClassVar[int]
    EQJD_FIELD_NUMBER: _ClassVar[int]
    EQJE_FIELD_NUMBER: _ClassVar[int]
    eqjc: bpsc
    eqjd: bpse
    eqje: bpsg
    def __init__(self, eqjc: _Optional[_Union[bpsc, _Mapping]] = ..., eqjd: _Optional[_Union[bpse, _Mapping]] = ..., eqje: _Optional[_Union[bpsg, _Mapping]] = ...) -> None: ...

class bpsc(_message.Message):
    __slots__ = ("eqjj", "eqjk", "eqjl", "eqjm", "eqjn", "eqjo", "eqjp", "eqjq")
    EQJJ_FIELD_NUMBER: _ClassVar[int]
    EQJK_FIELD_NUMBER: _ClassVar[int]
    EQJL_FIELD_NUMBER: _ClassVar[int]
    EQJM_FIELD_NUMBER: _ClassVar[int]
    EQJN_FIELD_NUMBER: _ClassVar[int]
    EQJO_FIELD_NUMBER: _ClassVar[int]
    EQJP_FIELD_NUMBER: _ClassVar[int]
    EQJQ_FIELD_NUMBER: _ClassVar[int]
    eqjj: str
    eqjk: bpsh
    eqjl: bpsl
    eqjm: bpsz
    eqjn: bpto
    eqjo: bptt
    eqjp: bpty
    eqjq: bpug
    def __init__(self, eqjj: _Optional[str] = ..., eqjk: _Optional[_Union[bpsh, _Mapping]] = ..., eqjl: _Optional[_Union[bpsl, _Mapping]] = ..., eqjm: _Optional[_Union[bpsz, _Mapping]] = ..., eqjn: _Optional[_Union[bpto, _Mapping]] = ..., eqjo: _Optional[_Union[bptt, _Mapping]] = ..., eqjp: _Optional[_Union[bpty, _Mapping]] = ..., eqjq: _Optional[_Union[bpug, _Mapping]] = ...) -> None: ...

class bpse(_message.Message):
    __slots__ = ("eqjv", "eqjw", "eqjx", "eqjy", "eqjz", "eqka", "eqkb")
    EQJV_FIELD_NUMBER: _ClassVar[int]
    EQJW_FIELD_NUMBER: _ClassVar[int]
    EQJX_FIELD_NUMBER: _ClassVar[int]
    EQJY_FIELD_NUMBER: _ClassVar[int]
    EQJZ_FIELD_NUMBER: _ClassVar[int]
    EQKA_FIELD_NUMBER: _ClassVar[int]
    EQKB_FIELD_NUMBER: _ClassVar[int]
    eqjv: str
    eqjw: bpsi
    eqjx: bpsy
    eqjy: bpte
    eqjz: bptq
    eqka: bpuf
    eqkb: bpun
    def __init__(self, eqjv: _Optional[str] = ..., eqjw: _Optional[_Union[bpsi, _Mapping]] = ..., eqjx: _Optional[_Union[bpsy, _Mapping]] = ..., eqjy: _Optional[_Union[bpte, _Mapping]] = ..., eqjz: _Optional[_Union[bptq, _Mapping]] = ..., eqka: _Optional[_Union[bpuf, _Mapping]] = ..., eqkb: _Optional[_Union[bpun, _Mapping]] = ...) -> None: ...

class bpsg(_message.Message):
    __slots__ = ("eqkg",)
    EQKG_FIELD_NUMBER: _ClassVar[int]
    eqkg: bpsj
    def __init__(self, eqkg: _Optional[_Union[bpsj, _Mapping]] = ...) -> None: ...

class bpsh(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class bpsi(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class bpsj(_message.Message):
    __slots__ = ("eqkr",)
    EQKR_FIELD_NUMBER: _ClassVar[int]
    eqkr: bptk
    def __init__(self, eqkr: _Optional[_Union[bptk, _Mapping]] = ...) -> None: ...

class bpsl(_message.Message):
    __slots__ = ("eqkv", "eqky", "eqkw", "eqkx")
    EQKV_FIELD_NUMBER: _ClassVar[int]
    EQKY_FIELD_NUMBER: _ClassVar[int]
    EQKW_FIELD_NUMBER: _ClassVar[int]
    EQKX_FIELD_NUMBER: _ClassVar[int]
    eqkv: str
    eqky: str
    eqkw: bpso
    eqkx: bpsp
    def __init__(self, eqkv: _Optional[str] = ..., eqky: _Optional[str] = ..., eqkw: _Optional[_Union[bpso, _Mapping]] = ..., eqkx: _Optional[_Union[bpsp, _Mapping]] = ...) -> None: ...

class bpso(_message.Message):
    __slots__ = ("eqli", "eqlj")
    class bpsm(_message.Message):
        __slots__ = ("eqld", "eqle")
        EQLD_FIELD_NUMBER: _ClassVar[int]
        EQLE_FIELD_NUMBER: _ClassVar[int]
        eqld: int
        eqle: str
        def __init__(self, eqld: _Optional[int] = ..., eqle: _Optional[str] = ...) -> None: ...
    EQLI_FIELD_NUMBER: _ClassVar[int]
    EQLJ_FIELD_NUMBER: _ClassVar[int]
    eqli: str
    eqlj: bpso.bpsm
    def __init__(self, eqli: _Optional[str] = ..., eqlj: _Optional[_Union[bpso.bpsm, _Mapping]] = ...) -> None: ...

class bpsp(_message.Message):
    __slots__ = ("eqln",)
    EQLN_FIELD_NUMBER: _ClassVar[int]
    eqln: str
    def __init__(self, eqln: _Optional[str] = ...) -> None: ...

class bpsy(_message.Message):
    __slots__ = ("eqmu", "eqmv")
    class bpst(_message.Message):
        __slots__ = ("eqma", "eqmb", "eqmc", "eqmd", "eqme", "eqmf", "eqmg", "eqmi", "bmjr")
        class bpsr(_message.Message):
            __slots__ = ("eqlr", "eqls", "eqlt", "eqlu", "eqlv", "eqlw", "bmjq")
            EQLR_FIELD_NUMBER: _ClassVar[int]
            EQLS_FIELD_NUMBER: _ClassVar[int]
            EQLT_FIELD_NUMBER: _ClassVar[int]
            EQLU_FIELD_NUMBER: _ClassVar[int]
            EQLV_FIELD_NUMBER: _ClassVar[int]
            EQLW_FIELD_NUMBER: _ClassVar[int]
            BMJQ_FIELD_NUMBER: _ClassVar[int]
            eqlr: bool
            eqls: bool
            eqlt: bool
            eqlu: bool
            eqlv: bool
            eqlw: bool
            bmjq: bool
            def __init__(self, eqlr: bool = ..., eqls: bool = ..., eqlt: bool = ..., eqlu: bool = ..., eqlv: bool = ..., eqlw: bool = ..., bmjq: bool = ...) -> None: ...
        EQMA_FIELD_NUMBER: _ClassVar[int]
        EQMB_FIELD_NUMBER: _ClassVar[int]
        EQMC_FIELD_NUMBER: _ClassVar[int]
        EQMD_FIELD_NUMBER: _ClassVar[int]
        EQME_FIELD_NUMBER: _ClassVar[int]
        EQMF_FIELD_NUMBER: _ClassVar[int]
        EQMG_FIELD_NUMBER: _ClassVar[int]
        EQMI_FIELD_NUMBER: _ClassVar[int]
        BMJR_FIELD_NUMBER: _ClassVar[int]
        eqma: int
        eqmb: str
        eqmc: str
        eqmd: bpth
        eqme: str
        eqmf: bpsy.bpst.bpsr
        eqmg: int
        eqmi: bptr
        bmjr: edy
        def __init__(self, eqma: _Optional[int] = ..., eqmb: _Optional[str] = ..., eqmc: _Optional[str] = ..., eqmd: _Optional[_Union[bpth, _Mapping]] = ..., eqme: _Optional[str] = ..., eqmf: _Optional[_Union[bpsy.bpst.bpsr, _Mapping]] = ..., eqmg: _Optional[int] = ..., eqmi: _Optional[_Union[bptr, _Mapping]] = ..., bmjr: _Optional[_Union[edy, _Mapping]] = ...) -> None: ...
    class bpsw(_message.Message):
        __slots__ = ("eqmm", "eqmn", "eqmp")
        class bpsu(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            BPSU_EDDM: _ClassVar[bpsy.bpsw.bpsu]
            BPSU_EDDN: _ClassVar[bpsy.bpsw.bpsu]
            BPSU_EDDO: _ClassVar[bpsy.bpsw.bpsu]
            BPSU_EDDP: _ClassVar[bpsy.bpsw.bpsu]
            BPSU_EDDQ: _ClassVar[bpsy.bpsw.bpsu]
            BPSU_EDDR: _ClassVar[bpsy.bpsw.bpsu]
            BPSU_EDDS: _ClassVar[bpsy.bpsw.bpsu]
            BPSU_EDDT: _ClassVar[bpsy.bpsw.bpsu]
            BPSU_EDDU: _ClassVar[bpsy.bpsw.bpsu]
            BPSU_EDDV: _ClassVar[bpsy.bpsw.bpsu]
            BPSU_EDDW: _ClassVar[bpsy.bpsw.bpsu]
            BPSU_EDDX: _ClassVar[bpsy.bpsw.bpsu]
            BPSU_EDDY: _ClassVar[bpsy.bpsw.bpsu]
            BPSU_EDDZ: _ClassVar[bpsy.bpsw.bpsu]
        BPSU_EDDM: bpsy.bpsw.bpsu
        BPSU_EDDN: bpsy.bpsw.bpsu
        BPSU_EDDO: bpsy.bpsw.bpsu
        BPSU_EDDP: bpsy.bpsw.bpsu
        BPSU_EDDQ: bpsy.bpsw.bpsu
        BPSU_EDDR: bpsy.bpsw.bpsu
        BPSU_EDDS: bpsy.bpsw.bpsu
        BPSU_EDDT: bpsy.bpsw.bpsu
        BPSU_EDDU: bpsy.bpsw.bpsu
        BPSU_EDDV: bpsy.bpsw.bpsu
        BPSU_EDDW: bpsy.bpsw.bpsu
        BPSU_EDDX: bpsy.bpsw.bpsu
        BPSU_EDDY: bpsy.bpsw.bpsu
        BPSU_EDDZ: bpsy.bpsw.bpsu
        EQMM_FIELD_NUMBER: _ClassVar[int]
        EQMN_FIELD_NUMBER: _ClassVar[int]
        EQMP_FIELD_NUMBER: _ClassVar[int]
        eqmm: bpsy.bpsw.bpsu
        eqmn: str
        eqmp: str
        def __init__(self, eqmm: _Optional[_Union[bpsy.bpsw.bpsu, str]] = ..., eqmn: _Optional[str] = ..., eqmp: _Optional[str] = ...) -> None: ...
    EQMU_FIELD_NUMBER: _ClassVar[int]
    EQMV_FIELD_NUMBER: _ClassVar[int]
    eqmu: bpsy.bpst
    eqmv: bpsy.bpsw
    def __init__(self, eqmu: _Optional[_Union[bpsy.bpst, _Mapping]] = ..., eqmv: _Optional[_Union[bpsy.bpsw, _Mapping]] = ...) -> None: ...

class bpsz(_message.Message):
    __slots__ = ("eqna",)
    EQNA_FIELD_NUMBER: _ClassVar[int]
    eqna: int
    def __init__(self, eqna: _Optional[int] = ...) -> None: ...

class bpte(_message.Message):
    __slots__ = ("eqnk", "eqnl")
    class bptb(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BPTB_EDEX: _ClassVar[bpte.bptb]
        BPTB_EDEY: _ClassVar[bpte.bptb]
        BPTB_EDEZ: _ClassVar[bpte.bptb]
        BPTB_EDFA: _ClassVar[bpte.bptb]
    BPTB_EDEX: bpte.bptb
    BPTB_EDEY: bpte.bptb
    BPTB_EDEZ: bpte.bptb
    BPTB_EDFA: bpte.bptb
    class bptc(_message.Message):
        __slots__ = ("eqne", "eqnf", "eqng")
        EQNE_FIELD_NUMBER: _ClassVar[int]
        EQNF_FIELD_NUMBER: _ClassVar[int]
        EQNG_FIELD_NUMBER: _ClassVar[int]
        eqne: str
        eqnf: str
        eqng: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, eqne: _Optional[str] = ..., eqnf: _Optional[str] = ..., eqng: _Optional[_Iterable[int]] = ...) -> None: ...
    EQNK_FIELD_NUMBER: _ClassVar[int]
    EQNL_FIELD_NUMBER: _ClassVar[int]
    eqnk: bpte.bptc
    eqnl: bpte.bptb
    def __init__(self, eqnk: _Optional[_Union[bpte.bptc, _Mapping]] = ..., eqnl: _Optional[_Union[bpte.bptb, str]] = ...) -> None: ...

class bpth(_message.Message):
    __slots__ = ("eqnw", "eqnx", "eqny")
    class bptf(_message.Message):
        __slots__ = ("eqnr", "eqns")
        EQNR_FIELD_NUMBER: _ClassVar[int]
        EQNS_FIELD_NUMBER: _ClassVar[int]
        eqnr: bpry
        eqns: int
        def __init__(self, eqnr: _Optional[_Union[bpry, str]] = ..., eqns: _Optional[int] = ...) -> None: ...
    EQNW_FIELD_NUMBER: _ClassVar[int]
    EQNX_FIELD_NUMBER: _ClassVar[int]
    EQNY_FIELD_NUMBER: _ClassVar[int]
    eqnw: _containers.RepeatedCompositeFieldContainer[bptk]
    eqnx: _containers.RepeatedCompositeFieldContainer[bpth.bptf]
    eqny: bool
    def __init__(self, eqnw: _Optional[_Iterable[_Union[bptk, _Mapping]]] = ..., eqnx: _Optional[_Iterable[_Union[bpth.bptf, _Mapping]]] = ..., eqny: bool = ...) -> None: ...

class bptk(_message.Message):
    __slots__ = ("eqoc", "eqod", "eqoe")
    class bpti(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BPTI_EDGG: _ClassVar[bptk.bpti]
        BPTI_EDGH: _ClassVar[bptk.bpti]
        BPTI_EDGI: _ClassVar[bptk.bpti]
        BPTI_EDGJ: _ClassVar[bptk.bpti]
    BPTI_EDGG: bptk.bpti
    BPTI_EDGH: bptk.bpti
    BPTI_EDGI: bptk.bpti
    BPTI_EDGJ: bptk.bpti
    EQOC_FIELD_NUMBER: _ClassVar[int]
    EQOD_FIELD_NUMBER: _ClassVar[int]
    EQOE_FIELD_NUMBER: _ClassVar[int]
    eqoc: bptn
    eqod: bptk.bpti
    eqoe: _containers.RepeatedCompositeFieldContainer[bptx]
    def __init__(self, eqoc: _Optional[_Union[bptn, _Mapping]] = ..., eqod: _Optional[_Union[bptk.bpti, str]] = ..., eqoe: _Optional[_Iterable[_Union[bptx, _Mapping]]] = ...) -> None: ...

class bptn(_message.Message):
    __slots__ = ("eqoi", "eqoj", "eqok")
    class bptl(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BPTL_EDGT: _ClassVar[bptn.bptl]
        BPTL_EDGU: _ClassVar[bptn.bptl]
    BPTL_EDGT: bptn.bptl
    BPTL_EDGU: bptn.bptl
    EQOI_FIELD_NUMBER: _ClassVar[int]
    EQOJ_FIELD_NUMBER: _ClassVar[int]
    EQOK_FIELD_NUMBER: _ClassVar[int]
    eqoi: int
    eqoj: bptn.bptl
    eqok: bpry
    def __init__(self, eqoi: _Optional[int] = ..., eqoj: _Optional[_Union[bptn.bptl, str]] = ..., eqok: _Optional[_Union[bpry, str]] = ...) -> None: ...

class bpto(_message.Message):
    __slots__ = ("eqoo",)
    EQOO_FIELD_NUMBER: _ClassVar[int]
    eqoo: int
    def __init__(self, eqoo: _Optional[int] = ...) -> None: ...

class bptq(_message.Message):
    __slots__ = ("eqos", "eqot")
    EQOS_FIELD_NUMBER: _ClassVar[int]
    EQOT_FIELD_NUMBER: _ClassVar[int]
    eqos: bptr
    eqot: bpts
    def __init__(self, eqos: _Optional[_Union[bptr, _Mapping]] = ..., eqot: _Optional[_Union[bpts, _Mapping]] = ...) -> None: ...

class bptr(_message.Message):
    __slots__ = ("eqoy", "eqoz", "eqpa", "eqpb", "eqpc")
    EQOY_FIELD_NUMBER: _ClassVar[int]
    EQOZ_FIELD_NUMBER: _ClassVar[int]
    EQPA_FIELD_NUMBER: _ClassVar[int]
    EQPB_FIELD_NUMBER: _ClassVar[int]
    EQPC_FIELD_NUMBER: _ClassVar[int]
    eqoy: bool
    eqoz: int
    eqpa: str
    eqpb: str
    eqpc: bpth
    def __init__(self, eqoy: bool = ..., eqoz: _Optional[int] = ..., eqpa: _Optional[str] = ..., eqpb: _Optional[str] = ..., eqpc: _Optional[_Union[bpth, _Mapping]] = ...) -> None: ...

class bpts(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class bptt(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class bptx(_message.Message):
    __slots__ = ("eqpm", "eqpn", "eqpo", "eqpp", "eqpq")
    class bptv(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BPTV_EDII: _ClassVar[bptx.bptv]
        BPTV_EDIJ: _ClassVar[bptx.bptv]
        BPTV_EDIK: _ClassVar[bptx.bptv]
        BPTV_EDIL: _ClassVar[bptx.bptv]
        BPTV_EDIM: _ClassVar[bptx.bptv]
        BPTV_EDIN: _ClassVar[bptx.bptv]
        BPTV_EDIO: _ClassVar[bptx.bptv]
        BPTV_EDIP: _ClassVar[bptx.bptv]
        BPTV_EDIQ: _ClassVar[bptx.bptv]
        BPTV_EDIR: _ClassVar[bptx.bptv]
        BPTV_EDIS: _ClassVar[bptx.bptv]
        BPTV_EDIU: _ClassVar[bptx.bptv]
        BPTV_EDIV: _ClassVar[bptx.bptv]
        BPTV_EDIW: _ClassVar[bptx.bptv]
        BPTV_EDIX: _ClassVar[bptx.bptv]
        BPTV_EDIY: _ClassVar[bptx.bptv]
        BPTV_EDIZ: _ClassVar[bptx.bptv]
        BPTV_EDJA: _ClassVar[bptx.bptv]
        BPTV_EDJB: _ClassVar[bptx.bptv]
    BPTV_EDII: bptx.bptv
    BPTV_EDIJ: bptx.bptv
    BPTV_EDIK: bptx.bptv
    BPTV_EDIL: bptx.bptv
    BPTV_EDIM: bptx.bptv
    BPTV_EDIN: bptx.bptv
    BPTV_EDIO: bptx.bptv
    BPTV_EDIP: bptx.bptv
    BPTV_EDIQ: bptx.bptv
    BPTV_EDIR: bptx.bptv
    BPTV_EDIS: bptx.bptv
    BPTV_EDIU: bptx.bptv
    BPTV_EDIV: bptx.bptv
    BPTV_EDIW: bptx.bptv
    BPTV_EDIX: bptx.bptv
    BPTV_EDIY: bptx.bptv
    BPTV_EDIZ: bptx.bptv
    BPTV_EDJA: bptx.bptv
    BPTV_EDJB: bptx.bptv
    class bptu(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BPTU_EDIG: _ClassVar[bptx.bptu]
        BPTU_EDIH: _ClassVar[bptx.bptu]
    BPTU_EDIG: bptx.bptu
    BPTU_EDIH: bptx.bptu
    EQPM_FIELD_NUMBER: _ClassVar[int]
    EQPN_FIELD_NUMBER: _ClassVar[int]
    EQPO_FIELD_NUMBER: _ClassVar[int]
    EQPP_FIELD_NUMBER: _ClassVar[int]
    EQPQ_FIELD_NUMBER: _ClassVar[int]
    eqpm: str
    eqpn: bptx.bptv
    eqpo: bptx.bptu
    eqpp: int
    eqpq: str
    def __init__(self, eqpm: _Optional[str] = ..., eqpn: _Optional[_Union[bptx.bptv, str]] = ..., eqpo: _Optional[_Union[bptx.bptu, str]] = ..., eqpp: _Optional[int] = ..., eqpq: _Optional[str] = ...) -> None: ...

class bpty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class bpuf(_message.Message):
    __slots__ = ("eqqh", "eqqi")
    class bpua(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BPUA_EDJT: _ClassVar[bpuf.bpua]
        BPUA_EDJU: _ClassVar[bpuf.bpua]
    BPUA_EDJT: bpuf.bpua
    BPUA_EDJU: bpuf.bpua
    class bpud(_message.Message):
        __slots__ = ("eqqd",)
        class bpub(_message.Message):
            __slots__ = ("eqpx", "eqpy", "eqpz")
            EQPX_FIELD_NUMBER: _ClassVar[int]
            EQPY_FIELD_NUMBER: _ClassVar[int]
            EQPZ_FIELD_NUMBER: _ClassVar[int]
            eqpx: str
            eqpy: str
            eqpz: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, eqpx: _Optional[str] = ..., eqpy: _Optional[str] = ..., eqpz: _Optional[_Iterable[int]] = ...) -> None: ...
        EQQD_FIELD_NUMBER: _ClassVar[int]
        eqqd: _containers.RepeatedCompositeFieldContainer[bpuf.bpud.bpub]
        def __init__(self, eqqd: _Optional[_Iterable[_Union[bpuf.bpud.bpub, _Mapping]]] = ...) -> None: ...
    EQQH_FIELD_NUMBER: _ClassVar[int]
    EQQI_FIELD_NUMBER: _ClassVar[int]
    eqqh: bpuf.bpud
    eqqi: bpuf.bpua
    def __init__(self, eqqh: _Optional[_Union[bpuf.bpud, _Mapping]] = ..., eqqi: _Optional[_Union[bpuf.bpua, str]] = ...) -> None: ...

class bpug(_message.Message):
    __slots__ = ("eqqo", "eqqp")
    EQQO_FIELD_NUMBER: _ClassVar[int]
    EQQP_FIELD_NUMBER: _ClassVar[int]
    eqqo: str
    eqqp: str
    def __init__(self, eqqo: _Optional[str] = ..., eqqp: _Optional[str] = ...) -> None: ...

class bpun(_message.Message):
    __slots__ = ("eqrb", "eqrc")
    class bpui(_message.Message):
        __slots__ = ("eqqt",)
        EQQT_FIELD_NUMBER: _ClassVar[int]
        eqqt: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, eqqt: _Optional[_Iterable[int]] = ...) -> None: ...
    class bpul(_message.Message):
        __slots__ = ("eqqx",)
        class bpuj(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            BPUJ_EDLD: _ClassVar[bpun.bpul.bpuj]
            BPUJ_EDLE: _ClassVar[bpun.bpul.bpuj]
            BPUJ_EDLF: _ClassVar[bpun.bpul.bpuj]
            BPUJ_EDLG: _ClassVar[bpun.bpul.bpuj]
        BPUJ_EDLD: bpun.bpul.bpuj
        BPUJ_EDLE: bpun.bpul.bpuj
        BPUJ_EDLF: bpun.bpul.bpuj
        BPUJ_EDLG: bpun.bpul.bpuj
        EQQX_FIELD_NUMBER: _ClassVar[int]
        eqqx: bpun.bpul.bpuj
        def __init__(self, eqqx: _Optional[_Union[bpun.bpul.bpuj, str]] = ...) -> None: ...
    EQRB_FIELD_NUMBER: _ClassVar[int]
    EQRC_FIELD_NUMBER: _ClassVar[int]
    eqrb: bpun.bpui
    eqrc: bpun.bpul
    def __init__(self, eqrb: _Optional[_Union[bpun.bpui, _Mapping]] = ..., eqrc: _Optional[_Union[bpun.bpul, _Mapping]] = ...) -> None: ...

class edy(_message.Message):
    __slots__ = ("bmjz", "bmkt", "bmlj")
    BMJZ_FIELD_NUMBER: _ClassVar[int]
    BMKT_FIELD_NUMBER: _ClassVar[int]
    BMLJ_FIELD_NUMBER: _ClassVar[int]
    bmjz: str
    bmkt: str
    bmlj: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, bmjz: _Optional[str] = ..., bmkt: _Optional[str] = ..., bmlj: _Optional[_Iterable[int]] = ...) -> None: ...
