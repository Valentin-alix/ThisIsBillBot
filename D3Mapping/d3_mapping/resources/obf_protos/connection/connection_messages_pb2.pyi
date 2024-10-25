from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class kgr(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KGR_DVXB: _ClassVar[kgr]
    KGR_DVXC: _ClassVar[kgr]
    KGR_DVXD: _ClassVar[kgr]
    KGR_DVXE: _ClassVar[kgr]
    KGR_DVXF: _ClassVar[kgr]
    KGR_DVXG: _ClassVar[kgr]
    KGR_DVXH: _ClassVar[kgr]
KGR_DVXB: kgr
KGR_DVXC: kgr
KGR_DVXD: kgr
KGR_DVXE: kgr
KGR_DVXF: kgr
KGR_DVXG: kgr
KGR_DVXH: kgr

class kgt(_message.Message):
    __slots__ = ("emyu", "emyv", "emyw")
    EMYU_FIELD_NUMBER: _ClassVar[int]
    EMYV_FIELD_NUMBER: _ClassVar[int]
    EMYW_FIELD_NUMBER: _ClassVar[int]
    emyu: kgv
    emyv: kgx
    emyw: kgz
    def __init__(self, emyu: _Optional[_Union[kgv, _Mapping]] = ..., emyv: _Optional[_Union[kgx, _Mapping]] = ..., emyw: _Optional[_Union[kgz, _Mapping]] = ...) -> None: ...

class kgv(_message.Message):
    __slots__ = ("emzb", "emzc", "emzd", "emze", "emzf", "emzg", "emzh", "emzi")
    EMZB_FIELD_NUMBER: _ClassVar[int]
    EMZC_FIELD_NUMBER: _ClassVar[int]
    EMZD_FIELD_NUMBER: _ClassVar[int]
    EMZE_FIELD_NUMBER: _ClassVar[int]
    EMZF_FIELD_NUMBER: _ClassVar[int]
    EMZG_FIELD_NUMBER: _ClassVar[int]
    EMZH_FIELD_NUMBER: _ClassVar[int]
    EMZI_FIELD_NUMBER: _ClassVar[int]
    emzb: str
    emzc: kha
    emzd: khe
    emze: khs
    emzf: kih
    emzg: kim
    emzh: kir
    emzi: kiz
    def __init__(self, emzb: _Optional[str] = ..., emzc: _Optional[_Union[kha, _Mapping]] = ..., emzd: _Optional[_Union[khe, _Mapping]] = ..., emze: _Optional[_Union[khs, _Mapping]] = ..., emzf: _Optional[_Union[kih, _Mapping]] = ..., emzg: _Optional[_Union[kim, _Mapping]] = ..., emzh: _Optional[_Union[kir, _Mapping]] = ..., emzi: _Optional[_Union[kiz, _Mapping]] = ...) -> None: ...

class kgx(_message.Message):
    __slots__ = ("emzn", "emzo", "emzp", "emzq", "emzr", "emzs", "emzt")
    EMZN_FIELD_NUMBER: _ClassVar[int]
    EMZO_FIELD_NUMBER: _ClassVar[int]
    EMZP_FIELD_NUMBER: _ClassVar[int]
    EMZQ_FIELD_NUMBER: _ClassVar[int]
    EMZR_FIELD_NUMBER: _ClassVar[int]
    EMZS_FIELD_NUMBER: _ClassVar[int]
    EMZT_FIELD_NUMBER: _ClassVar[int]
    emzn: str
    emzo: khb
    emzp: khr
    emzq: khx
    emzr: kij
    emzs: kiy
    emzt: kjg
    def __init__(self, emzn: _Optional[str] = ..., emzo: _Optional[_Union[khb, _Mapping]] = ..., emzp: _Optional[_Union[khr, _Mapping]] = ..., emzq: _Optional[_Union[khx, _Mapping]] = ..., emzr: _Optional[_Union[kij, _Mapping]] = ..., emzs: _Optional[_Union[kiy, _Mapping]] = ..., emzt: _Optional[_Union[kjg, _Mapping]] = ...) -> None: ...

class kgz(_message.Message):
    __slots__ = ("emzy",)
    EMZY_FIELD_NUMBER: _ClassVar[int]
    emzy: khc
    def __init__(self, emzy: _Optional[_Union[khc, _Mapping]] = ...) -> None: ...

class kha(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class khb(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class khc(_message.Message):
    __slots__ = ("enaj",)
    ENAJ_FIELD_NUMBER: _ClassVar[int]
    enaj: kid
    def __init__(self, enaj: _Optional[_Union[kid, _Mapping]] = ...) -> None: ...

class khe(_message.Message):
    __slots__ = ("enan", "enaq", "enao", "enap")
    ENAN_FIELD_NUMBER: _ClassVar[int]
    ENAQ_FIELD_NUMBER: _ClassVar[int]
    ENAO_FIELD_NUMBER: _ClassVar[int]
    ENAP_FIELD_NUMBER: _ClassVar[int]
    enan: str
    enaq: str
    enao: khh
    enap: khi
    def __init__(self, enan: _Optional[str] = ..., enaq: _Optional[str] = ..., enao: _Optional[_Union[khh, _Mapping]] = ..., enap: _Optional[_Union[khi, _Mapping]] = ...) -> None: ...

class khh(_message.Message):
    __slots__ = ("enba", "enbb")
    class khf(_message.Message):
        __slots__ = ("enav", "enaw")
        ENAV_FIELD_NUMBER: _ClassVar[int]
        ENAW_FIELD_NUMBER: _ClassVar[int]
        enav: int
        enaw: str
        def __init__(self, enav: _Optional[int] = ..., enaw: _Optional[str] = ...) -> None: ...
    ENBA_FIELD_NUMBER: _ClassVar[int]
    ENBB_FIELD_NUMBER: _ClassVar[int]
    enba: str
    enbb: khh.khf
    def __init__(self, enba: _Optional[str] = ..., enbb: _Optional[_Union[khh.khf, _Mapping]] = ...) -> None: ...

class khi(_message.Message):
    __slots__ = ("enbf",)
    ENBF_FIELD_NUMBER: _ClassVar[int]
    enbf: str
    def __init__(self, enbf: _Optional[str] = ...) -> None: ...

class khr(_message.Message):
    __slots__ = ("encm", "encn")
    class khm(_message.Message):
        __slots__ = ("enbs", "enbt", "enbu", "enbv", "enbw", "enbx", "enby", "enca")
        class khk(_message.Message):
            __slots__ = ("enbj", "enbk", "enbl", "enbm", "enbn", "enbo")
            ENBJ_FIELD_NUMBER: _ClassVar[int]
            ENBK_FIELD_NUMBER: _ClassVar[int]
            ENBL_FIELD_NUMBER: _ClassVar[int]
            ENBM_FIELD_NUMBER: _ClassVar[int]
            ENBN_FIELD_NUMBER: _ClassVar[int]
            ENBO_FIELD_NUMBER: _ClassVar[int]
            enbj: bool
            enbk: bool
            enbl: bool
            enbm: bool
            enbn: bool
            enbo: bool
            def __init__(self, enbj: bool = ..., enbk: bool = ..., enbl: bool = ..., enbm: bool = ..., enbn: bool = ..., enbo: bool = ...) -> None: ...
        ENBS_FIELD_NUMBER: _ClassVar[int]
        ENBT_FIELD_NUMBER: _ClassVar[int]
        ENBU_FIELD_NUMBER: _ClassVar[int]
        ENBV_FIELD_NUMBER: _ClassVar[int]
        ENBW_FIELD_NUMBER: _ClassVar[int]
        ENBX_FIELD_NUMBER: _ClassVar[int]
        ENBY_FIELD_NUMBER: _ClassVar[int]
        ENCA_FIELD_NUMBER: _ClassVar[int]
        enbs: int
        enbt: str
        enbu: str
        enbv: kia
        enbw: str
        enbx: khr.khm.khk
        enby: int
        enca: kik
        def __init__(self, enbs: _Optional[int] = ..., enbt: _Optional[str] = ..., enbu: _Optional[str] = ..., enbv: _Optional[_Union[kia, _Mapping]] = ..., enbw: _Optional[str] = ..., enbx: _Optional[_Union[khr.khm.khk, _Mapping]] = ..., enby: _Optional[int] = ..., enca: _Optional[_Union[kik, _Mapping]] = ...) -> None: ...
    class khp(_message.Message):
        __slots__ = ("ence", "encf", "ench")
        class khn(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            KHN_DWCK: _ClassVar[khr.khp.khn]
            KHN_DWCL: _ClassVar[khr.khp.khn]
            KHN_DWCM: _ClassVar[khr.khp.khn]
            KHN_DWCN: _ClassVar[khr.khp.khn]
            KHN_DWCO: _ClassVar[khr.khp.khn]
            KHN_DWCP: _ClassVar[khr.khp.khn]
            KHN_DWCQ: _ClassVar[khr.khp.khn]
            KHN_DWCR: _ClassVar[khr.khp.khn]
            KHN_DWCS: _ClassVar[khr.khp.khn]
            KHN_DWCT: _ClassVar[khr.khp.khn]
            KHN_DWCU: _ClassVar[khr.khp.khn]
            KHN_DWCV: _ClassVar[khr.khp.khn]
            KHN_DWCW: _ClassVar[khr.khp.khn]
            KHN_DWCX: _ClassVar[khr.khp.khn]
        KHN_DWCK: khr.khp.khn
        KHN_DWCL: khr.khp.khn
        KHN_DWCM: khr.khp.khn
        KHN_DWCN: khr.khp.khn
        KHN_DWCO: khr.khp.khn
        KHN_DWCP: khr.khp.khn
        KHN_DWCQ: khr.khp.khn
        KHN_DWCR: khr.khp.khn
        KHN_DWCS: khr.khp.khn
        KHN_DWCT: khr.khp.khn
        KHN_DWCU: khr.khp.khn
        KHN_DWCV: khr.khp.khn
        KHN_DWCW: khr.khp.khn
        KHN_DWCX: khr.khp.khn
        ENCE_FIELD_NUMBER: _ClassVar[int]
        ENCF_FIELD_NUMBER: _ClassVar[int]
        ENCH_FIELD_NUMBER: _ClassVar[int]
        ence: khr.khp.khn
        encf: str
        ench: str
        def __init__(self, ence: _Optional[_Union[khr.khp.khn, str]] = ..., encf: _Optional[str] = ..., ench: _Optional[str] = ...) -> None: ...
    ENCM_FIELD_NUMBER: _ClassVar[int]
    ENCN_FIELD_NUMBER: _ClassVar[int]
    encm: khr.khm
    encn: khr.khp
    def __init__(self, encm: _Optional[_Union[khr.khm, _Mapping]] = ..., encn: _Optional[_Union[khr.khp, _Mapping]] = ...) -> None: ...

class khs(_message.Message):
    __slots__ = ("encs",)
    ENCS_FIELD_NUMBER: _ClassVar[int]
    encs: int
    def __init__(self, encs: _Optional[int] = ...) -> None: ...

class khx(_message.Message):
    __slots__ = ("endc", "endd")
    class khu(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KHU_DWDV: _ClassVar[khx.khu]
        KHU_DWDW: _ClassVar[khx.khu]
        KHU_DWDX: _ClassVar[khx.khu]
        KHU_DWDY: _ClassVar[khx.khu]
    KHU_DWDV: khx.khu
    KHU_DWDW: khx.khu
    KHU_DWDX: khx.khu
    KHU_DWDY: khx.khu
    class khv(_message.Message):
        __slots__ = ("encw", "encx", "ency")
        ENCW_FIELD_NUMBER: _ClassVar[int]
        ENCX_FIELD_NUMBER: _ClassVar[int]
        ENCY_FIELD_NUMBER: _ClassVar[int]
        encw: str
        encx: str
        ency: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, encw: _Optional[str] = ..., encx: _Optional[str] = ..., ency: _Optional[_Iterable[int]] = ...) -> None: ...
    ENDC_FIELD_NUMBER: _ClassVar[int]
    ENDD_FIELD_NUMBER: _ClassVar[int]
    endc: khx.khv
    endd: khx.khu
    def __init__(self, endc: _Optional[_Union[khx.khv, _Mapping]] = ..., endd: _Optional[_Union[khx.khu, str]] = ...) -> None: ...

class kia(_message.Message):
    __slots__ = ("endo", "endp", "endq")
    class khy(_message.Message):
        __slots__ = ("endj", "endk")
        ENDJ_FIELD_NUMBER: _ClassVar[int]
        ENDK_FIELD_NUMBER: _ClassVar[int]
        endj: kgr
        endk: int
        def __init__(self, endj: _Optional[_Union[kgr, str]] = ..., endk: _Optional[int] = ...) -> None: ...
    ENDO_FIELD_NUMBER: _ClassVar[int]
    ENDP_FIELD_NUMBER: _ClassVar[int]
    ENDQ_FIELD_NUMBER: _ClassVar[int]
    endo: _containers.RepeatedCompositeFieldContainer[kid]
    endp: _containers.RepeatedCompositeFieldContainer[kia.khy]
    endq: bool
    def __init__(self, endo: _Optional[_Iterable[_Union[kid, _Mapping]]] = ..., endp: _Optional[_Iterable[_Union[kia.khy, _Mapping]]] = ..., endq: bool = ...) -> None: ...

class kid(_message.Message):
    __slots__ = ("endu", "endv", "endw")
    class kib(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KIB_DWFE: _ClassVar[kid.kib]
        KIB_DWFF: _ClassVar[kid.kib]
        KIB_DWFG: _ClassVar[kid.kib]
        KIB_DWFH: _ClassVar[kid.kib]
    KIB_DWFE: kid.kib
    KIB_DWFF: kid.kib
    KIB_DWFG: kid.kib
    KIB_DWFH: kid.kib
    ENDU_FIELD_NUMBER: _ClassVar[int]
    ENDV_FIELD_NUMBER: _ClassVar[int]
    ENDW_FIELD_NUMBER: _ClassVar[int]
    endu: kig
    endv: kid.kib
    endw: _containers.RepeatedCompositeFieldContainer[kiq]
    def __init__(self, endu: _Optional[_Union[kig, _Mapping]] = ..., endv: _Optional[_Union[kid.kib, str]] = ..., endw: _Optional[_Iterable[_Union[kiq, _Mapping]]] = ...) -> None: ...

class kig(_message.Message):
    __slots__ = ("enea", "eneb", "enec")
    class kie(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KIE_DWFR: _ClassVar[kig.kie]
        KIE_DWFS: _ClassVar[kig.kie]
    KIE_DWFR: kig.kie
    KIE_DWFS: kig.kie
    ENEA_FIELD_NUMBER: _ClassVar[int]
    ENEB_FIELD_NUMBER: _ClassVar[int]
    ENEC_FIELD_NUMBER: _ClassVar[int]
    enea: int
    eneb: kig.kie
    enec: kgr
    def __init__(self, enea: _Optional[int] = ..., eneb: _Optional[_Union[kig.kie, str]] = ..., enec: _Optional[_Union[kgr, str]] = ...) -> None: ...

class kih(_message.Message):
    __slots__ = ("eneg",)
    ENEG_FIELD_NUMBER: _ClassVar[int]
    eneg: int
    def __init__(self, eneg: _Optional[int] = ...) -> None: ...

class kij(_message.Message):
    __slots__ = ("enek", "enel")
    ENEK_FIELD_NUMBER: _ClassVar[int]
    ENEL_FIELD_NUMBER: _ClassVar[int]
    enek: kik
    enel: kil
    def __init__(self, enek: _Optional[_Union[kik, _Mapping]] = ..., enel: _Optional[_Union[kil, _Mapping]] = ...) -> None: ...

class kik(_message.Message):
    __slots__ = ("eneq", "ener", "enes", "enet", "eneu")
    ENEQ_FIELD_NUMBER: _ClassVar[int]
    ENER_FIELD_NUMBER: _ClassVar[int]
    ENES_FIELD_NUMBER: _ClassVar[int]
    ENET_FIELD_NUMBER: _ClassVar[int]
    ENEU_FIELD_NUMBER: _ClassVar[int]
    eneq: bool
    ener: int
    enes: str
    enet: str
    eneu: kia
    def __init__(self, eneq: bool = ..., ener: _Optional[int] = ..., enes: _Optional[str] = ..., enet: _Optional[str] = ..., eneu: _Optional[_Union[kia, _Mapping]] = ...) -> None: ...

class kil(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class kim(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class kiq(_message.Message):
    __slots__ = ("enfe", "enff", "enfg", "enfh", "enfi")
    class kio(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KIO_DWHG: _ClassVar[kiq.kio]
        KIO_DWHH: _ClassVar[kiq.kio]
        KIO_DWHI: _ClassVar[kiq.kio]
        KIO_DWHJ: _ClassVar[kiq.kio]
        KIO_DWHK: _ClassVar[kiq.kio]
        KIO_DWHL: _ClassVar[kiq.kio]
        KIO_DWHM: _ClassVar[kiq.kio]
        KIO_DWHN: _ClassVar[kiq.kio]
        KIO_DWHO: _ClassVar[kiq.kio]
        KIO_DWHP: _ClassVar[kiq.kio]
        KIO_DWHQ: _ClassVar[kiq.kio]
        KIO_DWHR: _ClassVar[kiq.kio]
        KIO_DWHS: _ClassVar[kiq.kio]
        KIO_DWHT: _ClassVar[kiq.kio]
        KIO_DWHU: _ClassVar[kiq.kio]
        KIO_DWHV: _ClassVar[kiq.kio]
        KIO_DWHW: _ClassVar[kiq.kio]
        KIO_DWHX: _ClassVar[kiq.kio]
        KIO_DWHY: _ClassVar[kiq.kio]
    KIO_DWHG: kiq.kio
    KIO_DWHH: kiq.kio
    KIO_DWHI: kiq.kio
    KIO_DWHJ: kiq.kio
    KIO_DWHK: kiq.kio
    KIO_DWHL: kiq.kio
    KIO_DWHM: kiq.kio
    KIO_DWHN: kiq.kio
    KIO_DWHO: kiq.kio
    KIO_DWHP: kiq.kio
    KIO_DWHQ: kiq.kio
    KIO_DWHR: kiq.kio
    KIO_DWHS: kiq.kio
    KIO_DWHT: kiq.kio
    KIO_DWHU: kiq.kio
    KIO_DWHV: kiq.kio
    KIO_DWHW: kiq.kio
    KIO_DWHX: kiq.kio
    KIO_DWHY: kiq.kio
    class kin(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KIN_DWHE: _ClassVar[kiq.kin]
        KIN_DWHF: _ClassVar[kiq.kin]
    KIN_DWHE: kiq.kin
    KIN_DWHF: kiq.kin
    ENFE_FIELD_NUMBER: _ClassVar[int]
    ENFF_FIELD_NUMBER: _ClassVar[int]
    ENFG_FIELD_NUMBER: _ClassVar[int]
    ENFH_FIELD_NUMBER: _ClassVar[int]
    ENFI_FIELD_NUMBER: _ClassVar[int]
    enfe: str
    enff: kiq.kio
    enfg: kiq.kin
    enfh: int
    enfi: str
    def __init__(self, enfe: _Optional[str] = ..., enff: _Optional[_Union[kiq.kio, str]] = ..., enfg: _Optional[_Union[kiq.kin, str]] = ..., enfh: _Optional[int] = ..., enfi: _Optional[str] = ...) -> None: ...

class kir(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class kiy(_message.Message):
    __slots__ = ("enfz", "enga")
    class kit(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KIT_DWIQ: _ClassVar[kiy.kit]
        KIT_DWIR: _ClassVar[kiy.kit]
    KIT_DWIQ: kiy.kit
    KIT_DWIR: kiy.kit
    class kiw(_message.Message):
        __slots__ = ("enfv",)
        class kiu(_message.Message):
            __slots__ = ("enfp", "enfq", "enfr")
            ENFP_FIELD_NUMBER: _ClassVar[int]
            ENFQ_FIELD_NUMBER: _ClassVar[int]
            ENFR_FIELD_NUMBER: _ClassVar[int]
            enfp: str
            enfq: str
            enfr: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, enfp: _Optional[str] = ..., enfq: _Optional[str] = ..., enfr: _Optional[_Iterable[int]] = ...) -> None: ...
        ENFV_FIELD_NUMBER: _ClassVar[int]
        enfv: _containers.RepeatedCompositeFieldContainer[kiy.kiw.kiu]
        def __init__(self, enfv: _Optional[_Iterable[_Union[kiy.kiw.kiu, _Mapping]]] = ...) -> None: ...
    ENFZ_FIELD_NUMBER: _ClassVar[int]
    ENGA_FIELD_NUMBER: _ClassVar[int]
    enfz: kiy.kiw
    enga: kiy.kit
    def __init__(self, enfz: _Optional[_Union[kiy.kiw, _Mapping]] = ..., enga: _Optional[_Union[kiy.kit, str]] = ...) -> None: ...

class kiz(_message.Message):
    __slots__ = ("engg", "engh")
    ENGG_FIELD_NUMBER: _ClassVar[int]
    ENGH_FIELD_NUMBER: _ClassVar[int]
    engg: str
    engh: str
    def __init__(self, engg: _Optional[str] = ..., engh: _Optional[str] = ...) -> None: ...

class kjg(_message.Message):
    __slots__ = ("engt", "engu")
    class kjb(_message.Message):
        __slots__ = ("engl",)
        ENGL_FIELD_NUMBER: _ClassVar[int]
        engl: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, engl: _Optional[_Iterable[int]] = ...) -> None: ...
    class kje(_message.Message):
        __slots__ = ("engp",)
        class kjc(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            KJC_DWKA: _ClassVar[kjg.kje.kjc]
            KJC_DWKB: _ClassVar[kjg.kje.kjc]
            KJC_DWKC: _ClassVar[kjg.kje.kjc]
            KJC_DWKD: _ClassVar[kjg.kje.kjc]
        KJC_DWKA: kjg.kje.kjc
        KJC_DWKB: kjg.kje.kjc
        KJC_DWKC: kjg.kje.kjc
        KJC_DWKD: kjg.kje.kjc
        ENGP_FIELD_NUMBER: _ClassVar[int]
        engp: kjg.kje.kjc
        def __init__(self, engp: _Optional[_Union[kjg.kje.kjc, str]] = ...) -> None: ...
    ENGT_FIELD_NUMBER: _ClassVar[int]
    ENGU_FIELD_NUMBER: _ClassVar[int]
    engt: kjg.kjb
    engu: kjg.kje
    def __init__(self, engt: _Optional[_Union[kjg.kjb, _Mapping]] = ..., engu: _Optional[_Union[kjg.kje, _Mapping]] = ...) -> None: ...
