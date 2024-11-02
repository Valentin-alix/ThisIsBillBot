from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class kmq(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KMQ_ELEX: _ClassVar[kmq]
    KMQ_ELEY: _ClassVar[kmq]
    KMQ_ELEZ: _ClassVar[kmq]
    KMQ_ELFA: _ClassVar[kmq]
    KMQ_ELFB: _ClassVar[kmq]
    KMQ_ELFC: _ClassVar[kmq]
    KMQ_ELFD: _ClassVar[kmq]
KMQ_ELEX: kmq
KMQ_ELEY: kmq
KMQ_ELEZ: kmq
KMQ_ELFA: kmq
KMQ_ELFB: kmq
KMQ_ELFC: kmq
KMQ_ELFD: kmq

class kms(_message.Message):
    __slots__ = ("ffvj", "ffvk", "ffvl")
    FFVJ_FIELD_NUMBER: _ClassVar[int]
    FFVK_FIELD_NUMBER: _ClassVar[int]
    FFVL_FIELD_NUMBER: _ClassVar[int]
    ffvj: kmu
    ffvk: kmw
    ffvl: kmy
    def __init__(self, ffvj: _Optional[_Union[kmu, _Mapping]] = ..., ffvk: _Optional[_Union[kmw, _Mapping]] = ..., ffvl: _Optional[_Union[kmy, _Mapping]] = ...) -> None: ...

class kmu(_message.Message):
    __slots__ = ("ffvq", "ffvr", "ffvs", "ffvt", "ffvu", "ffvv", "ffvw", "ffvx")
    FFVQ_FIELD_NUMBER: _ClassVar[int]
    FFVR_FIELD_NUMBER: _ClassVar[int]
    FFVS_FIELD_NUMBER: _ClassVar[int]
    FFVT_FIELD_NUMBER: _ClassVar[int]
    FFVU_FIELD_NUMBER: _ClassVar[int]
    FFVV_FIELD_NUMBER: _ClassVar[int]
    FFVW_FIELD_NUMBER: _ClassVar[int]
    FFVX_FIELD_NUMBER: _ClassVar[int]
    ffvq: str
    ffvr: kmz
    ffvs: knd
    ffvt: knr
    ffvu: kog
    ffvv: kol
    ffvw: koq
    ffvx: koy
    def __init__(self, ffvq: _Optional[str] = ..., ffvr: _Optional[_Union[kmz, _Mapping]] = ..., ffvs: _Optional[_Union[knd, _Mapping]] = ..., ffvt: _Optional[_Union[knr, _Mapping]] = ..., ffvu: _Optional[_Union[kog, _Mapping]] = ..., ffvv: _Optional[_Union[kol, _Mapping]] = ..., ffvw: _Optional[_Union[koq, _Mapping]] = ..., ffvx: _Optional[_Union[koy, _Mapping]] = ...) -> None: ...

class kmw(_message.Message):
    __slots__ = ("ffwc", "ffwd", "ffwe", "ffwf", "ffwg", "ffwh", "ffwi")
    FFWC_FIELD_NUMBER: _ClassVar[int]
    FFWD_FIELD_NUMBER: _ClassVar[int]
    FFWE_FIELD_NUMBER: _ClassVar[int]
    FFWF_FIELD_NUMBER: _ClassVar[int]
    FFWG_FIELD_NUMBER: _ClassVar[int]
    FFWH_FIELD_NUMBER: _ClassVar[int]
    FFWI_FIELD_NUMBER: _ClassVar[int]
    ffwc: str
    ffwd: kna
    ffwe: knq
    ffwf: knw
    ffwg: koi
    ffwh: kox
    ffwi: kpf
    def __init__(self, ffwc: _Optional[str] = ..., ffwd: _Optional[_Union[kna, _Mapping]] = ..., ffwe: _Optional[_Union[knq, _Mapping]] = ..., ffwf: _Optional[_Union[knw, _Mapping]] = ..., ffwg: _Optional[_Union[koi, _Mapping]] = ..., ffwh: _Optional[_Union[kox, _Mapping]] = ..., ffwi: _Optional[_Union[kpf, _Mapping]] = ...) -> None: ...

class kmy(_message.Message):
    __slots__ = ("ffwn",)
    FFWN_FIELD_NUMBER: _ClassVar[int]
    ffwn: knb
    def __init__(self, ffwn: _Optional[_Union[knb, _Mapping]] = ...) -> None: ...

class kmz(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class kna(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class knb(_message.Message):
    __slots__ = ("ffwy",)
    FFWY_FIELD_NUMBER: _ClassVar[int]
    ffwy: koc
    def __init__(self, ffwy: _Optional[_Union[koc, _Mapping]] = ...) -> None: ...

class knd(_message.Message):
    __slots__ = ("ffxc", "ffxf", "ffxd", "ffxe")
    FFXC_FIELD_NUMBER: _ClassVar[int]
    FFXF_FIELD_NUMBER: _ClassVar[int]
    FFXD_FIELD_NUMBER: _ClassVar[int]
    FFXE_FIELD_NUMBER: _ClassVar[int]
    ffxc: str
    ffxf: str
    ffxd: kng
    ffxe: knh
    def __init__(self, ffxc: _Optional[str] = ..., ffxf: _Optional[str] = ..., ffxd: _Optional[_Union[kng, _Mapping]] = ..., ffxe: _Optional[_Union[knh, _Mapping]] = ...) -> None: ...

class kng(_message.Message):
    __slots__ = ("ffxp", "ffxq")
    class kne(_message.Message):
        __slots__ = ("ffxk", "ffxl")
        FFXK_FIELD_NUMBER: _ClassVar[int]
        FFXL_FIELD_NUMBER: _ClassVar[int]
        ffxk: int
        ffxl: str
        def __init__(self, ffxk: _Optional[int] = ..., ffxl: _Optional[str] = ...) -> None: ...
    FFXP_FIELD_NUMBER: _ClassVar[int]
    FFXQ_FIELD_NUMBER: _ClassVar[int]
    ffxp: str
    ffxq: kng.kne
    def __init__(self, ffxp: _Optional[str] = ..., ffxq: _Optional[_Union[kng.kne, _Mapping]] = ...) -> None: ...

class knh(_message.Message):
    __slots__ = ("ffxu",)
    FFXU_FIELD_NUMBER: _ClassVar[int]
    ffxu: str
    def __init__(self, ffxu: _Optional[str] = ...) -> None: ...

class knq(_message.Message):
    __slots__ = ("ffzd", "ffze")
    class knl(_message.Message):
        __slots__ = ("ffyi", "ffyj", "ffyk", "ffyl", "ffym", "ffyn", "ffyo", "ffyq", "ffyr")
        class knj(_message.Message):
            __slots__ = ("ffxy", "ffxz", "ffya", "ffyb", "ffyc", "ffyd", "ffye")
            FFXY_FIELD_NUMBER: _ClassVar[int]
            FFXZ_FIELD_NUMBER: _ClassVar[int]
            FFYA_FIELD_NUMBER: _ClassVar[int]
            FFYB_FIELD_NUMBER: _ClassVar[int]
            FFYC_FIELD_NUMBER: _ClassVar[int]
            FFYD_FIELD_NUMBER: _ClassVar[int]
            FFYE_FIELD_NUMBER: _ClassVar[int]
            ffxy: bool
            ffxz: bool
            ffya: bool
            ffyb: bool
            ffyc: bool
            ffyd: bool
            ffye: bool
            def __init__(self, ffxy: bool = ..., ffxz: bool = ..., ffya: bool = ..., ffyb: bool = ..., ffyc: bool = ..., ffyd: bool = ..., ffye: bool = ...) -> None: ...
        FFYI_FIELD_NUMBER: _ClassVar[int]
        FFYJ_FIELD_NUMBER: _ClassVar[int]
        FFYK_FIELD_NUMBER: _ClassVar[int]
        FFYL_FIELD_NUMBER: _ClassVar[int]
        FFYM_FIELD_NUMBER: _ClassVar[int]
        FFYN_FIELD_NUMBER: _ClassVar[int]
        FFYO_FIELD_NUMBER: _ClassVar[int]
        FFYQ_FIELD_NUMBER: _ClassVar[int]
        FFYR_FIELD_NUMBER: _ClassVar[int]
        ffyi: int
        ffyj: str
        ffyk: str
        ffyl: knz
        ffym: str
        ffyn: knq.knl.knj
        ffyo: int
        ffyq: koj
        ffyr: kpg
        def __init__(self, ffyi: _Optional[int] = ..., ffyj: _Optional[str] = ..., ffyk: _Optional[str] = ..., ffyl: _Optional[_Union[knz, _Mapping]] = ..., ffym: _Optional[str] = ..., ffyn: _Optional[_Union[knq.knl.knj, _Mapping]] = ..., ffyo: _Optional[int] = ..., ffyq: _Optional[_Union[koj, _Mapping]] = ..., ffyr: _Optional[_Union[kpg, _Mapping]] = ...) -> None: ...
    class kno(_message.Message):
        __slots__ = ("ffyv", "ffyw", "ffyy")
        class knm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            KNM_ELKK: _ClassVar[knq.kno.knm]
            KNM_ELKL: _ClassVar[knq.kno.knm]
            KNM_ELKM: _ClassVar[knq.kno.knm]
            KNM_ELKN: _ClassVar[knq.kno.knm]
            KNM_ELKO: _ClassVar[knq.kno.knm]
            KNM_ELKP: _ClassVar[knq.kno.knm]
            KNM_ELKQ: _ClassVar[knq.kno.knm]
            KNM_ELKR: _ClassVar[knq.kno.knm]
            KNM_ELKS: _ClassVar[knq.kno.knm]
            KNM_ELKT: _ClassVar[knq.kno.knm]
            KNM_ELKU: _ClassVar[knq.kno.knm]
            KNM_ELKV: _ClassVar[knq.kno.knm]
            KNM_ELKW: _ClassVar[knq.kno.knm]
            KNM_ELKX: _ClassVar[knq.kno.knm]
        KNM_ELKK: knq.kno.knm
        KNM_ELKL: knq.kno.knm
        KNM_ELKM: knq.kno.knm
        KNM_ELKN: knq.kno.knm
        KNM_ELKO: knq.kno.knm
        KNM_ELKP: knq.kno.knm
        KNM_ELKQ: knq.kno.knm
        KNM_ELKR: knq.kno.knm
        KNM_ELKS: knq.kno.knm
        KNM_ELKT: knq.kno.knm
        KNM_ELKU: knq.kno.knm
        KNM_ELKV: knq.kno.knm
        KNM_ELKW: knq.kno.knm
        KNM_ELKX: knq.kno.knm
        FFYV_FIELD_NUMBER: _ClassVar[int]
        FFYW_FIELD_NUMBER: _ClassVar[int]
        FFYY_FIELD_NUMBER: _ClassVar[int]
        ffyv: knq.kno.knm
        ffyw: str
        ffyy: str
        def __init__(self, ffyv: _Optional[_Union[knq.kno.knm, str]] = ..., ffyw: _Optional[str] = ..., ffyy: _Optional[str] = ...) -> None: ...
    FFZD_FIELD_NUMBER: _ClassVar[int]
    FFZE_FIELD_NUMBER: _ClassVar[int]
    ffzd: knq.knl
    ffze: knq.kno
    def __init__(self, ffzd: _Optional[_Union[knq.knl, _Mapping]] = ..., ffze: _Optional[_Union[knq.kno, _Mapping]] = ...) -> None: ...

class knr(_message.Message):
    __slots__ = ("ffzj",)
    FFZJ_FIELD_NUMBER: _ClassVar[int]
    ffzj: int
    def __init__(self, ffzj: _Optional[int] = ...) -> None: ...

class knw(_message.Message):
    __slots__ = ("ffzt", "ffzu")
    class knt(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KNT_ELLV: _ClassVar[knw.knt]
        KNT_ELLW: _ClassVar[knw.knt]
        KNT_ELLX: _ClassVar[knw.knt]
        KNT_ELLY: _ClassVar[knw.knt]
    KNT_ELLV: knw.knt
    KNT_ELLW: knw.knt
    KNT_ELLX: knw.knt
    KNT_ELLY: knw.knt
    class knu(_message.Message):
        __slots__ = ("ffzn", "ffzo", "ffzp")
        FFZN_FIELD_NUMBER: _ClassVar[int]
        FFZO_FIELD_NUMBER: _ClassVar[int]
        FFZP_FIELD_NUMBER: _ClassVar[int]
        ffzn: str
        ffzo: str
        ffzp: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, ffzn: _Optional[str] = ..., ffzo: _Optional[str] = ..., ffzp: _Optional[_Iterable[int]] = ...) -> None: ...
    FFZT_FIELD_NUMBER: _ClassVar[int]
    FFZU_FIELD_NUMBER: _ClassVar[int]
    ffzt: knw.knu
    ffzu: knw.knt
    def __init__(self, ffzt: _Optional[_Union[knw.knu, _Mapping]] = ..., ffzu: _Optional[_Union[knw.knt, str]] = ...) -> None: ...

class knz(_message.Message):
    __slots__ = ("fgaf", "fgag", "fgah")
    class knx(_message.Message):
        __slots__ = ("fgaa", "fgab")
        FGAA_FIELD_NUMBER: _ClassVar[int]
        FGAB_FIELD_NUMBER: _ClassVar[int]
        fgaa: kmq
        fgab: int
        def __init__(self, fgaa: _Optional[_Union[kmq, str]] = ..., fgab: _Optional[int] = ...) -> None: ...
    FGAF_FIELD_NUMBER: _ClassVar[int]
    FGAG_FIELD_NUMBER: _ClassVar[int]
    FGAH_FIELD_NUMBER: _ClassVar[int]
    fgaf: _containers.RepeatedCompositeFieldContainer[koc]
    fgag: _containers.RepeatedCompositeFieldContainer[knz.knx]
    fgah: bool
    def __init__(self, fgaf: _Optional[_Iterable[_Union[koc, _Mapping]]] = ..., fgag: _Optional[_Iterable[_Union[knz.knx, _Mapping]]] = ..., fgah: bool = ...) -> None: ...

class koc(_message.Message):
    __slots__ = ("fgal", "fgam", "fgan")
    class koa(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KOA_ELNE: _ClassVar[koc.koa]
        KOA_ELNF: _ClassVar[koc.koa]
        KOA_ELNG: _ClassVar[koc.koa]
        KOA_ELNH: _ClassVar[koc.koa]
    KOA_ELNE: koc.koa
    KOA_ELNF: koc.koa
    KOA_ELNG: koc.koa
    KOA_ELNH: koc.koa
    FGAL_FIELD_NUMBER: _ClassVar[int]
    FGAM_FIELD_NUMBER: _ClassVar[int]
    FGAN_FIELD_NUMBER: _ClassVar[int]
    fgal: kof
    fgam: koc.koa
    fgan: _containers.RepeatedCompositeFieldContainer[kop]
    def __init__(self, fgal: _Optional[_Union[kof, _Mapping]] = ..., fgam: _Optional[_Union[koc.koa, str]] = ..., fgan: _Optional[_Iterable[_Union[kop, _Mapping]]] = ...) -> None: ...

class kof(_message.Message):
    __slots__ = ("fgar", "fgas", "fgat")
    class kod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KOD_ELNR: _ClassVar[kof.kod]
        KOD_ELNS: _ClassVar[kof.kod]
    KOD_ELNR: kof.kod
    KOD_ELNS: kof.kod
    FGAR_FIELD_NUMBER: _ClassVar[int]
    FGAS_FIELD_NUMBER: _ClassVar[int]
    FGAT_FIELD_NUMBER: _ClassVar[int]
    fgar: int
    fgas: kof.kod
    fgat: kmq
    def __init__(self, fgar: _Optional[int] = ..., fgas: _Optional[_Union[kof.kod, str]] = ..., fgat: _Optional[_Union[kmq, str]] = ...) -> None: ...

class kog(_message.Message):
    __slots__ = ("fgax",)
    FGAX_FIELD_NUMBER: _ClassVar[int]
    fgax: int
    def __init__(self, fgax: _Optional[int] = ...) -> None: ...

class koi(_message.Message):
    __slots__ = ("fgbb", "fgbc")
    FGBB_FIELD_NUMBER: _ClassVar[int]
    FGBC_FIELD_NUMBER: _ClassVar[int]
    fgbb: koj
    fgbc: kok
    def __init__(self, fgbb: _Optional[_Union[koj, _Mapping]] = ..., fgbc: _Optional[_Union[kok, _Mapping]] = ...) -> None: ...

class koj(_message.Message):
    __slots__ = ("fgbh", "fgbi", "fgbj", "fgbk", "fgbl")
    FGBH_FIELD_NUMBER: _ClassVar[int]
    FGBI_FIELD_NUMBER: _ClassVar[int]
    FGBJ_FIELD_NUMBER: _ClassVar[int]
    FGBK_FIELD_NUMBER: _ClassVar[int]
    FGBL_FIELD_NUMBER: _ClassVar[int]
    fgbh: bool
    fgbi: int
    fgbj: str
    fgbk: str
    fgbl: knz
    def __init__(self, fgbh: bool = ..., fgbi: _Optional[int] = ..., fgbj: _Optional[str] = ..., fgbk: _Optional[str] = ..., fgbl: _Optional[_Union[knz, _Mapping]] = ...) -> None: ...

class kok(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class kol(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class kop(_message.Message):
    __slots__ = ("fgbv", "fgbw", "fgbx", "fgby", "fgbz")
    class kon(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KON_ELPG: _ClassVar[kop.kon]
        KON_ELPH: _ClassVar[kop.kon]
        KON_ELPI: _ClassVar[kop.kon]
        KON_ELPJ: _ClassVar[kop.kon]
        KON_ELPK: _ClassVar[kop.kon]
        KON_ELPL: _ClassVar[kop.kon]
        KON_ELPM: _ClassVar[kop.kon]
        KON_ELPN: _ClassVar[kop.kon]
        KON_ELPO: _ClassVar[kop.kon]
        KON_ELPP: _ClassVar[kop.kon]
        KON_ELPQ: _ClassVar[kop.kon]
        KON_ELPR: _ClassVar[kop.kon]
        KON_ELPS: _ClassVar[kop.kon]
        KON_ELPT: _ClassVar[kop.kon]
        KON_ELPU: _ClassVar[kop.kon]
        KON_ELPV: _ClassVar[kop.kon]
        KON_ELPW: _ClassVar[kop.kon]
        KON_ELPX: _ClassVar[kop.kon]
        KON_ELPY: _ClassVar[kop.kon]
    KON_ELPG: kop.kon
    KON_ELPH: kop.kon
    KON_ELPI: kop.kon
    KON_ELPJ: kop.kon
    KON_ELPK: kop.kon
    KON_ELPL: kop.kon
    KON_ELPM: kop.kon
    KON_ELPN: kop.kon
    KON_ELPO: kop.kon
    KON_ELPP: kop.kon
    KON_ELPQ: kop.kon
    KON_ELPR: kop.kon
    KON_ELPS: kop.kon
    KON_ELPT: kop.kon
    KON_ELPU: kop.kon
    KON_ELPV: kop.kon
    KON_ELPW: kop.kon
    KON_ELPX: kop.kon
    KON_ELPY: kop.kon
    class kom(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KOM_ELPE: _ClassVar[kop.kom]
        KOM_ELPF: _ClassVar[kop.kom]
    KOM_ELPE: kop.kom
    KOM_ELPF: kop.kom
    FGBV_FIELD_NUMBER: _ClassVar[int]
    FGBW_FIELD_NUMBER: _ClassVar[int]
    FGBX_FIELD_NUMBER: _ClassVar[int]
    FGBY_FIELD_NUMBER: _ClassVar[int]
    FGBZ_FIELD_NUMBER: _ClassVar[int]
    fgbv: str
    fgbw: kop.kon
    fgbx: kop.kom
    fgby: int
    fgbz: str
    def __init__(self, fgbv: _Optional[str] = ..., fgbw: _Optional[_Union[kop.kon, str]] = ..., fgbx: _Optional[_Union[kop.kom, str]] = ..., fgby: _Optional[int] = ..., fgbz: _Optional[str] = ...) -> None: ...

class koq(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class kox(_message.Message):
    __slots__ = ("fgcq", "fgcr")
    class kos(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KOS_ELQQ: _ClassVar[kox.kos]
        KOS_ELQR: _ClassVar[kox.kos]
    KOS_ELQQ: kox.kos
    KOS_ELQR: kox.kos
    class kov(_message.Message):
        __slots__ = ("fgcm",)
        class kot(_message.Message):
            __slots__ = ("fgcg", "fgch", "fgci")
            FGCG_FIELD_NUMBER: _ClassVar[int]
            FGCH_FIELD_NUMBER: _ClassVar[int]
            FGCI_FIELD_NUMBER: _ClassVar[int]
            fgcg: str
            fgch: str
            fgci: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, fgcg: _Optional[str] = ..., fgch: _Optional[str] = ..., fgci: _Optional[_Iterable[int]] = ...) -> None: ...
        FGCM_FIELD_NUMBER: _ClassVar[int]
        fgcm: _containers.RepeatedCompositeFieldContainer[kox.kov.kot]
        def __init__(self, fgcm: _Optional[_Iterable[_Union[kox.kov.kot, _Mapping]]] = ...) -> None: ...
    FGCQ_FIELD_NUMBER: _ClassVar[int]
    FGCR_FIELD_NUMBER: _ClassVar[int]
    fgcq: kox.kov
    fgcr: kox.kos
    def __init__(self, fgcq: _Optional[_Union[kox.kov, _Mapping]] = ..., fgcr: _Optional[_Union[kox.kos, str]] = ...) -> None: ...

class koy(_message.Message):
    __slots__ = ("fgcx", "fgcy")
    FGCX_FIELD_NUMBER: _ClassVar[int]
    FGCY_FIELD_NUMBER: _ClassVar[int]
    fgcx: str
    fgcy: str
    def __init__(self, fgcx: _Optional[str] = ..., fgcy: _Optional[str] = ...) -> None: ...

class kpf(_message.Message):
    __slots__ = ("fgdk", "fgdl")
    class kpa(_message.Message):
        __slots__ = ("fgdc",)
        FGDC_FIELD_NUMBER: _ClassVar[int]
        fgdc: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, fgdc: _Optional[_Iterable[int]] = ...) -> None: ...
    class kpd(_message.Message):
        __slots__ = ("fgdg",)
        class kpb(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            KPB_ELSA: _ClassVar[kpf.kpd.kpb]
            KPB_ELSB: _ClassVar[kpf.kpd.kpb]
            KPB_ELSC: _ClassVar[kpf.kpd.kpb]
            KPB_ELSD: _ClassVar[kpf.kpd.kpb]
        KPB_ELSA: kpf.kpd.kpb
        KPB_ELSB: kpf.kpd.kpb
        KPB_ELSC: kpf.kpd.kpb
        KPB_ELSD: kpf.kpd.kpb
        FGDG_FIELD_NUMBER: _ClassVar[int]
        fgdg: kpf.kpd.kpb
        def __init__(self, fgdg: _Optional[_Union[kpf.kpd.kpb, str]] = ...) -> None: ...
    FGDK_FIELD_NUMBER: _ClassVar[int]
    FGDL_FIELD_NUMBER: _ClassVar[int]
    fgdk: kpf.kpa
    fgdl: kpf.kpd
    def __init__(self, fgdk: _Optional[_Union[kpf.kpa, _Mapping]] = ..., fgdl: _Optional[_Union[kpf.kpd, _Mapping]] = ...) -> None: ...

class kpg(_message.Message):
    __slots__ = ("fgdq", "fgdr", "fgds")
    FGDQ_FIELD_NUMBER: _ClassVar[int]
    FGDR_FIELD_NUMBER: _ClassVar[int]
    FGDS_FIELD_NUMBER: _ClassVar[int]
    fgdq: str
    fgdr: str
    fgds: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, fgdq: _Optional[str] = ..., fgdr: _Optional[str] = ..., fgds: _Optional[_Iterable[int]] = ...) -> None: ...
