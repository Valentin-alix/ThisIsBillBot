from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class lbq(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LBQ_ETWL: _ClassVar[lbq]
    LBQ_ETWM: _ClassVar[lbq]
    LBQ_ETWN: _ClassVar[lbq]
    LBQ_ETWO: _ClassVar[lbq]
    LBQ_ETWP: _ClassVar[lbq]
    LBQ_ETWQ: _ClassVar[lbq]
    LBQ_ETWR: _ClassVar[lbq]
LBQ_ETWL: lbq
LBQ_ETWM: lbq
LBQ_ETWN: lbq
LBQ_ETWO: lbq
LBQ_ETWP: lbq
LBQ_ETWQ: lbq
LBQ_ETWR: lbq

class lbs(_message.Message):
    __slots__ = ("fqiu", "fqiv", "fqiw")
    FQIU_FIELD_NUMBER: _ClassVar[int]
    FQIV_FIELD_NUMBER: _ClassVar[int]
    FQIW_FIELD_NUMBER: _ClassVar[int]
    fqiu: lbu
    fqiv: lbw
    fqiw: lby
    def __init__(self, fqiu: _Optional[_Union[lbu, _Mapping]] = ..., fqiv: _Optional[_Union[lbw, _Mapping]] = ..., fqiw: _Optional[_Union[lby, _Mapping]] = ...) -> None: ...

class lbu(_message.Message):
    __slots__ = ("fqjb", "fqjc", "fqjd", "fqje", "fqjf", "fqjg", "fqjh", "fqji")
    FQJB_FIELD_NUMBER: _ClassVar[int]
    FQJC_FIELD_NUMBER: _ClassVar[int]
    FQJD_FIELD_NUMBER: _ClassVar[int]
    FQJE_FIELD_NUMBER: _ClassVar[int]
    FQJF_FIELD_NUMBER: _ClassVar[int]
    FQJG_FIELD_NUMBER: _ClassVar[int]
    FQJH_FIELD_NUMBER: _ClassVar[int]
    FQJI_FIELD_NUMBER: _ClassVar[int]
    fqjb: str
    fqjc: lbz
    fqjd: lcd
    fqje: lcr
    fqjf: ldg
    fqjg: ldl
    fqjh: ldq
    fqji: ldy
    def __init__(self, fqjb: _Optional[str] = ..., fqjc: _Optional[_Union[lbz, _Mapping]] = ..., fqjd: _Optional[_Union[lcd, _Mapping]] = ..., fqje: _Optional[_Union[lcr, _Mapping]] = ..., fqjf: _Optional[_Union[ldg, _Mapping]] = ..., fqjg: _Optional[_Union[ldl, _Mapping]] = ..., fqjh: _Optional[_Union[ldq, _Mapping]] = ..., fqji: _Optional[_Union[ldy, _Mapping]] = ...) -> None: ...

class lbw(_message.Message):
    __slots__ = ("fqjn", "fqjo", "fqjp", "fqjq", "fqjr", "fqjs", "fqjt")
    FQJN_FIELD_NUMBER: _ClassVar[int]
    FQJO_FIELD_NUMBER: _ClassVar[int]
    FQJP_FIELD_NUMBER: _ClassVar[int]
    FQJQ_FIELD_NUMBER: _ClassVar[int]
    FQJR_FIELD_NUMBER: _ClassVar[int]
    FQJS_FIELD_NUMBER: _ClassVar[int]
    FQJT_FIELD_NUMBER: _ClassVar[int]
    fqjn: str
    fqjo: lca
    fqjp: lcq
    fqjq: lcw
    fqjr: ldi
    fqjs: ldx
    fqjt: lef
    def __init__(self, fqjn: _Optional[str] = ..., fqjo: _Optional[_Union[lca, _Mapping]] = ..., fqjp: _Optional[_Union[lcq, _Mapping]] = ..., fqjq: _Optional[_Union[lcw, _Mapping]] = ..., fqjr: _Optional[_Union[ldi, _Mapping]] = ..., fqjs: _Optional[_Union[ldx, _Mapping]] = ..., fqjt: _Optional[_Union[lef, _Mapping]] = ...) -> None: ...

class lby(_message.Message):
    __slots__ = ("fqjy",)
    FQJY_FIELD_NUMBER: _ClassVar[int]
    fqjy: lcb
    def __init__(self, fqjy: _Optional[_Union[lcb, _Mapping]] = ...) -> None: ...

class lbz(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class lca(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class lcb(_message.Message):
    __slots__ = ("fqkj",)
    FQKJ_FIELD_NUMBER: _ClassVar[int]
    fqkj: ldc
    def __init__(self, fqkj: _Optional[_Union[ldc, _Mapping]] = ...) -> None: ...

class lcd(_message.Message):
    __slots__ = ("fqkn", "fqkq", "fqko", "fqkp")
    FQKN_FIELD_NUMBER: _ClassVar[int]
    FQKQ_FIELD_NUMBER: _ClassVar[int]
    FQKO_FIELD_NUMBER: _ClassVar[int]
    FQKP_FIELD_NUMBER: _ClassVar[int]
    fqkn: str
    fqkq: str
    fqko: lcg
    fqkp: lch
    def __init__(self, fqkn: _Optional[str] = ..., fqkq: _Optional[str] = ..., fqko: _Optional[_Union[lcg, _Mapping]] = ..., fqkp: _Optional[_Union[lch, _Mapping]] = ...) -> None: ...

class lcg(_message.Message):
    __slots__ = ("fqla", "fqlb")
    class lce(_message.Message):
        __slots__ = ("fqkv", "fqkw")
        FQKV_FIELD_NUMBER: _ClassVar[int]
        FQKW_FIELD_NUMBER: _ClassVar[int]
        fqkv: int
        fqkw: str
        def __init__(self, fqkv: _Optional[int] = ..., fqkw: _Optional[str] = ...) -> None: ...
    FQLA_FIELD_NUMBER: _ClassVar[int]
    FQLB_FIELD_NUMBER: _ClassVar[int]
    fqla: str
    fqlb: lcg.lce
    def __init__(self, fqla: _Optional[str] = ..., fqlb: _Optional[_Union[lcg.lce, _Mapping]] = ...) -> None: ...

class lch(_message.Message):
    __slots__ = ("fqlf",)
    FQLF_FIELD_NUMBER: _ClassVar[int]
    fqlf: str
    def __init__(self, fqlf: _Optional[str] = ...) -> None: ...

class lcq(_message.Message):
    __slots__ = ("fqml", "fqmm")
    class lcl(_message.Message):
        __slots__ = ("fqlq", "fqlr", "fqls", "fqlt", "fqlu", "fqlv", "fqlw", "fqly", "fqlz")
        class lcj(_message.Message):
            __slots__ = ("fqlj", "fqlk", "fqll", "fqlm")
            FQLJ_FIELD_NUMBER: _ClassVar[int]
            FQLK_FIELD_NUMBER: _ClassVar[int]
            FQLL_FIELD_NUMBER: _ClassVar[int]
            FQLM_FIELD_NUMBER: _ClassVar[int]
            fqlj: bool
            fqlk: bool
            fqll: bool
            fqlm: bool
            def __init__(self, fqlj: bool = ..., fqlk: bool = ..., fqll: bool = ..., fqlm: bool = ...) -> None: ...
        FQLQ_FIELD_NUMBER: _ClassVar[int]
        FQLR_FIELD_NUMBER: _ClassVar[int]
        FQLS_FIELD_NUMBER: _ClassVar[int]
        FQLT_FIELD_NUMBER: _ClassVar[int]
        FQLU_FIELD_NUMBER: _ClassVar[int]
        FQLV_FIELD_NUMBER: _ClassVar[int]
        FQLW_FIELD_NUMBER: _ClassVar[int]
        FQLY_FIELD_NUMBER: _ClassVar[int]
        FQLZ_FIELD_NUMBER: _ClassVar[int]
        fqlq: int
        fqlr: str
        fqls: str
        fqlt: lcz
        fqlu: str
        fqlv: lcq.lcl.lcj
        fqlw: int
        fqly: ldj
        fqlz: leg
        def __init__(self, fqlq: _Optional[int] = ..., fqlr: _Optional[str] = ..., fqls: _Optional[str] = ..., fqlt: _Optional[_Union[lcz, _Mapping]] = ..., fqlu: _Optional[str] = ..., fqlv: _Optional[_Union[lcq.lcl.lcj, _Mapping]] = ..., fqlw: _Optional[int] = ..., fqly: _Optional[_Union[ldj, _Mapping]] = ..., fqlz: _Optional[_Union[leg, _Mapping]] = ...) -> None: ...
    class lco(_message.Message):
        __slots__ = ("fqmd", "fqme", "fqmg")
        class lcm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            LCM_EUBS: _ClassVar[lcq.lco.lcm]
            LCM_EUBT: _ClassVar[lcq.lco.lcm]
            LCM_EUBU: _ClassVar[lcq.lco.lcm]
            LCM_EUBV: _ClassVar[lcq.lco.lcm]
            LCM_EUBW: _ClassVar[lcq.lco.lcm]
            LCM_EUBX: _ClassVar[lcq.lco.lcm]
            LCM_EUBY: _ClassVar[lcq.lco.lcm]
            LCM_EUBZ: _ClassVar[lcq.lco.lcm]
            LCM_EUCA: _ClassVar[lcq.lco.lcm]
            LCM_EUCB: _ClassVar[lcq.lco.lcm]
            LCM_EUCC: _ClassVar[lcq.lco.lcm]
            LCM_EUCD: _ClassVar[lcq.lco.lcm]
            LCM_EUCE: _ClassVar[lcq.lco.lcm]
            LCM_EUCF: _ClassVar[lcq.lco.lcm]
            LCM_EUCG: _ClassVar[lcq.lco.lcm]
        LCM_EUBS: lcq.lco.lcm
        LCM_EUBT: lcq.lco.lcm
        LCM_EUBU: lcq.lco.lcm
        LCM_EUBV: lcq.lco.lcm
        LCM_EUBW: lcq.lco.lcm
        LCM_EUBX: lcq.lco.lcm
        LCM_EUBY: lcq.lco.lcm
        LCM_EUBZ: lcq.lco.lcm
        LCM_EUCA: lcq.lco.lcm
        LCM_EUCB: lcq.lco.lcm
        LCM_EUCC: lcq.lco.lcm
        LCM_EUCD: lcq.lco.lcm
        LCM_EUCE: lcq.lco.lcm
        LCM_EUCF: lcq.lco.lcm
        LCM_EUCG: lcq.lco.lcm
        FQMD_FIELD_NUMBER: _ClassVar[int]
        FQME_FIELD_NUMBER: _ClassVar[int]
        FQMG_FIELD_NUMBER: _ClassVar[int]
        fqmd: lcq.lco.lcm
        fqme: str
        fqmg: str
        def __init__(self, fqmd: _Optional[_Union[lcq.lco.lcm, str]] = ..., fqme: _Optional[str] = ..., fqmg: _Optional[str] = ...) -> None: ...
    FQML_FIELD_NUMBER: _ClassVar[int]
    FQMM_FIELD_NUMBER: _ClassVar[int]
    fqml: lcq.lcl
    fqmm: lcq.lco
    def __init__(self, fqml: _Optional[_Union[lcq.lcl, _Mapping]] = ..., fqmm: _Optional[_Union[lcq.lco, _Mapping]] = ...) -> None: ...

class lcr(_message.Message):
    __slots__ = ("fqmr",)
    FQMR_FIELD_NUMBER: _ClassVar[int]
    fqmr: int
    def __init__(self, fqmr: _Optional[int] = ...) -> None: ...

class lcw(_message.Message):
    __slots__ = ("fqnb", "fqnc")
    class lct(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LCT_EUDE: _ClassVar[lcw.lct]
        LCT_EUDF: _ClassVar[lcw.lct]
        LCT_EUDG: _ClassVar[lcw.lct]
        LCT_EUDH: _ClassVar[lcw.lct]
    LCT_EUDE: lcw.lct
    LCT_EUDF: lcw.lct
    LCT_EUDG: lcw.lct
    LCT_EUDH: lcw.lct
    class lcu(_message.Message):
        __slots__ = ("fqmv", "fqmw", "fqmx")
        FQMV_FIELD_NUMBER: _ClassVar[int]
        FQMW_FIELD_NUMBER: _ClassVar[int]
        FQMX_FIELD_NUMBER: _ClassVar[int]
        fqmv: str
        fqmw: str
        fqmx: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, fqmv: _Optional[str] = ..., fqmw: _Optional[str] = ..., fqmx: _Optional[_Iterable[int]] = ...) -> None: ...
    FQNB_FIELD_NUMBER: _ClassVar[int]
    FQNC_FIELD_NUMBER: _ClassVar[int]
    fqnb: lcw.lcu
    fqnc: lcw.lct
    def __init__(self, fqnb: _Optional[_Union[lcw.lcu, _Mapping]] = ..., fqnc: _Optional[_Union[lcw.lct, str]] = ...) -> None: ...

class lcz(_message.Message):
    __slots__ = ("fqnn", "fqno", "fqnp")
    class lcx(_message.Message):
        __slots__ = ("fqni", "fqnj")
        FQNI_FIELD_NUMBER: _ClassVar[int]
        FQNJ_FIELD_NUMBER: _ClassVar[int]
        fqni: lbq
        fqnj: int
        def __init__(self, fqni: _Optional[_Union[lbq, str]] = ..., fqnj: _Optional[int] = ...) -> None: ...
    FQNN_FIELD_NUMBER: _ClassVar[int]
    FQNO_FIELD_NUMBER: _ClassVar[int]
    FQNP_FIELD_NUMBER: _ClassVar[int]
    fqnn: _containers.RepeatedCompositeFieldContainer[ldc]
    fqno: _containers.RepeatedCompositeFieldContainer[lcz.lcx]
    fqnp: bool
    def __init__(self, fqnn: _Optional[_Iterable[_Union[ldc, _Mapping]]] = ..., fqno: _Optional[_Iterable[_Union[lcz.lcx, _Mapping]]] = ..., fqnp: bool = ...) -> None: ...

class ldc(_message.Message):
    __slots__ = ("fqnt", "fqnu", "fqnv")
    class lda(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LDA_EUEN: _ClassVar[ldc.lda]
        LDA_EUEO: _ClassVar[ldc.lda]
        LDA_EUEP: _ClassVar[ldc.lda]
        LDA_EUEQ: _ClassVar[ldc.lda]
    LDA_EUEN: ldc.lda
    LDA_EUEO: ldc.lda
    LDA_EUEP: ldc.lda
    LDA_EUEQ: ldc.lda
    FQNT_FIELD_NUMBER: _ClassVar[int]
    FQNU_FIELD_NUMBER: _ClassVar[int]
    FQNV_FIELD_NUMBER: _ClassVar[int]
    fqnt: ldf
    fqnu: ldc.lda
    fqnv: _containers.RepeatedCompositeFieldContainer[ldp]
    def __init__(self, fqnt: _Optional[_Union[ldf, _Mapping]] = ..., fqnu: _Optional[_Union[ldc.lda, str]] = ..., fqnv: _Optional[_Iterable[_Union[ldp, _Mapping]]] = ...) -> None: ...

class ldf(_message.Message):
    __slots__ = ("fqnz", "fqoa", "fqob")
    class ldd(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LDD_EUFA: _ClassVar[ldf.ldd]
        LDD_EUFB: _ClassVar[ldf.ldd]
    LDD_EUFA: ldf.ldd
    LDD_EUFB: ldf.ldd
    FQNZ_FIELD_NUMBER: _ClassVar[int]
    FQOA_FIELD_NUMBER: _ClassVar[int]
    FQOB_FIELD_NUMBER: _ClassVar[int]
    fqnz: int
    fqoa: ldf.ldd
    fqob: lbq
    def __init__(self, fqnz: _Optional[int] = ..., fqoa: _Optional[_Union[ldf.ldd, str]] = ..., fqob: _Optional[_Union[lbq, str]] = ...) -> None: ...

class ldg(_message.Message):
    __slots__ = ("fqof",)
    FQOF_FIELD_NUMBER: _ClassVar[int]
    fqof: int
    def __init__(self, fqof: _Optional[int] = ...) -> None: ...

class ldi(_message.Message):
    __slots__ = ("fqoj", "fqok")
    FQOJ_FIELD_NUMBER: _ClassVar[int]
    FQOK_FIELD_NUMBER: _ClassVar[int]
    fqoj: ldj
    fqok: ldk
    def __init__(self, fqoj: _Optional[_Union[ldj, _Mapping]] = ..., fqok: _Optional[_Union[ldk, _Mapping]] = ...) -> None: ...

class ldj(_message.Message):
    __slots__ = ("fqop", "fqoq", "fqor", "fqos", "fqot")
    FQOP_FIELD_NUMBER: _ClassVar[int]
    FQOQ_FIELD_NUMBER: _ClassVar[int]
    FQOR_FIELD_NUMBER: _ClassVar[int]
    FQOS_FIELD_NUMBER: _ClassVar[int]
    FQOT_FIELD_NUMBER: _ClassVar[int]
    fqop: bool
    fqoq: int
    fqor: str
    fqos: str
    fqot: lcz
    def __init__(self, fqop: bool = ..., fqoq: _Optional[int] = ..., fqor: _Optional[str] = ..., fqos: _Optional[str] = ..., fqot: _Optional[_Union[lcz, _Mapping]] = ...) -> None: ...

class ldk(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ldl(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ldp(_message.Message):
    __slots__ = ("fqpd", "fqpe", "fqpf", "fqpg", "fqph")
    class ldn(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LDN_EUGP: _ClassVar[ldp.ldn]
        LDN_EUGQ: _ClassVar[ldp.ldn]
        LDN_EUGR: _ClassVar[ldp.ldn]
        LDN_EUGS: _ClassVar[ldp.ldn]
        LDN_EUGT: _ClassVar[ldp.ldn]
        LDN_EUGU: _ClassVar[ldp.ldn]
        LDN_EUGV: _ClassVar[ldp.ldn]
        LDN_EUGW: _ClassVar[ldp.ldn]
        LDN_EUGX: _ClassVar[ldp.ldn]
        LDN_EUGY: _ClassVar[ldp.ldn]
        LDN_EUGZ: _ClassVar[ldp.ldn]
        LDN_EUHA: _ClassVar[ldp.ldn]
        LDN_EUHB: _ClassVar[ldp.ldn]
        LDN_EUHC: _ClassVar[ldp.ldn]
        LDN_EUHD: _ClassVar[ldp.ldn]
        LDN_EUHE: _ClassVar[ldp.ldn]
        LDN_EUHF: _ClassVar[ldp.ldn]
        LDN_EUHG: _ClassVar[ldp.ldn]
        LDN_EUHH: _ClassVar[ldp.ldn]
    LDN_EUGP: ldp.ldn
    LDN_EUGQ: ldp.ldn
    LDN_EUGR: ldp.ldn
    LDN_EUGS: ldp.ldn
    LDN_EUGT: ldp.ldn
    LDN_EUGU: ldp.ldn
    LDN_EUGV: ldp.ldn
    LDN_EUGW: ldp.ldn
    LDN_EUGX: ldp.ldn
    LDN_EUGY: ldp.ldn
    LDN_EUGZ: ldp.ldn
    LDN_EUHA: ldp.ldn
    LDN_EUHB: ldp.ldn
    LDN_EUHC: ldp.ldn
    LDN_EUHD: ldp.ldn
    LDN_EUHE: ldp.ldn
    LDN_EUHF: ldp.ldn
    LDN_EUHG: ldp.ldn
    LDN_EUHH: ldp.ldn
    class ldm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LDM_EUGN: _ClassVar[ldp.ldm]
        LDM_EUGO: _ClassVar[ldp.ldm]
    LDM_EUGN: ldp.ldm
    LDM_EUGO: ldp.ldm
    FQPD_FIELD_NUMBER: _ClassVar[int]
    FQPE_FIELD_NUMBER: _ClassVar[int]
    FQPF_FIELD_NUMBER: _ClassVar[int]
    FQPG_FIELD_NUMBER: _ClassVar[int]
    FQPH_FIELD_NUMBER: _ClassVar[int]
    fqpd: str
    fqpe: ldp.ldn
    fqpf: ldp.ldm
    fqpg: int
    fqph: str
    def __init__(self, fqpd: _Optional[str] = ..., fqpe: _Optional[_Union[ldp.ldn, str]] = ..., fqpf: _Optional[_Union[ldp.ldm, str]] = ..., fqpg: _Optional[int] = ..., fqph: _Optional[str] = ...) -> None: ...

class ldq(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ldx(_message.Message):
    __slots__ = ("fqpy", "fqpz")
    class lds(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LDS_EUHZ: _ClassVar[ldx.lds]
        LDS_EUIA: _ClassVar[ldx.lds]
    LDS_EUHZ: ldx.lds
    LDS_EUIA: ldx.lds
    class ldv(_message.Message):
        __slots__ = ("fqpu",)
        class ldt(_message.Message):
            __slots__ = ("fqpo", "fqpp", "fqpq")
            FQPO_FIELD_NUMBER: _ClassVar[int]
            FQPP_FIELD_NUMBER: _ClassVar[int]
            FQPQ_FIELD_NUMBER: _ClassVar[int]
            fqpo: str
            fqpp: str
            fqpq: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, fqpo: _Optional[str] = ..., fqpp: _Optional[str] = ..., fqpq: _Optional[_Iterable[int]] = ...) -> None: ...
        FQPU_FIELD_NUMBER: _ClassVar[int]
        fqpu: _containers.RepeatedCompositeFieldContainer[ldx.ldv.ldt]
        def __init__(self, fqpu: _Optional[_Iterable[_Union[ldx.ldv.ldt, _Mapping]]] = ...) -> None: ...
    FQPY_FIELD_NUMBER: _ClassVar[int]
    FQPZ_FIELD_NUMBER: _ClassVar[int]
    fqpy: ldx.ldv
    fqpz: ldx.lds
    def __init__(self, fqpy: _Optional[_Union[ldx.ldv, _Mapping]] = ..., fqpz: _Optional[_Union[ldx.lds, str]] = ...) -> None: ...

class ldy(_message.Message):
    __slots__ = ("fqqf", "fqqg")
    FQQF_FIELD_NUMBER: _ClassVar[int]
    FQQG_FIELD_NUMBER: _ClassVar[int]
    fqqf: str
    fqqg: str
    def __init__(self, fqqf: _Optional[str] = ..., fqqg: _Optional[str] = ...) -> None: ...

class lef(_message.Message):
    __slots__ = ("fqqs", "fqqt")
    class lea(_message.Message):
        __slots__ = ("fqqk",)
        FQQK_FIELD_NUMBER: _ClassVar[int]
        fqqk: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, fqqk: _Optional[_Iterable[int]] = ...) -> None: ...
    class led(_message.Message):
        __slots__ = ("fqqo",)
        class leb(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            LEB_EUJJ: _ClassVar[lef.led.leb]
            LEB_EUJK: _ClassVar[lef.led.leb]
            LEB_EUJL: _ClassVar[lef.led.leb]
            LEB_EUJM: _ClassVar[lef.led.leb]
        LEB_EUJJ: lef.led.leb
        LEB_EUJK: lef.led.leb
        LEB_EUJL: lef.led.leb
        LEB_EUJM: lef.led.leb
        FQQO_FIELD_NUMBER: _ClassVar[int]
        fqqo: lef.led.leb
        def __init__(self, fqqo: _Optional[_Union[lef.led.leb, str]] = ...) -> None: ...
    FQQS_FIELD_NUMBER: _ClassVar[int]
    FQQT_FIELD_NUMBER: _ClassVar[int]
    fqqs: lef.lea
    fqqt: lef.led
    def __init__(self, fqqs: _Optional[_Union[lef.lea, _Mapping]] = ..., fqqt: _Optional[_Union[lef.led, _Mapping]] = ...) -> None: ...

class leg(_message.Message):
    __slots__ = ("fqqy", "fqqz", "fqra")
    FQQY_FIELD_NUMBER: _ClassVar[int]
    FQQZ_FIELD_NUMBER: _ClassVar[int]
    FQRA_FIELD_NUMBER: _ClassVar[int]
    fqqy: str
    fqqz: str
    fqra: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, fqqy: _Optional[str] = ..., fqqz: _Optional[str] = ..., fqra: _Optional[_Iterable[int]] = ...) -> None: ...
