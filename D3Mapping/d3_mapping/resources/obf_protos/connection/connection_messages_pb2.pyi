from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class lcg(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LCG_ETKY: _ClassVar[lcg]
    LCG_ETKZ: _ClassVar[lcg]
    LCG_ETLA: _ClassVar[lcg]
    LCG_ETLB: _ClassVar[lcg]
    LCG_ETLC: _ClassVar[lcg]
    LCG_ETLD: _ClassVar[lcg]
    LCG_ETLE: _ClassVar[lcg]
LCG_ETKY: lcg
LCG_ETKZ: lcg
LCG_ETLA: lcg
LCG_ETLB: lcg
LCG_ETLC: lcg
LCG_ETLD: lcg
LCG_ETLE: lcg

class lci(_message.Message):
    __slots__ = ("fptp", "fptq", "fptr")
    FPTP_FIELD_NUMBER: _ClassVar[int]
    FPTQ_FIELD_NUMBER: _ClassVar[int]
    FPTR_FIELD_NUMBER: _ClassVar[int]
    fptp: lck
    fptq: lcm
    fptr: lco
    def __init__(self, fptp: _Optional[_Union[lck, _Mapping]] = ..., fptq: _Optional[_Union[lcm, _Mapping]] = ..., fptr: _Optional[_Union[lco, _Mapping]] = ...) -> None: ...

class lck(_message.Message):
    __slots__ = ("fptw", "fptx", "fpty", "fptz", "fpua", "fpub", "fpuc", "fpud")
    FPTW_FIELD_NUMBER: _ClassVar[int]
    FPTX_FIELD_NUMBER: _ClassVar[int]
    FPTY_FIELD_NUMBER: _ClassVar[int]
    FPTZ_FIELD_NUMBER: _ClassVar[int]
    FPUA_FIELD_NUMBER: _ClassVar[int]
    FPUB_FIELD_NUMBER: _ClassVar[int]
    FPUC_FIELD_NUMBER: _ClassVar[int]
    FPUD_FIELD_NUMBER: _ClassVar[int]
    fptw: str
    fptx: lcp
    fpty: lct
    fptz: ldh
    fpua: ldw
    fpub: leb
    fpuc: leg
    fpud: leo
    def __init__(self, fptw: _Optional[str] = ..., fptx: _Optional[_Union[lcp, _Mapping]] = ..., fpty: _Optional[_Union[lct, _Mapping]] = ..., fptz: _Optional[_Union[ldh, _Mapping]] = ..., fpua: _Optional[_Union[ldw, _Mapping]] = ..., fpub: _Optional[_Union[leb, _Mapping]] = ..., fpuc: _Optional[_Union[leg, _Mapping]] = ..., fpud: _Optional[_Union[leo, _Mapping]] = ...) -> None: ...

class lcm(_message.Message):
    __slots__ = ("fpui", "fpuj", "fpuk", "fpul", "fpum", "fpun", "fpuo")
    FPUI_FIELD_NUMBER: _ClassVar[int]
    FPUJ_FIELD_NUMBER: _ClassVar[int]
    FPUK_FIELD_NUMBER: _ClassVar[int]
    FPUL_FIELD_NUMBER: _ClassVar[int]
    FPUM_FIELD_NUMBER: _ClassVar[int]
    FPUN_FIELD_NUMBER: _ClassVar[int]
    FPUO_FIELD_NUMBER: _ClassVar[int]
    fpui: str
    fpuj: lcq
    fpuk: ldg
    fpul: ldm
    fpum: ldy
    fpun: len
    fpuo: lev
    def __init__(self, fpui: _Optional[str] = ..., fpuj: _Optional[_Union[lcq, _Mapping]] = ..., fpuk: _Optional[_Union[ldg, _Mapping]] = ..., fpul: _Optional[_Union[ldm, _Mapping]] = ..., fpum: _Optional[_Union[ldy, _Mapping]] = ..., fpun: _Optional[_Union[len, _Mapping]] = ..., fpuo: _Optional[_Union[lev, _Mapping]] = ...) -> None: ...

class lco(_message.Message):
    __slots__ = ("fput",)
    FPUT_FIELD_NUMBER: _ClassVar[int]
    fput: lcr
    def __init__(self, fput: _Optional[_Union[lcr, _Mapping]] = ...) -> None: ...

class lcp(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class lcq(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class lcr(_message.Message):
    __slots__ = ("fpve",)
    FPVE_FIELD_NUMBER: _ClassVar[int]
    fpve: lds
    def __init__(self, fpve: _Optional[_Union[lds, _Mapping]] = ...) -> None: ...

class lct(_message.Message):
    __slots__ = ("fpvi", "fpvl", "fpvj", "fpvk")
    FPVI_FIELD_NUMBER: _ClassVar[int]
    FPVL_FIELD_NUMBER: _ClassVar[int]
    FPVJ_FIELD_NUMBER: _ClassVar[int]
    FPVK_FIELD_NUMBER: _ClassVar[int]
    fpvi: str
    fpvl: str
    fpvj: lcw
    fpvk: lcx
    def __init__(self, fpvi: _Optional[str] = ..., fpvl: _Optional[str] = ..., fpvj: _Optional[_Union[lcw, _Mapping]] = ..., fpvk: _Optional[_Union[lcx, _Mapping]] = ...) -> None: ...

class lcw(_message.Message):
    __slots__ = ("fpvv", "fpvw")
    class lcu(_message.Message):
        __slots__ = ("fpvq", "fpvr")
        FPVQ_FIELD_NUMBER: _ClassVar[int]
        FPVR_FIELD_NUMBER: _ClassVar[int]
        fpvq: int
        fpvr: str
        def __init__(self, fpvq: _Optional[int] = ..., fpvr: _Optional[str] = ...) -> None: ...
    FPVV_FIELD_NUMBER: _ClassVar[int]
    FPVW_FIELD_NUMBER: _ClassVar[int]
    fpvv: str
    fpvw: lcw.lcu
    def __init__(self, fpvv: _Optional[str] = ..., fpvw: _Optional[_Union[lcw.lcu, _Mapping]] = ...) -> None: ...

class lcx(_message.Message):
    __slots__ = ("fpwa",)
    FPWA_FIELD_NUMBER: _ClassVar[int]
    fpwa: str
    def __init__(self, fpwa: _Optional[str] = ...) -> None: ...

class ldg(_message.Message):
    __slots__ = ("fpxg", "fpxh")
    class ldb(_message.Message):
        __slots__ = ("fpwl", "fpwm", "fpwn", "fpwo", "fpwp", "fpwq", "fpwr", "fpwt", "fpwu")
        class lcz(_message.Message):
            __slots__ = ("fpwe", "fpwf", "fpwg", "fpwh")
            FPWE_FIELD_NUMBER: _ClassVar[int]
            FPWF_FIELD_NUMBER: _ClassVar[int]
            FPWG_FIELD_NUMBER: _ClassVar[int]
            FPWH_FIELD_NUMBER: _ClassVar[int]
            fpwe: bool
            fpwf: bool
            fpwg: bool
            fpwh: bool
            def __init__(self, fpwe: bool = ..., fpwf: bool = ..., fpwg: bool = ..., fpwh: bool = ...) -> None: ...
        FPWL_FIELD_NUMBER: _ClassVar[int]
        FPWM_FIELD_NUMBER: _ClassVar[int]
        FPWN_FIELD_NUMBER: _ClassVar[int]
        FPWO_FIELD_NUMBER: _ClassVar[int]
        FPWP_FIELD_NUMBER: _ClassVar[int]
        FPWQ_FIELD_NUMBER: _ClassVar[int]
        FPWR_FIELD_NUMBER: _ClassVar[int]
        FPWT_FIELD_NUMBER: _ClassVar[int]
        FPWU_FIELD_NUMBER: _ClassVar[int]
        fpwl: int
        fpwm: str
        fpwn: str
        fpwo: ldp
        fpwp: str
        fpwq: ldg.ldb.lcz
        fpwr: int
        fpwt: ldz
        fpwu: lew
        def __init__(self, fpwl: _Optional[int] = ..., fpwm: _Optional[str] = ..., fpwn: _Optional[str] = ..., fpwo: _Optional[_Union[ldp, _Mapping]] = ..., fpwp: _Optional[str] = ..., fpwq: _Optional[_Union[ldg.ldb.lcz, _Mapping]] = ..., fpwr: _Optional[int] = ..., fpwt: _Optional[_Union[ldz, _Mapping]] = ..., fpwu: _Optional[_Union[lew, _Mapping]] = ...) -> None: ...
    class lde(_message.Message):
        __slots__ = ("fpwy", "fpwz", "fpxb")
        class ldc(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            LDC_ETQF: _ClassVar[ldg.lde.ldc]
            LDC_ETQG: _ClassVar[ldg.lde.ldc]
            LDC_ETQH: _ClassVar[ldg.lde.ldc]
            LDC_ETQI: _ClassVar[ldg.lde.ldc]
            LDC_ETQJ: _ClassVar[ldg.lde.ldc]
            LDC_ETQK: _ClassVar[ldg.lde.ldc]
            LDC_ETQL: _ClassVar[ldg.lde.ldc]
            LDC_ETQM: _ClassVar[ldg.lde.ldc]
            LDC_ETQN: _ClassVar[ldg.lde.ldc]
            LDC_ETQO: _ClassVar[ldg.lde.ldc]
            LDC_ETQP: _ClassVar[ldg.lde.ldc]
            LDC_ETQQ: _ClassVar[ldg.lde.ldc]
            LDC_ETQR: _ClassVar[ldg.lde.ldc]
            LDC_ETQS: _ClassVar[ldg.lde.ldc]
            LDC_ETQT: _ClassVar[ldg.lde.ldc]
        LDC_ETQF: ldg.lde.ldc
        LDC_ETQG: ldg.lde.ldc
        LDC_ETQH: ldg.lde.ldc
        LDC_ETQI: ldg.lde.ldc
        LDC_ETQJ: ldg.lde.ldc
        LDC_ETQK: ldg.lde.ldc
        LDC_ETQL: ldg.lde.ldc
        LDC_ETQM: ldg.lde.ldc
        LDC_ETQN: ldg.lde.ldc
        LDC_ETQO: ldg.lde.ldc
        LDC_ETQP: ldg.lde.ldc
        LDC_ETQQ: ldg.lde.ldc
        LDC_ETQR: ldg.lde.ldc
        LDC_ETQS: ldg.lde.ldc
        LDC_ETQT: ldg.lde.ldc
        FPWY_FIELD_NUMBER: _ClassVar[int]
        FPWZ_FIELD_NUMBER: _ClassVar[int]
        FPXB_FIELD_NUMBER: _ClassVar[int]
        fpwy: ldg.lde.ldc
        fpwz: str
        fpxb: str
        def __init__(self, fpwy: _Optional[_Union[ldg.lde.ldc, str]] = ..., fpwz: _Optional[str] = ..., fpxb: _Optional[str] = ...) -> None: ...
    FPXG_FIELD_NUMBER: _ClassVar[int]
    FPXH_FIELD_NUMBER: _ClassVar[int]
    fpxg: ldg.ldb
    fpxh: ldg.lde
    def __init__(self, fpxg: _Optional[_Union[ldg.ldb, _Mapping]] = ..., fpxh: _Optional[_Union[ldg.lde, _Mapping]] = ...) -> None: ...

class ldh(_message.Message):
    __slots__ = ("fpxm",)
    FPXM_FIELD_NUMBER: _ClassVar[int]
    fpxm: int
    def __init__(self, fpxm: _Optional[int] = ...) -> None: ...

class ldm(_message.Message):
    __slots__ = ("fpxw", "fpxx")
    class ldj(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LDJ_ETRR: _ClassVar[ldm.ldj]
        LDJ_ETRS: _ClassVar[ldm.ldj]
        LDJ_ETRT: _ClassVar[ldm.ldj]
        LDJ_ETRU: _ClassVar[ldm.ldj]
    LDJ_ETRR: ldm.ldj
    LDJ_ETRS: ldm.ldj
    LDJ_ETRT: ldm.ldj
    LDJ_ETRU: ldm.ldj
    class ldk(_message.Message):
        __slots__ = ("fpxq", "fpxr", "fpxs")
        FPXQ_FIELD_NUMBER: _ClassVar[int]
        FPXR_FIELD_NUMBER: _ClassVar[int]
        FPXS_FIELD_NUMBER: _ClassVar[int]
        fpxq: str
        fpxr: str
        fpxs: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, fpxq: _Optional[str] = ..., fpxr: _Optional[str] = ..., fpxs: _Optional[_Iterable[int]] = ...) -> None: ...
    FPXW_FIELD_NUMBER: _ClassVar[int]
    FPXX_FIELD_NUMBER: _ClassVar[int]
    fpxw: ldm.ldk
    fpxx: ldm.ldj
    def __init__(self, fpxw: _Optional[_Union[ldm.ldk, _Mapping]] = ..., fpxx: _Optional[_Union[ldm.ldj, str]] = ...) -> None: ...

class ldp(_message.Message):
    __slots__ = ("fpyi", "fpyj", "fpyk")
    class ldn(_message.Message):
        __slots__ = ("fpyd", "fpye")
        FPYD_FIELD_NUMBER: _ClassVar[int]
        FPYE_FIELD_NUMBER: _ClassVar[int]
        fpyd: lcg
        fpye: int
        def __init__(self, fpyd: _Optional[_Union[lcg, str]] = ..., fpye: _Optional[int] = ...) -> None: ...
    FPYI_FIELD_NUMBER: _ClassVar[int]
    FPYJ_FIELD_NUMBER: _ClassVar[int]
    FPYK_FIELD_NUMBER: _ClassVar[int]
    fpyi: _containers.RepeatedCompositeFieldContainer[lds]
    fpyj: _containers.RepeatedCompositeFieldContainer[ldp.ldn]
    fpyk: bool
    def __init__(self, fpyi: _Optional[_Iterable[_Union[lds, _Mapping]]] = ..., fpyj: _Optional[_Iterable[_Union[ldp.ldn, _Mapping]]] = ..., fpyk: bool = ...) -> None: ...

class lds(_message.Message):
    __slots__ = ("fpyo", "fpyp", "fpyq")
    class ldq(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LDQ_ETTA: _ClassVar[lds.ldq]
        LDQ_ETTB: _ClassVar[lds.ldq]
        LDQ_ETTC: _ClassVar[lds.ldq]
        LDQ_ETTD: _ClassVar[lds.ldq]
    LDQ_ETTA: lds.ldq
    LDQ_ETTB: lds.ldq
    LDQ_ETTC: lds.ldq
    LDQ_ETTD: lds.ldq
    FPYO_FIELD_NUMBER: _ClassVar[int]
    FPYP_FIELD_NUMBER: _ClassVar[int]
    FPYQ_FIELD_NUMBER: _ClassVar[int]
    fpyo: ldv
    fpyp: lds.ldq
    fpyq: _containers.RepeatedCompositeFieldContainer[lef]
    def __init__(self, fpyo: _Optional[_Union[ldv, _Mapping]] = ..., fpyp: _Optional[_Union[lds.ldq, str]] = ..., fpyq: _Optional[_Iterable[_Union[lef, _Mapping]]] = ...) -> None: ...

class ldv(_message.Message):
    __slots__ = ("fpyu", "fpyv", "fpyw")
    class ldt(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LDT_ETTN: _ClassVar[ldv.ldt]
        LDT_ETTO: _ClassVar[ldv.ldt]
    LDT_ETTN: ldv.ldt
    LDT_ETTO: ldv.ldt
    FPYU_FIELD_NUMBER: _ClassVar[int]
    FPYV_FIELD_NUMBER: _ClassVar[int]
    FPYW_FIELD_NUMBER: _ClassVar[int]
    fpyu: int
    fpyv: ldv.ldt
    fpyw: lcg
    def __init__(self, fpyu: _Optional[int] = ..., fpyv: _Optional[_Union[ldv.ldt, str]] = ..., fpyw: _Optional[_Union[lcg, str]] = ...) -> None: ...

class ldw(_message.Message):
    __slots__ = ("fpza",)
    FPZA_FIELD_NUMBER: _ClassVar[int]
    fpza: int
    def __init__(self, fpza: _Optional[int] = ...) -> None: ...

class ldy(_message.Message):
    __slots__ = ("fpze", "fpzf")
    FPZE_FIELD_NUMBER: _ClassVar[int]
    FPZF_FIELD_NUMBER: _ClassVar[int]
    fpze: ldz
    fpzf: lea
    def __init__(self, fpze: _Optional[_Union[ldz, _Mapping]] = ..., fpzf: _Optional[_Union[lea, _Mapping]] = ...) -> None: ...

class ldz(_message.Message):
    __slots__ = ("fpzk", "fpzl", "fpzm", "fpzn", "fpzo")
    FPZK_FIELD_NUMBER: _ClassVar[int]
    FPZL_FIELD_NUMBER: _ClassVar[int]
    FPZM_FIELD_NUMBER: _ClassVar[int]
    FPZN_FIELD_NUMBER: _ClassVar[int]
    FPZO_FIELD_NUMBER: _ClassVar[int]
    fpzk: bool
    fpzl: int
    fpzm: str
    fpzn: str
    fpzo: ldp
    def __init__(self, fpzk: bool = ..., fpzl: _Optional[int] = ..., fpzm: _Optional[str] = ..., fpzn: _Optional[str] = ..., fpzo: _Optional[_Union[ldp, _Mapping]] = ...) -> None: ...

class lea(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class leb(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class lef(_message.Message):
    __slots__ = ("fpzy", "fpzz", "fqaa", "fqab", "fqac")
    class led(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LED_ETVC: _ClassVar[lef.led]
        LED_ETVD: _ClassVar[lef.led]
        LED_ETVE: _ClassVar[lef.led]
        LED_ETVF: _ClassVar[lef.led]
        LED_ETVG: _ClassVar[lef.led]
        LED_ETVH: _ClassVar[lef.led]
        LED_ETVI: _ClassVar[lef.led]
        LED_ETVJ: _ClassVar[lef.led]
        LED_ETVK: _ClassVar[lef.led]
        LED_ETVL: _ClassVar[lef.led]
        LED_ETVM: _ClassVar[lef.led]
        LED_ETVN: _ClassVar[lef.led]
        LED_ETVO: _ClassVar[lef.led]
        LED_ETVP: _ClassVar[lef.led]
        LED_ETVQ: _ClassVar[lef.led]
        LED_ETVR: _ClassVar[lef.led]
        LED_ETVS: _ClassVar[lef.led]
        LED_ETVT: _ClassVar[lef.led]
        LED_ETVU: _ClassVar[lef.led]
    LED_ETVC: lef.led
    LED_ETVD: lef.led
    LED_ETVE: lef.led
    LED_ETVF: lef.led
    LED_ETVG: lef.led
    LED_ETVH: lef.led
    LED_ETVI: lef.led
    LED_ETVJ: lef.led
    LED_ETVK: lef.led
    LED_ETVL: lef.led
    LED_ETVM: lef.led
    LED_ETVN: lef.led
    LED_ETVO: lef.led
    LED_ETVP: lef.led
    LED_ETVQ: lef.led
    LED_ETVR: lef.led
    LED_ETVS: lef.led
    LED_ETVT: lef.led
    LED_ETVU: lef.led
    class lec(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LEC_ETVA: _ClassVar[lef.lec]
        LEC_ETVB: _ClassVar[lef.lec]
    LEC_ETVA: lef.lec
    LEC_ETVB: lef.lec
    FPZY_FIELD_NUMBER: _ClassVar[int]
    FPZZ_FIELD_NUMBER: _ClassVar[int]
    FQAA_FIELD_NUMBER: _ClassVar[int]
    FQAB_FIELD_NUMBER: _ClassVar[int]
    FQAC_FIELD_NUMBER: _ClassVar[int]
    fpzy: str
    fpzz: lef.led
    fqaa: lef.lec
    fqab: int
    fqac: str
    def __init__(self, fpzy: _Optional[str] = ..., fpzz: _Optional[_Union[lef.led, str]] = ..., fqaa: _Optional[_Union[lef.lec, str]] = ..., fqab: _Optional[int] = ..., fqac: _Optional[str] = ...) -> None: ...

class leg(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class len(_message.Message):
    __slots__ = ("fqat", "fqau")
    class lei(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LEI_ETWM: _ClassVar[len.lei]
        LEI_ETWN: _ClassVar[len.lei]
    LEI_ETWM: len.lei
    LEI_ETWN: len.lei
    class lel(_message.Message):
        __slots__ = ("fqap",)
        class lej(_message.Message):
            __slots__ = ("fqaj", "fqak", "fqal")
            FQAJ_FIELD_NUMBER: _ClassVar[int]
            FQAK_FIELD_NUMBER: _ClassVar[int]
            FQAL_FIELD_NUMBER: _ClassVar[int]
            fqaj: str
            fqak: str
            fqal: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, fqaj: _Optional[str] = ..., fqak: _Optional[str] = ..., fqal: _Optional[_Iterable[int]] = ...) -> None: ...
        FQAP_FIELD_NUMBER: _ClassVar[int]
        fqap: _containers.RepeatedCompositeFieldContainer[len.lel.lej]
        def __init__(self, fqap: _Optional[_Iterable[_Union[len.lel.lej, _Mapping]]] = ...) -> None: ...
    FQAT_FIELD_NUMBER: _ClassVar[int]
    FQAU_FIELD_NUMBER: _ClassVar[int]
    fqat: len.lel
    fqau: len.lei
    def __init__(self, fqat: _Optional[_Union[len.lel, _Mapping]] = ..., fqau: _Optional[_Union[len.lei, str]] = ...) -> None: ...

class leo(_message.Message):
    __slots__ = ("fqba", "fqbb")
    FQBA_FIELD_NUMBER: _ClassVar[int]
    FQBB_FIELD_NUMBER: _ClassVar[int]
    fqba: str
    fqbb: str
    def __init__(self, fqba: _Optional[str] = ..., fqbb: _Optional[str] = ...) -> None: ...

class lev(_message.Message):
    __slots__ = ("fqbn", "fqbo")
    class leq(_message.Message):
        __slots__ = ("fqbf",)
        FQBF_FIELD_NUMBER: _ClassVar[int]
        fqbf: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, fqbf: _Optional[_Iterable[int]] = ...) -> None: ...
    class let(_message.Message):
        __slots__ = ("fqbj",)
        class ler(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            LER_ETXW: _ClassVar[lev.let.ler]
            LER_ETXX: _ClassVar[lev.let.ler]
            LER_ETXY: _ClassVar[lev.let.ler]
            LER_ETXZ: _ClassVar[lev.let.ler]
        LER_ETXW: lev.let.ler
        LER_ETXX: lev.let.ler
        LER_ETXY: lev.let.ler
        LER_ETXZ: lev.let.ler
        FQBJ_FIELD_NUMBER: _ClassVar[int]
        fqbj: lev.let.ler
        def __init__(self, fqbj: _Optional[_Union[lev.let.ler, str]] = ...) -> None: ...
    FQBN_FIELD_NUMBER: _ClassVar[int]
    FQBO_FIELD_NUMBER: _ClassVar[int]
    fqbn: lev.leq
    fqbo: lev.let
    def __init__(self, fqbn: _Optional[_Union[lev.leq, _Mapping]] = ..., fqbo: _Optional[_Union[lev.let, _Mapping]] = ...) -> None: ...

class lew(_message.Message):
    __slots__ = ("fqbt", "fqbu", "fqbv")
    FQBT_FIELD_NUMBER: _ClassVar[int]
    FQBU_FIELD_NUMBER: _ClassVar[int]
    FQBV_FIELD_NUMBER: _ClassVar[int]
    fqbt: str
    fqbu: str
    fqbv: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, fqbt: _Optional[str] = ..., fqbu: _Optional[str] = ..., fqbv: _Optional[_Iterable[int]] = ...) -> None: ...
