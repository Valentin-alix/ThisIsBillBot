from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class lbp(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LBP_ESZK: _ClassVar[lbp]
    LBP_ESZL: _ClassVar[lbp]
    LBP_ESZM: _ClassVar[lbp]
    LBP_ESZN: _ClassVar[lbp]
    LBP_ESZO: _ClassVar[lbp]
    LBP_ESZP: _ClassVar[lbp]
    LBP_ESZQ: _ClassVar[lbp]
LBP_ESZK: lbp
LBP_ESZL: lbp
LBP_ESZM: lbp
LBP_ESZN: lbp
LBP_ESZO: lbp
LBP_ESZP: lbp
LBP_ESZQ: lbp

class lbr(_message.Message):
    __slots__ = ("fpen", "fpeo", "fpep")
    FPEN_FIELD_NUMBER: _ClassVar[int]
    FPEO_FIELD_NUMBER: _ClassVar[int]
    FPEP_FIELD_NUMBER: _ClassVar[int]
    fpen: lbt
    fpeo: lbv
    fpep: lbx
    def __init__(self, fpen: _Optional[_Union[lbt, _Mapping]] = ..., fpeo: _Optional[_Union[lbv, _Mapping]] = ..., fpep: _Optional[_Union[lbx, _Mapping]] = ...) -> None: ...

class lbt(_message.Message):
    __slots__ = ("fpeu", "fpev", "fpew", "fpex", "fpey", "fpez", "fpfa", "fpfb")
    FPEU_FIELD_NUMBER: _ClassVar[int]
    FPEV_FIELD_NUMBER: _ClassVar[int]
    FPEW_FIELD_NUMBER: _ClassVar[int]
    FPEX_FIELD_NUMBER: _ClassVar[int]
    FPEY_FIELD_NUMBER: _ClassVar[int]
    FPEZ_FIELD_NUMBER: _ClassVar[int]
    FPFA_FIELD_NUMBER: _ClassVar[int]
    FPFB_FIELD_NUMBER: _ClassVar[int]
    fpeu: str
    fpev: lby
    fpew: lcc
    fpex: lcq
    fpey: ldf
    fpez: ldk
    fpfa: ldp
    fpfb: ldx
    def __init__(self, fpeu: _Optional[str] = ..., fpev: _Optional[_Union[lby, _Mapping]] = ..., fpew: _Optional[_Union[lcc, _Mapping]] = ..., fpex: _Optional[_Union[lcq, _Mapping]] = ..., fpey: _Optional[_Union[ldf, _Mapping]] = ..., fpez: _Optional[_Union[ldk, _Mapping]] = ..., fpfa: _Optional[_Union[ldp, _Mapping]] = ..., fpfb: _Optional[_Union[ldx, _Mapping]] = ...) -> None: ...

class lbv(_message.Message):
    __slots__ = ("fpfg", "fpfh", "fpfi", "fpfj", "fpfk", "fpfl", "fpfm")
    FPFG_FIELD_NUMBER: _ClassVar[int]
    FPFH_FIELD_NUMBER: _ClassVar[int]
    FPFI_FIELD_NUMBER: _ClassVar[int]
    FPFJ_FIELD_NUMBER: _ClassVar[int]
    FPFK_FIELD_NUMBER: _ClassVar[int]
    FPFL_FIELD_NUMBER: _ClassVar[int]
    FPFM_FIELD_NUMBER: _ClassVar[int]
    fpfg: str
    fpfh: lbz
    fpfi: lcp
    fpfj: lcv
    fpfk: ldh
    fpfl: ldw
    fpfm: lee
    def __init__(self, fpfg: _Optional[str] = ..., fpfh: _Optional[_Union[lbz, _Mapping]] = ..., fpfi: _Optional[_Union[lcp, _Mapping]] = ..., fpfj: _Optional[_Union[lcv, _Mapping]] = ..., fpfk: _Optional[_Union[ldh, _Mapping]] = ..., fpfl: _Optional[_Union[ldw, _Mapping]] = ..., fpfm: _Optional[_Union[lee, _Mapping]] = ...) -> None: ...

class lbx(_message.Message):
    __slots__ = ("fpfr",)
    FPFR_FIELD_NUMBER: _ClassVar[int]
    fpfr: lca
    def __init__(self, fpfr: _Optional[_Union[lca, _Mapping]] = ...) -> None: ...

class lby(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class lbz(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class lca(_message.Message):
    __slots__ = ("fpgc",)
    FPGC_FIELD_NUMBER: _ClassVar[int]
    fpgc: ldb
    def __init__(self, fpgc: _Optional[_Union[ldb, _Mapping]] = ...) -> None: ...

class lcc(_message.Message):
    __slots__ = ("fpgg", "fpgj", "fpgh", "fpgi")
    FPGG_FIELD_NUMBER: _ClassVar[int]
    FPGJ_FIELD_NUMBER: _ClassVar[int]
    FPGH_FIELD_NUMBER: _ClassVar[int]
    FPGI_FIELD_NUMBER: _ClassVar[int]
    fpgg: str
    fpgj: str
    fpgh: lcf
    fpgi: lcg
    def __init__(self, fpgg: _Optional[str] = ..., fpgj: _Optional[str] = ..., fpgh: _Optional[_Union[lcf, _Mapping]] = ..., fpgi: _Optional[_Union[lcg, _Mapping]] = ...) -> None: ...

class lcf(_message.Message):
    __slots__ = ("fpgt", "fpgu")
    class lcd(_message.Message):
        __slots__ = ("fpgo", "fpgp")
        FPGO_FIELD_NUMBER: _ClassVar[int]
        FPGP_FIELD_NUMBER: _ClassVar[int]
        fpgo: int
        fpgp: str
        def __init__(self, fpgo: _Optional[int] = ..., fpgp: _Optional[str] = ...) -> None: ...
    FPGT_FIELD_NUMBER: _ClassVar[int]
    FPGU_FIELD_NUMBER: _ClassVar[int]
    fpgt: str
    fpgu: lcf.lcd
    def __init__(self, fpgt: _Optional[str] = ..., fpgu: _Optional[_Union[lcf.lcd, _Mapping]] = ...) -> None: ...

class lcg(_message.Message):
    __slots__ = ("fpgy",)
    FPGY_FIELD_NUMBER: _ClassVar[int]
    fpgy: str
    def __init__(self, fpgy: _Optional[str] = ...) -> None: ...

class lcp(_message.Message):
    __slots__ = ("fpie", "fpif")
    class lck(_message.Message):
        __slots__ = ("fphj", "fphk", "fphl", "fphm", "fphn", "fpho", "fphp", "fphr", "fphs")
        class lci(_message.Message):
            __slots__ = ("fphc", "fphd", "fphe", "fphf")
            FPHC_FIELD_NUMBER: _ClassVar[int]
            FPHD_FIELD_NUMBER: _ClassVar[int]
            FPHE_FIELD_NUMBER: _ClassVar[int]
            FPHF_FIELD_NUMBER: _ClassVar[int]
            fphc: bool
            fphd: bool
            fphe: bool
            fphf: bool
            def __init__(self, fphc: bool = ..., fphd: bool = ..., fphe: bool = ..., fphf: bool = ...) -> None: ...
        FPHJ_FIELD_NUMBER: _ClassVar[int]
        FPHK_FIELD_NUMBER: _ClassVar[int]
        FPHL_FIELD_NUMBER: _ClassVar[int]
        FPHM_FIELD_NUMBER: _ClassVar[int]
        FPHN_FIELD_NUMBER: _ClassVar[int]
        FPHO_FIELD_NUMBER: _ClassVar[int]
        FPHP_FIELD_NUMBER: _ClassVar[int]
        FPHR_FIELD_NUMBER: _ClassVar[int]
        FPHS_FIELD_NUMBER: _ClassVar[int]
        fphj: int
        fphk: str
        fphl: str
        fphm: lcy
        fphn: str
        fpho: lcp.lck.lci
        fphp: int
        fphr: ldi
        fphs: lef
        def __init__(self, fphj: _Optional[int] = ..., fphk: _Optional[str] = ..., fphl: _Optional[str] = ..., fphm: _Optional[_Union[lcy, _Mapping]] = ..., fphn: _Optional[str] = ..., fpho: _Optional[_Union[lcp.lck.lci, _Mapping]] = ..., fphp: _Optional[int] = ..., fphr: _Optional[_Union[ldi, _Mapping]] = ..., fphs: _Optional[_Union[lef, _Mapping]] = ...) -> None: ...
    class lcn(_message.Message):
        __slots__ = ("fphw", "fphx", "fphz")
        class lcl(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            LCL_ETER: _ClassVar[lcp.lcn.lcl]
            LCL_ETES: _ClassVar[lcp.lcn.lcl]
            LCL_ETET: _ClassVar[lcp.lcn.lcl]
            LCL_ETEU: _ClassVar[lcp.lcn.lcl]
            LCL_ETEV: _ClassVar[lcp.lcn.lcl]
            LCL_ETEW: _ClassVar[lcp.lcn.lcl]
            LCL_ETEX: _ClassVar[lcp.lcn.lcl]
            LCL_ETEY: _ClassVar[lcp.lcn.lcl]
            LCL_ETEZ: _ClassVar[lcp.lcn.lcl]
            LCL_ETFA: _ClassVar[lcp.lcn.lcl]
            LCL_ETFB: _ClassVar[lcp.lcn.lcl]
            LCL_ETFC: _ClassVar[lcp.lcn.lcl]
            LCL_ETFD: _ClassVar[lcp.lcn.lcl]
            LCL_ETFE: _ClassVar[lcp.lcn.lcl]
        LCL_ETER: lcp.lcn.lcl
        LCL_ETES: lcp.lcn.lcl
        LCL_ETET: lcp.lcn.lcl
        LCL_ETEU: lcp.lcn.lcl
        LCL_ETEV: lcp.lcn.lcl
        LCL_ETEW: lcp.lcn.lcl
        LCL_ETEX: lcp.lcn.lcl
        LCL_ETEY: lcp.lcn.lcl
        LCL_ETEZ: lcp.lcn.lcl
        LCL_ETFA: lcp.lcn.lcl
        LCL_ETFB: lcp.lcn.lcl
        LCL_ETFC: lcp.lcn.lcl
        LCL_ETFD: lcp.lcn.lcl
        LCL_ETFE: lcp.lcn.lcl
        FPHW_FIELD_NUMBER: _ClassVar[int]
        FPHX_FIELD_NUMBER: _ClassVar[int]
        FPHZ_FIELD_NUMBER: _ClassVar[int]
        fphw: lcp.lcn.lcl
        fphx: str
        fphz: str
        def __init__(self, fphw: _Optional[_Union[lcp.lcn.lcl, str]] = ..., fphx: _Optional[str] = ..., fphz: _Optional[str] = ...) -> None: ...
    FPIE_FIELD_NUMBER: _ClassVar[int]
    FPIF_FIELD_NUMBER: _ClassVar[int]
    fpie: lcp.lck
    fpif: lcp.lcn
    def __init__(self, fpie: _Optional[_Union[lcp.lck, _Mapping]] = ..., fpif: _Optional[_Union[lcp.lcn, _Mapping]] = ...) -> None: ...

class lcq(_message.Message):
    __slots__ = ("fpik",)
    FPIK_FIELD_NUMBER: _ClassVar[int]
    fpik: int
    def __init__(self, fpik: _Optional[int] = ...) -> None: ...

class lcv(_message.Message):
    __slots__ = ("fpiu", "fpiv")
    class lcs(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LCS_ETGC: _ClassVar[lcv.lcs]
        LCS_ETGD: _ClassVar[lcv.lcs]
        LCS_ETGE: _ClassVar[lcv.lcs]
        LCS_ETGF: _ClassVar[lcv.lcs]
    LCS_ETGC: lcv.lcs
    LCS_ETGD: lcv.lcs
    LCS_ETGE: lcv.lcs
    LCS_ETGF: lcv.lcs
    class lct(_message.Message):
        __slots__ = ("fpio", "fpip", "fpiq")
        FPIO_FIELD_NUMBER: _ClassVar[int]
        FPIP_FIELD_NUMBER: _ClassVar[int]
        FPIQ_FIELD_NUMBER: _ClassVar[int]
        fpio: str
        fpip: str
        fpiq: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, fpio: _Optional[str] = ..., fpip: _Optional[str] = ..., fpiq: _Optional[_Iterable[int]] = ...) -> None: ...
    FPIU_FIELD_NUMBER: _ClassVar[int]
    FPIV_FIELD_NUMBER: _ClassVar[int]
    fpiu: lcv.lct
    fpiv: lcv.lcs
    def __init__(self, fpiu: _Optional[_Union[lcv.lct, _Mapping]] = ..., fpiv: _Optional[_Union[lcv.lcs, str]] = ...) -> None: ...

class lcy(_message.Message):
    __slots__ = ("fpjg", "fpjh", "fpji")
    class lcw(_message.Message):
        __slots__ = ("fpjb", "fpjc")
        FPJB_FIELD_NUMBER: _ClassVar[int]
        FPJC_FIELD_NUMBER: _ClassVar[int]
        fpjb: lbp
        fpjc: int
        def __init__(self, fpjb: _Optional[_Union[lbp, str]] = ..., fpjc: _Optional[int] = ...) -> None: ...
    FPJG_FIELD_NUMBER: _ClassVar[int]
    FPJH_FIELD_NUMBER: _ClassVar[int]
    FPJI_FIELD_NUMBER: _ClassVar[int]
    fpjg: _containers.RepeatedCompositeFieldContainer[ldb]
    fpjh: _containers.RepeatedCompositeFieldContainer[lcy.lcw]
    fpji: bool
    def __init__(self, fpjg: _Optional[_Iterable[_Union[ldb, _Mapping]]] = ..., fpjh: _Optional[_Iterable[_Union[lcy.lcw, _Mapping]]] = ..., fpji: bool = ...) -> None: ...

class ldb(_message.Message):
    __slots__ = ("fpjm", "fpjn", "fpjo")
    class lcz(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LCZ_ETHL: _ClassVar[ldb.lcz]
        LCZ_ETHM: _ClassVar[ldb.lcz]
        LCZ_ETHN: _ClassVar[ldb.lcz]
        LCZ_ETHO: _ClassVar[ldb.lcz]
    LCZ_ETHL: ldb.lcz
    LCZ_ETHM: ldb.lcz
    LCZ_ETHN: ldb.lcz
    LCZ_ETHO: ldb.lcz
    FPJM_FIELD_NUMBER: _ClassVar[int]
    FPJN_FIELD_NUMBER: _ClassVar[int]
    FPJO_FIELD_NUMBER: _ClassVar[int]
    fpjm: lde
    fpjn: ldb.lcz
    fpjo: _containers.RepeatedCompositeFieldContainer[ldo]
    def __init__(self, fpjm: _Optional[_Union[lde, _Mapping]] = ..., fpjn: _Optional[_Union[ldb.lcz, str]] = ..., fpjo: _Optional[_Iterable[_Union[ldo, _Mapping]]] = ...) -> None: ...

class lde(_message.Message):
    __slots__ = ("fpjs", "fpjt", "fpju")
    class ldc(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LDC_ETHY: _ClassVar[lde.ldc]
        LDC_ETHZ: _ClassVar[lde.ldc]
    LDC_ETHY: lde.ldc
    LDC_ETHZ: lde.ldc
    FPJS_FIELD_NUMBER: _ClassVar[int]
    FPJT_FIELD_NUMBER: _ClassVar[int]
    FPJU_FIELD_NUMBER: _ClassVar[int]
    fpjs: int
    fpjt: lde.ldc
    fpju: lbp
    def __init__(self, fpjs: _Optional[int] = ..., fpjt: _Optional[_Union[lde.ldc, str]] = ..., fpju: _Optional[_Union[lbp, str]] = ...) -> None: ...

class ldf(_message.Message):
    __slots__ = ("fpjy",)
    FPJY_FIELD_NUMBER: _ClassVar[int]
    fpjy: int
    def __init__(self, fpjy: _Optional[int] = ...) -> None: ...

class ldh(_message.Message):
    __slots__ = ("fpkc", "fpkd")
    FPKC_FIELD_NUMBER: _ClassVar[int]
    FPKD_FIELD_NUMBER: _ClassVar[int]
    fpkc: ldi
    fpkd: ldj
    def __init__(self, fpkc: _Optional[_Union[ldi, _Mapping]] = ..., fpkd: _Optional[_Union[ldj, _Mapping]] = ...) -> None: ...

class ldi(_message.Message):
    __slots__ = ("fpki", "fpkj", "fpkk", "fpkl", "fpkm")
    FPKI_FIELD_NUMBER: _ClassVar[int]
    FPKJ_FIELD_NUMBER: _ClassVar[int]
    FPKK_FIELD_NUMBER: _ClassVar[int]
    FPKL_FIELD_NUMBER: _ClassVar[int]
    FPKM_FIELD_NUMBER: _ClassVar[int]
    fpki: bool
    fpkj: int
    fpkk: str
    fpkl: str
    fpkm: lcy
    def __init__(self, fpki: bool = ..., fpkj: _Optional[int] = ..., fpkk: _Optional[str] = ..., fpkl: _Optional[str] = ..., fpkm: _Optional[_Union[lcy, _Mapping]] = ...) -> None: ...

class ldj(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ldk(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ldo(_message.Message):
    __slots__ = ("fpkw", "fpkx", "fpky", "fpkz", "fpla")
    class ldm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LDM_ETJN: _ClassVar[ldo.ldm]
        LDM_ETJO: _ClassVar[ldo.ldm]
        LDM_ETJP: _ClassVar[ldo.ldm]
        LDM_ETJQ: _ClassVar[ldo.ldm]
        LDM_ETJR: _ClassVar[ldo.ldm]
        LDM_ETJS: _ClassVar[ldo.ldm]
        LDM_ETJT: _ClassVar[ldo.ldm]
        LDM_ETJU: _ClassVar[ldo.ldm]
        LDM_ETJV: _ClassVar[ldo.ldm]
        LDM_ETJW: _ClassVar[ldo.ldm]
        LDM_ETJX: _ClassVar[ldo.ldm]
        LDM_ETJY: _ClassVar[ldo.ldm]
        LDM_ETJZ: _ClassVar[ldo.ldm]
        LDM_ETKA: _ClassVar[ldo.ldm]
        LDM_ETKB: _ClassVar[ldo.ldm]
        LDM_ETKC: _ClassVar[ldo.ldm]
        LDM_ETKD: _ClassVar[ldo.ldm]
        LDM_ETKE: _ClassVar[ldo.ldm]
        LDM_ETKF: _ClassVar[ldo.ldm]
    LDM_ETJN: ldo.ldm
    LDM_ETJO: ldo.ldm
    LDM_ETJP: ldo.ldm
    LDM_ETJQ: ldo.ldm
    LDM_ETJR: ldo.ldm
    LDM_ETJS: ldo.ldm
    LDM_ETJT: ldo.ldm
    LDM_ETJU: ldo.ldm
    LDM_ETJV: ldo.ldm
    LDM_ETJW: ldo.ldm
    LDM_ETJX: ldo.ldm
    LDM_ETJY: ldo.ldm
    LDM_ETJZ: ldo.ldm
    LDM_ETKA: ldo.ldm
    LDM_ETKB: ldo.ldm
    LDM_ETKC: ldo.ldm
    LDM_ETKD: ldo.ldm
    LDM_ETKE: ldo.ldm
    LDM_ETKF: ldo.ldm
    class ldl(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LDL_ETJL: _ClassVar[ldo.ldl]
        LDL_ETJM: _ClassVar[ldo.ldl]
    LDL_ETJL: ldo.ldl
    LDL_ETJM: ldo.ldl
    FPKW_FIELD_NUMBER: _ClassVar[int]
    FPKX_FIELD_NUMBER: _ClassVar[int]
    FPKY_FIELD_NUMBER: _ClassVar[int]
    FPKZ_FIELD_NUMBER: _ClassVar[int]
    FPLA_FIELD_NUMBER: _ClassVar[int]
    fpkw: str
    fpkx: ldo.ldm
    fpky: ldo.ldl
    fpkz: int
    fpla: str
    def __init__(self, fpkw: _Optional[str] = ..., fpkx: _Optional[_Union[ldo.ldm, str]] = ..., fpky: _Optional[_Union[ldo.ldl, str]] = ..., fpkz: _Optional[int] = ..., fpla: _Optional[str] = ...) -> None: ...

class ldp(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ldw(_message.Message):
    __slots__ = ("fplr", "fpls")
    class ldr(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LDR_ETKX: _ClassVar[ldw.ldr]
        LDR_ETKY: _ClassVar[ldw.ldr]
    LDR_ETKX: ldw.ldr
    LDR_ETKY: ldw.ldr
    class ldu(_message.Message):
        __slots__ = ("fpln",)
        class lds(_message.Message):
            __slots__ = ("fplh", "fpli", "fplj")
            FPLH_FIELD_NUMBER: _ClassVar[int]
            FPLI_FIELD_NUMBER: _ClassVar[int]
            FPLJ_FIELD_NUMBER: _ClassVar[int]
            fplh: str
            fpli: str
            fplj: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, fplh: _Optional[str] = ..., fpli: _Optional[str] = ..., fplj: _Optional[_Iterable[int]] = ...) -> None: ...
        FPLN_FIELD_NUMBER: _ClassVar[int]
        fpln: _containers.RepeatedCompositeFieldContainer[ldw.ldu.lds]
        def __init__(self, fpln: _Optional[_Iterable[_Union[ldw.ldu.lds, _Mapping]]] = ...) -> None: ...
    FPLR_FIELD_NUMBER: _ClassVar[int]
    FPLS_FIELD_NUMBER: _ClassVar[int]
    fplr: ldw.ldu
    fpls: ldw.ldr
    def __init__(self, fplr: _Optional[_Union[ldw.ldu, _Mapping]] = ..., fpls: _Optional[_Union[ldw.ldr, str]] = ...) -> None: ...

class ldx(_message.Message):
    __slots__ = ("fply", "fplz")
    FPLY_FIELD_NUMBER: _ClassVar[int]
    FPLZ_FIELD_NUMBER: _ClassVar[int]
    fply: str
    fplz: str
    def __init__(self, fply: _Optional[str] = ..., fplz: _Optional[str] = ...) -> None: ...

class lee(_message.Message):
    __slots__ = ("fpml", "fpmm")
    class ldz(_message.Message):
        __slots__ = ("fpmd",)
        FPMD_FIELD_NUMBER: _ClassVar[int]
        fpmd: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, fpmd: _Optional[_Iterable[int]] = ...) -> None: ...
    class lec(_message.Message):
        __slots__ = ("fpmh",)
        class lea(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            LEA_ETMH: _ClassVar[lee.lec.lea]
            LEA_ETMI: _ClassVar[lee.lec.lea]
            LEA_ETMJ: _ClassVar[lee.lec.lea]
            LEA_ETMK: _ClassVar[lee.lec.lea]
        LEA_ETMH: lee.lec.lea
        LEA_ETMI: lee.lec.lea
        LEA_ETMJ: lee.lec.lea
        LEA_ETMK: lee.lec.lea
        FPMH_FIELD_NUMBER: _ClassVar[int]
        fpmh: lee.lec.lea
        def __init__(self, fpmh: _Optional[_Union[lee.lec.lea, str]] = ...) -> None: ...
    FPML_FIELD_NUMBER: _ClassVar[int]
    FPMM_FIELD_NUMBER: _ClassVar[int]
    fpml: lee.ldz
    fpmm: lee.lec
    def __init__(self, fpml: _Optional[_Union[lee.ldz, _Mapping]] = ..., fpmm: _Optional[_Union[lee.lec, _Mapping]] = ...) -> None: ...

class lef(_message.Message):
    __slots__ = ("fpmr", "fpms", "fpmt")
    FPMR_FIELD_NUMBER: _ClassVar[int]
    FPMS_FIELD_NUMBER: _ClassVar[int]
    FPMT_FIELD_NUMBER: _ClassVar[int]
    fpmr: str
    fpms: str
    fpmt: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, fpmr: _Optional[str] = ..., fpms: _Optional[str] = ..., fpmt: _Optional[_Iterable[int]] = ...) -> None: ...
