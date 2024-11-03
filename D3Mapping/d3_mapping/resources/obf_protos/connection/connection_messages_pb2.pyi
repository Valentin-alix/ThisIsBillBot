from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class krv(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KRV_EPNH: _ClassVar[krv]
    KRV_EPNI: _ClassVar[krv]
    KRV_EPNJ: _ClassVar[krv]
    KRV_EPNK: _ClassVar[krv]
    KRV_EPNL: _ClassVar[krv]
    KRV_EPNM: _ClassVar[krv]
    KRV_EPNN: _ClassVar[krv]
KRV_EPNH: krv
KRV_EPNI: krv
KRV_EPNJ: krv
KRV_EPNK: krv
KRV_EPNL: krv
KRV_EPNM: krv
KRV_EPNN: krv

class krx(_message.Message):
    __slots__ = ("fkxs", "fkxt", "fkxu")
    FKXS_FIELD_NUMBER: _ClassVar[int]
    FKXT_FIELD_NUMBER: _ClassVar[int]
    FKXU_FIELD_NUMBER: _ClassVar[int]
    fkxs: krz
    fkxt: ksb
    fkxu: ksd
    def __init__(self, fkxs: _Optional[_Union[krz, _Mapping]] = ..., fkxt: _Optional[_Union[ksb, _Mapping]] = ..., fkxu: _Optional[_Union[ksd, _Mapping]] = ...) -> None: ...

class krz(_message.Message):
    __slots__ = ("fkxz", "fkya", "fkyb", "fkyc", "fkyd", "fkye", "fkyf", "fkyg")
    FKXZ_FIELD_NUMBER: _ClassVar[int]
    FKYA_FIELD_NUMBER: _ClassVar[int]
    FKYB_FIELD_NUMBER: _ClassVar[int]
    FKYC_FIELD_NUMBER: _ClassVar[int]
    FKYD_FIELD_NUMBER: _ClassVar[int]
    FKYE_FIELD_NUMBER: _ClassVar[int]
    FKYF_FIELD_NUMBER: _ClassVar[int]
    FKYG_FIELD_NUMBER: _ClassVar[int]
    fkxz: str
    fkya: kse
    fkyb: ksi
    fkyc: ksw
    fkyd: ktl
    fkye: ktq
    fkyf: ktv
    fkyg: kud
    def __init__(self, fkxz: _Optional[str] = ..., fkya: _Optional[_Union[kse, _Mapping]] = ..., fkyb: _Optional[_Union[ksi, _Mapping]] = ..., fkyc: _Optional[_Union[ksw, _Mapping]] = ..., fkyd: _Optional[_Union[ktl, _Mapping]] = ..., fkye: _Optional[_Union[ktq, _Mapping]] = ..., fkyf: _Optional[_Union[ktv, _Mapping]] = ..., fkyg: _Optional[_Union[kud, _Mapping]] = ...) -> None: ...

class ksb(_message.Message):
    __slots__ = ("fkyl", "fkym", "fkyn", "fkyo", "fkyp", "fkyq", "fkyr")
    FKYL_FIELD_NUMBER: _ClassVar[int]
    FKYM_FIELD_NUMBER: _ClassVar[int]
    FKYN_FIELD_NUMBER: _ClassVar[int]
    FKYO_FIELD_NUMBER: _ClassVar[int]
    FKYP_FIELD_NUMBER: _ClassVar[int]
    FKYQ_FIELD_NUMBER: _ClassVar[int]
    FKYR_FIELD_NUMBER: _ClassVar[int]
    fkyl: str
    fkym: ksf
    fkyn: ksv
    fkyo: ktb
    fkyp: ktn
    fkyq: kuc
    fkyr: kuk
    def __init__(self, fkyl: _Optional[str] = ..., fkym: _Optional[_Union[ksf, _Mapping]] = ..., fkyn: _Optional[_Union[ksv, _Mapping]] = ..., fkyo: _Optional[_Union[ktb, _Mapping]] = ..., fkyp: _Optional[_Union[ktn, _Mapping]] = ..., fkyq: _Optional[_Union[kuc, _Mapping]] = ..., fkyr: _Optional[_Union[kuk, _Mapping]] = ...) -> None: ...

class ksd(_message.Message):
    __slots__ = ("fkyw",)
    FKYW_FIELD_NUMBER: _ClassVar[int]
    fkyw: ksg
    def __init__(self, fkyw: _Optional[_Union[ksg, _Mapping]] = ...) -> None: ...

class kse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ksf(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ksg(_message.Message):
    __slots__ = ("fkzh",)
    FKZH_FIELD_NUMBER: _ClassVar[int]
    fkzh: kth
    def __init__(self, fkzh: _Optional[_Union[kth, _Mapping]] = ...) -> None: ...

class ksi(_message.Message):
    __slots__ = ("fkzl", "fkzo", "fkzm", "fkzn")
    FKZL_FIELD_NUMBER: _ClassVar[int]
    FKZO_FIELD_NUMBER: _ClassVar[int]
    FKZM_FIELD_NUMBER: _ClassVar[int]
    FKZN_FIELD_NUMBER: _ClassVar[int]
    fkzl: str
    fkzo: str
    fkzm: ksl
    fkzn: ksm
    def __init__(self, fkzl: _Optional[str] = ..., fkzo: _Optional[str] = ..., fkzm: _Optional[_Union[ksl, _Mapping]] = ..., fkzn: _Optional[_Union[ksm, _Mapping]] = ...) -> None: ...

class ksl(_message.Message):
    __slots__ = ("fkzy", "fkzz")
    class ksj(_message.Message):
        __slots__ = ("fkzt", "fkzu")
        FKZT_FIELD_NUMBER: _ClassVar[int]
        FKZU_FIELD_NUMBER: _ClassVar[int]
        fkzt: int
        fkzu: str
        def __init__(self, fkzt: _Optional[int] = ..., fkzu: _Optional[str] = ...) -> None: ...
    FKZY_FIELD_NUMBER: _ClassVar[int]
    FKZZ_FIELD_NUMBER: _ClassVar[int]
    fkzy: str
    fkzz: ksl.ksj
    def __init__(self, fkzy: _Optional[str] = ..., fkzz: _Optional[_Union[ksl.ksj, _Mapping]] = ...) -> None: ...

class ksm(_message.Message):
    __slots__ = ("flad",)
    FLAD_FIELD_NUMBER: _ClassVar[int]
    flad: str
    def __init__(self, flad: _Optional[str] = ...) -> None: ...

class ksv(_message.Message):
    __slots__ = ("flbo", "flbp")
    class ksq(_message.Message):
        __slots__ = ("flat", "flau", "flav", "flaw", "flax", "flay", "flaz", "flbb", "flbc")
        class kso(_message.Message):
            __slots__ = ("flai", "flaj", "flak", "flal", "flam", "flan", "flao", "flap")
            FLAI_FIELD_NUMBER: _ClassVar[int]
            FLAJ_FIELD_NUMBER: _ClassVar[int]
            FLAK_FIELD_NUMBER: _ClassVar[int]
            FLAL_FIELD_NUMBER: _ClassVar[int]
            FLAM_FIELD_NUMBER: _ClassVar[int]
            FLAN_FIELD_NUMBER: _ClassVar[int]
            FLAO_FIELD_NUMBER: _ClassVar[int]
            FLAP_FIELD_NUMBER: _ClassVar[int]
            flai: bool
            flaj: bool
            flak: bool
            flal: bool
            flam: bool
            flan: bool
            flao: bool
            flap: bool
            def __init__(self, flai: bool = ..., flaj: bool = ..., flak: bool = ..., flal: bool = ..., flam: bool = ..., flan: bool = ..., flao: bool = ..., flap: bool = ...) -> None: ...
        FLAT_FIELD_NUMBER: _ClassVar[int]
        FLAU_FIELD_NUMBER: _ClassVar[int]
        FLAV_FIELD_NUMBER: _ClassVar[int]
        FLAW_FIELD_NUMBER: _ClassVar[int]
        FLAX_FIELD_NUMBER: _ClassVar[int]
        FLAY_FIELD_NUMBER: _ClassVar[int]
        FLAZ_FIELD_NUMBER: _ClassVar[int]
        FLBB_FIELD_NUMBER: _ClassVar[int]
        FLBC_FIELD_NUMBER: _ClassVar[int]
        flat: int
        flau: str
        flav: str
        flaw: kte
        flax: str
        flay: ksv.ksq.kso
        flaz: int
        flbb: kto
        flbc: kul
        def __init__(self, flat: _Optional[int] = ..., flau: _Optional[str] = ..., flav: _Optional[str] = ..., flaw: _Optional[_Union[kte, _Mapping]] = ..., flax: _Optional[str] = ..., flay: _Optional[_Union[ksv.ksq.kso, _Mapping]] = ..., flaz: _Optional[int] = ..., flbb: _Optional[_Union[kto, _Mapping]] = ..., flbc: _Optional[_Union[kul, _Mapping]] = ...) -> None: ...
    class kst(_message.Message):
        __slots__ = ("flbg", "flbh", "flbj")
        class ksr(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            KSR_EPSW: _ClassVar[ksv.kst.ksr]
            KSR_EPSX: _ClassVar[ksv.kst.ksr]
            KSR_EPSY: _ClassVar[ksv.kst.ksr]
            KSR_EPSZ: _ClassVar[ksv.kst.ksr]
            KSR_EPTA: _ClassVar[ksv.kst.ksr]
            KSR_EPTB: _ClassVar[ksv.kst.ksr]
            KSR_EPTC: _ClassVar[ksv.kst.ksr]
            KSR_EPTD: _ClassVar[ksv.kst.ksr]
            KSR_EPTE: _ClassVar[ksv.kst.ksr]
            KSR_EPTF: _ClassVar[ksv.kst.ksr]
            KSR_EPTG: _ClassVar[ksv.kst.ksr]
            KSR_EPTH: _ClassVar[ksv.kst.ksr]
            KSR_EPTI: _ClassVar[ksv.kst.ksr]
            KSR_EPTJ: _ClassVar[ksv.kst.ksr]
        KSR_EPSW: ksv.kst.ksr
        KSR_EPSX: ksv.kst.ksr
        KSR_EPSY: ksv.kst.ksr
        KSR_EPSZ: ksv.kst.ksr
        KSR_EPTA: ksv.kst.ksr
        KSR_EPTB: ksv.kst.ksr
        KSR_EPTC: ksv.kst.ksr
        KSR_EPTD: ksv.kst.ksr
        KSR_EPTE: ksv.kst.ksr
        KSR_EPTF: ksv.kst.ksr
        KSR_EPTG: ksv.kst.ksr
        KSR_EPTH: ksv.kst.ksr
        KSR_EPTI: ksv.kst.ksr
        KSR_EPTJ: ksv.kst.ksr
        FLBG_FIELD_NUMBER: _ClassVar[int]
        FLBH_FIELD_NUMBER: _ClassVar[int]
        FLBJ_FIELD_NUMBER: _ClassVar[int]
        flbg: ksv.kst.ksr
        flbh: str
        flbj: str
        def __init__(self, flbg: _Optional[_Union[ksv.kst.ksr, str]] = ..., flbh: _Optional[str] = ..., flbj: _Optional[str] = ...) -> None: ...
    FLBO_FIELD_NUMBER: _ClassVar[int]
    FLBP_FIELD_NUMBER: _ClassVar[int]
    flbo: ksv.ksq
    flbp: ksv.kst
    def __init__(self, flbo: _Optional[_Union[ksv.ksq, _Mapping]] = ..., flbp: _Optional[_Union[ksv.kst, _Mapping]] = ...) -> None: ...

class ksw(_message.Message):
    __slots__ = ("flbu",)
    FLBU_FIELD_NUMBER: _ClassVar[int]
    flbu: int
    def __init__(self, flbu: _Optional[int] = ...) -> None: ...

class ktb(_message.Message):
    __slots__ = ("flce", "flcf")
    class ksy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KSY_EPUH: _ClassVar[ktb.ksy]
        KSY_EPUI: _ClassVar[ktb.ksy]
        KSY_EPUJ: _ClassVar[ktb.ksy]
        KSY_EPUK: _ClassVar[ktb.ksy]
    KSY_EPUH: ktb.ksy
    KSY_EPUI: ktb.ksy
    KSY_EPUJ: ktb.ksy
    KSY_EPUK: ktb.ksy
    class ksz(_message.Message):
        __slots__ = ("flby", "flbz", "flca")
        FLBY_FIELD_NUMBER: _ClassVar[int]
        FLBZ_FIELD_NUMBER: _ClassVar[int]
        FLCA_FIELD_NUMBER: _ClassVar[int]
        flby: str
        flbz: str
        flca: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, flby: _Optional[str] = ..., flbz: _Optional[str] = ..., flca: _Optional[_Iterable[int]] = ...) -> None: ...
    FLCE_FIELD_NUMBER: _ClassVar[int]
    FLCF_FIELD_NUMBER: _ClassVar[int]
    flce: ktb.ksz
    flcf: ktb.ksy
    def __init__(self, flce: _Optional[_Union[ktb.ksz, _Mapping]] = ..., flcf: _Optional[_Union[ktb.ksy, str]] = ...) -> None: ...

class kte(_message.Message):
    __slots__ = ("flcq", "flcr", "flcs")
    class ktc(_message.Message):
        __slots__ = ("flcl", "flcm")
        FLCL_FIELD_NUMBER: _ClassVar[int]
        FLCM_FIELD_NUMBER: _ClassVar[int]
        flcl: krv
        flcm: int
        def __init__(self, flcl: _Optional[_Union[krv, str]] = ..., flcm: _Optional[int] = ...) -> None: ...
    FLCQ_FIELD_NUMBER: _ClassVar[int]
    FLCR_FIELD_NUMBER: _ClassVar[int]
    FLCS_FIELD_NUMBER: _ClassVar[int]
    flcq: _containers.RepeatedCompositeFieldContainer[kth]
    flcr: _containers.RepeatedCompositeFieldContainer[kte.ktc]
    flcs: bool
    def __init__(self, flcq: _Optional[_Iterable[_Union[kth, _Mapping]]] = ..., flcr: _Optional[_Iterable[_Union[kte.ktc, _Mapping]]] = ..., flcs: bool = ...) -> None: ...

class kth(_message.Message):
    __slots__ = ("flcw", "flcx", "flcy")
    class ktf(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KTF_EPVQ: _ClassVar[kth.ktf]
        KTF_EPVR: _ClassVar[kth.ktf]
        KTF_EPVS: _ClassVar[kth.ktf]
        KTF_EPVT: _ClassVar[kth.ktf]
    KTF_EPVQ: kth.ktf
    KTF_EPVR: kth.ktf
    KTF_EPVS: kth.ktf
    KTF_EPVT: kth.ktf
    FLCW_FIELD_NUMBER: _ClassVar[int]
    FLCX_FIELD_NUMBER: _ClassVar[int]
    FLCY_FIELD_NUMBER: _ClassVar[int]
    flcw: ktk
    flcx: kth.ktf
    flcy: _containers.RepeatedCompositeFieldContainer[ktu]
    def __init__(self, flcw: _Optional[_Union[ktk, _Mapping]] = ..., flcx: _Optional[_Union[kth.ktf, str]] = ..., flcy: _Optional[_Iterable[_Union[ktu, _Mapping]]] = ...) -> None: ...

class ktk(_message.Message):
    __slots__ = ("fldc", "fldd", "flde")
    class kti(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KTI_EPWD: _ClassVar[ktk.kti]
        KTI_EPWE: _ClassVar[ktk.kti]
    KTI_EPWD: ktk.kti
    KTI_EPWE: ktk.kti
    FLDC_FIELD_NUMBER: _ClassVar[int]
    FLDD_FIELD_NUMBER: _ClassVar[int]
    FLDE_FIELD_NUMBER: _ClassVar[int]
    fldc: int
    fldd: ktk.kti
    flde: krv
    def __init__(self, fldc: _Optional[int] = ..., fldd: _Optional[_Union[ktk.kti, str]] = ..., flde: _Optional[_Union[krv, str]] = ...) -> None: ...

class ktl(_message.Message):
    __slots__ = ("fldi",)
    FLDI_FIELD_NUMBER: _ClassVar[int]
    fldi: int
    def __init__(self, fldi: _Optional[int] = ...) -> None: ...

class ktn(_message.Message):
    __slots__ = ("fldm", "fldn")
    FLDM_FIELD_NUMBER: _ClassVar[int]
    FLDN_FIELD_NUMBER: _ClassVar[int]
    fldm: kto
    fldn: ktp
    def __init__(self, fldm: _Optional[_Union[kto, _Mapping]] = ..., fldn: _Optional[_Union[ktp, _Mapping]] = ...) -> None: ...

class kto(_message.Message):
    __slots__ = ("flds", "fldt", "fldu", "fldv", "fldw")
    FLDS_FIELD_NUMBER: _ClassVar[int]
    FLDT_FIELD_NUMBER: _ClassVar[int]
    FLDU_FIELD_NUMBER: _ClassVar[int]
    FLDV_FIELD_NUMBER: _ClassVar[int]
    FLDW_FIELD_NUMBER: _ClassVar[int]
    flds: bool
    fldt: int
    fldu: str
    fldv: str
    fldw: kte
    def __init__(self, flds: bool = ..., fldt: _Optional[int] = ..., fldu: _Optional[str] = ..., fldv: _Optional[str] = ..., fldw: _Optional[_Union[kte, _Mapping]] = ...) -> None: ...

class ktp(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ktq(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ktu(_message.Message):
    __slots__ = ("fleg", "fleh", "flei", "flej", "flek")
    class kts(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KTS_EPXS: _ClassVar[ktu.kts]
        KTS_EPXT: _ClassVar[ktu.kts]
        KTS_EPXU: _ClassVar[ktu.kts]
        KTS_EPXV: _ClassVar[ktu.kts]
        KTS_EPXW: _ClassVar[ktu.kts]
        KTS_EPXX: _ClassVar[ktu.kts]
        KTS_EPXY: _ClassVar[ktu.kts]
        KTS_EPXZ: _ClassVar[ktu.kts]
        KTS_EPYA: _ClassVar[ktu.kts]
        KTS_EPYB: _ClassVar[ktu.kts]
        KTS_EPYC: _ClassVar[ktu.kts]
        KTS_EPYD: _ClassVar[ktu.kts]
        KTS_EPYE: _ClassVar[ktu.kts]
        KTS_EPYF: _ClassVar[ktu.kts]
        KTS_EPYG: _ClassVar[ktu.kts]
        KTS_EPYH: _ClassVar[ktu.kts]
        KTS_EPYI: _ClassVar[ktu.kts]
        KTS_EPYJ: _ClassVar[ktu.kts]
        KTS_EPYK: _ClassVar[ktu.kts]
    KTS_EPXS: ktu.kts
    KTS_EPXT: ktu.kts
    KTS_EPXU: ktu.kts
    KTS_EPXV: ktu.kts
    KTS_EPXW: ktu.kts
    KTS_EPXX: ktu.kts
    KTS_EPXY: ktu.kts
    KTS_EPXZ: ktu.kts
    KTS_EPYA: ktu.kts
    KTS_EPYB: ktu.kts
    KTS_EPYC: ktu.kts
    KTS_EPYD: ktu.kts
    KTS_EPYE: ktu.kts
    KTS_EPYF: ktu.kts
    KTS_EPYG: ktu.kts
    KTS_EPYH: ktu.kts
    KTS_EPYI: ktu.kts
    KTS_EPYJ: ktu.kts
    KTS_EPYK: ktu.kts
    class ktr(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KTR_EPXQ: _ClassVar[ktu.ktr]
        KTR_EPXR: _ClassVar[ktu.ktr]
    KTR_EPXQ: ktu.ktr
    KTR_EPXR: ktu.ktr
    FLEG_FIELD_NUMBER: _ClassVar[int]
    FLEH_FIELD_NUMBER: _ClassVar[int]
    FLEI_FIELD_NUMBER: _ClassVar[int]
    FLEJ_FIELD_NUMBER: _ClassVar[int]
    FLEK_FIELD_NUMBER: _ClassVar[int]
    fleg: str
    fleh: ktu.kts
    flei: ktu.ktr
    flej: int
    flek: str
    def __init__(self, fleg: _Optional[str] = ..., fleh: _Optional[_Union[ktu.kts, str]] = ..., flei: _Optional[_Union[ktu.ktr, str]] = ..., flej: _Optional[int] = ..., flek: _Optional[str] = ...) -> None: ...

class ktv(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class kuc(_message.Message):
    __slots__ = ("flfb", "flfc")
    class ktx(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KTX_EPZC: _ClassVar[kuc.ktx]
        KTX_EPZD: _ClassVar[kuc.ktx]
    KTX_EPZC: kuc.ktx
    KTX_EPZD: kuc.ktx
    class kua(_message.Message):
        __slots__ = ("flex",)
        class kty(_message.Message):
            __slots__ = ("fler", "fles", "flet")
            FLER_FIELD_NUMBER: _ClassVar[int]
            FLES_FIELD_NUMBER: _ClassVar[int]
            FLET_FIELD_NUMBER: _ClassVar[int]
            fler: str
            fles: str
            flet: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, fler: _Optional[str] = ..., fles: _Optional[str] = ..., flet: _Optional[_Iterable[int]] = ...) -> None: ...
        FLEX_FIELD_NUMBER: _ClassVar[int]
        flex: _containers.RepeatedCompositeFieldContainer[kuc.kua.kty]
        def __init__(self, flex: _Optional[_Iterable[_Union[kuc.kua.kty, _Mapping]]] = ...) -> None: ...
    FLFB_FIELD_NUMBER: _ClassVar[int]
    FLFC_FIELD_NUMBER: _ClassVar[int]
    flfb: kuc.kua
    flfc: kuc.ktx
    def __init__(self, flfb: _Optional[_Union[kuc.kua, _Mapping]] = ..., flfc: _Optional[_Union[kuc.ktx, str]] = ...) -> None: ...

class kud(_message.Message):
    __slots__ = ("flfi", "flfj")
    FLFI_FIELD_NUMBER: _ClassVar[int]
    FLFJ_FIELD_NUMBER: _ClassVar[int]
    flfi: str
    flfj: str
    def __init__(self, flfi: _Optional[str] = ..., flfj: _Optional[str] = ...) -> None: ...

class kuk(_message.Message):
    __slots__ = ("flfv", "flfw")
    class kuf(_message.Message):
        __slots__ = ("flfn",)
        FLFN_FIELD_NUMBER: _ClassVar[int]
        flfn: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, flfn: _Optional[_Iterable[int]] = ...) -> None: ...
    class kui(_message.Message):
        __slots__ = ("flfr",)
        class kug(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            KUG_EQAM: _ClassVar[kuk.kui.kug]
            KUG_EQAN: _ClassVar[kuk.kui.kug]
            KUG_EQAO: _ClassVar[kuk.kui.kug]
            KUG_EQAP: _ClassVar[kuk.kui.kug]
        KUG_EQAM: kuk.kui.kug
        KUG_EQAN: kuk.kui.kug
        KUG_EQAO: kuk.kui.kug
        KUG_EQAP: kuk.kui.kug
        FLFR_FIELD_NUMBER: _ClassVar[int]
        flfr: kuk.kui.kug
        def __init__(self, flfr: _Optional[_Union[kuk.kui.kug, str]] = ...) -> None: ...
    FLFV_FIELD_NUMBER: _ClassVar[int]
    FLFW_FIELD_NUMBER: _ClassVar[int]
    flfv: kuk.kuf
    flfw: kuk.kui
    def __init__(self, flfv: _Optional[_Union[kuk.kuf, _Mapping]] = ..., flfw: _Optional[_Union[kuk.kui, _Mapping]] = ...) -> None: ...

class kul(_message.Message):
    __slots__ = ("flgb", "flgc", "flgd")
    FLGB_FIELD_NUMBER: _ClassVar[int]
    FLGC_FIELD_NUMBER: _ClassVar[int]
    FLGD_FIELD_NUMBER: _ClassVar[int]
    flgb: str
    flgc: str
    flgd: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, flgb: _Optional[str] = ..., flgc: _Optional[str] = ..., flgd: _Optional[_Iterable[int]] = ...) -> None: ...
