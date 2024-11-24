from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class leg(_message.Message):
    __slots__ = ("frcz", "frda", "frdb")
    FRCZ_FIELD_NUMBER: _ClassVar[int]
    FRDA_FIELD_NUMBER: _ClassVar[int]
    FRDB_FIELD_NUMBER: _ClassVar[int]
    frcz: lei
    frda: lek
    frdb: lem
    def __init__(self, frcz: _Optional[_Union[lei, _Mapping]] = ..., frda: _Optional[_Union[lek, _Mapping]] = ..., frdb: _Optional[_Union[lem, _Mapping]] = ...) -> None: ...

class lei(_message.Message):
    __slots__ = ("frdg", "frdh", "frdi", "frdj", "frdk", "frdl", "frdm", "frdn")
    FRDG_FIELD_NUMBER: _ClassVar[int]
    FRDH_FIELD_NUMBER: _ClassVar[int]
    FRDI_FIELD_NUMBER: _ClassVar[int]
    FRDJ_FIELD_NUMBER: _ClassVar[int]
    FRDK_FIELD_NUMBER: _ClassVar[int]
    FRDL_FIELD_NUMBER: _ClassVar[int]
    FRDM_FIELD_NUMBER: _ClassVar[int]
    FRDN_FIELD_NUMBER: _ClassVar[int]
    frdg: str
    frdh: len
    frdi: ler
    frdj: lff
    frdk: lfu
    frdl: lfz
    frdm: lge
    frdn: lgm
    def __init__(self, frdg: _Optional[str] = ..., frdh: _Optional[_Union[len, _Mapping]] = ..., frdi: _Optional[_Union[ler, _Mapping]] = ..., frdj: _Optional[_Union[lff, _Mapping]] = ..., frdk: _Optional[_Union[lfu, _Mapping]] = ..., frdl: _Optional[_Union[lfz, _Mapping]] = ..., frdm: _Optional[_Union[lge, _Mapping]] = ..., frdn: _Optional[_Union[lgm, _Mapping]] = ...) -> None: ...

class len(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ler(_message.Message):
    __slots__ = ("fret", "freu", "frev", "frew")
    FRET_FIELD_NUMBER: _ClassVar[int]
    FREU_FIELD_NUMBER: _ClassVar[int]
    FREV_FIELD_NUMBER: _ClassVar[int]
    FREW_FIELD_NUMBER: _ClassVar[int]
    fret: str
    freu: leu
    frev: lev
    frew: str
    def __init__(self, fret: _Optional[str] = ..., freu: _Optional[_Union[leu, _Mapping]] = ..., frev: _Optional[_Union[lev, _Mapping]] = ..., frew: _Optional[str] = ...) -> None: ...

class leu(_message.Message):
    __slots__ = ("frfg", "frfh")
    class les(_message.Message):
        __slots__ = ("frfb", "frfc")
        FRFB_FIELD_NUMBER: _ClassVar[int]
        FRFC_FIELD_NUMBER: _ClassVar[int]
        frfb: int
        frfc: str
        def __init__(self, frfb: _Optional[int] = ..., frfc: _Optional[str] = ...) -> None: ...
    FRFG_FIELD_NUMBER: _ClassVar[int]
    FRFH_FIELD_NUMBER: _ClassVar[int]
    frfg: str
    frfh: leu.les
    def __init__(self, frfg: _Optional[str] = ..., frfh: _Optional[_Union[leu.les, _Mapping]] = ...) -> None: ...

class lev(_message.Message):
    __slots__ = ("frfl",)
    FRFL_FIELD_NUMBER: _ClassVar[int]
    frfl: str
    def __init__(self, frfl: _Optional[str] = ...) -> None: ...

class lff(_message.Message):
    __slots__ = ("frgx",)
    FRGX_FIELD_NUMBER: _ClassVar[int]
    frgx: int
    def __init__(self, frgx: _Optional[int] = ...) -> None: ...

class lfu(_message.Message):
    __slots__ = ("fril",)
    FRIL_FIELD_NUMBER: _ClassVar[int]
    fril: int
    def __init__(self, fril: _Optional[int] = ...) -> None: ...

class lfz(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class lge(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class lgm(_message.Message):
    __slots__ = ("frkl", "frkm")
    FRKL_FIELD_NUMBER: _ClassVar[int]
    FRKM_FIELD_NUMBER: _ClassVar[int]
    frkl: str
    frkm: str
    def __init__(self, frkl: _Optional[str] = ..., frkm: _Optional[str] = ...) -> None: ...

class lek(_message.Message):
    __slots__ = ("frds", "frdt", "frdu", "frdv", "frdw", "frdx", "frdy")
    FRDS_FIELD_NUMBER: _ClassVar[int]
    FRDT_FIELD_NUMBER: _ClassVar[int]
    FRDU_FIELD_NUMBER: _ClassVar[int]
    FRDV_FIELD_NUMBER: _ClassVar[int]
    FRDW_FIELD_NUMBER: _ClassVar[int]
    FRDX_FIELD_NUMBER: _ClassVar[int]
    FRDY_FIELD_NUMBER: _ClassVar[int]
    frds: str
    frdt: leo
    frdu: lfe
    frdv: lfk
    frdw: lfw
    frdx: lgl
    frdy: lgt
    def __init__(self, frds: _Optional[str] = ..., frdt: _Optional[_Union[leo, _Mapping]] = ..., frdu: _Optional[_Union[lfe, _Mapping]] = ..., frdv: _Optional[_Union[lfk, _Mapping]] = ..., frdw: _Optional[_Union[lfw, _Mapping]] = ..., frdx: _Optional[_Union[lgl, _Mapping]] = ..., frdy: _Optional[_Union[lgt, _Mapping]] = ...) -> None: ...

class leo(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class lfe(_message.Message):
    __slots__ = ("frgr", "frgs")
    class lez(_message.Message):
        __slots__ = ("frfw", "frfx", "frfy", "frfz", "frga", "frgb", "frgc", "frge", "frgf")
        class lex(_message.Message):
            __slots__ = ("frfp", "frfq", "frfr", "frfs")
            FRFP_FIELD_NUMBER: _ClassVar[int]
            FRFQ_FIELD_NUMBER: _ClassVar[int]
            FRFR_FIELD_NUMBER: _ClassVar[int]
            FRFS_FIELD_NUMBER: _ClassVar[int]
            frfp: bool
            frfq: bool
            frfr: bool
            frfs: bool
            def __init__(self, frfp: bool = ..., frfq: bool = ..., frfr: bool = ..., frfs: bool = ...) -> None: ...
        FRFW_FIELD_NUMBER: _ClassVar[int]
        FRFX_FIELD_NUMBER: _ClassVar[int]
        FRFY_FIELD_NUMBER: _ClassVar[int]
        FRFZ_FIELD_NUMBER: _ClassVar[int]
        FRGA_FIELD_NUMBER: _ClassVar[int]
        FRGB_FIELD_NUMBER: _ClassVar[int]
        FRGC_FIELD_NUMBER: _ClassVar[int]
        FRGE_FIELD_NUMBER: _ClassVar[int]
        FRGF_FIELD_NUMBER: _ClassVar[int]
        frfw: int
        frfx: str
        frfy: str
        frfz: lfn
        frga: str
        frgb: lfe.lez.lex
        frgc: int
        frge: lfx
        frgf: lgu
        def __init__(self, frfw: _Optional[int] = ..., frfx: _Optional[str] = ..., frfy: _Optional[str] = ..., frfz: _Optional[_Union[lfn, _Mapping]] = ..., frga: _Optional[str] = ..., frgb: _Optional[_Union[lfe.lez.lex, _Mapping]] = ..., frgc: _Optional[int] = ..., frge: _Optional[_Union[lfx, _Mapping]] = ..., frgf: _Optional[_Union[lgu, _Mapping]] = ...) -> None: ...
    class lfc(_message.Message):
        __slots__ = ("frgj", "frgk", "frgm")
        class lfa(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        FRGJ_FIELD_NUMBER: _ClassVar[int]
        FRGK_FIELD_NUMBER: _ClassVar[int]
        FRGM_FIELD_NUMBER: _ClassVar[int]
        frgj: lfe.lfc.lfa
        frgk: str
        frgm: str
        def __init__(self, frgj: _Optional[_Union[lfe.lfc.lfa, _Mapping]] = ..., frgk: _Optional[str] = ..., frgm: _Optional[str] = ...) -> None: ...
    FRGR_FIELD_NUMBER: _ClassVar[int]
    FRGS_FIELD_NUMBER: _ClassVar[int]
    frgr: lfe.lez
    frgs: lfe.lfc
    def __init__(self, frgr: _Optional[_Union[lfe.lez, _Mapping]] = ..., frgs: _Optional[_Union[lfe.lfc, _Mapping]] = ...) -> None: ...

class lfn(_message.Message):
    __slots__ = ("frht", "frhu", "frhv")
    class lfl(_message.Message):
        __slots__ = ("frho", "frhp")
        FRHO_FIELD_NUMBER: _ClassVar[int]
        FRHP_FIELD_NUMBER: _ClassVar[int]
        frho: lee
        frhp: int
        def __init__(self, frho: _Optional[_Union[lee, _Mapping]] = ..., frhp: _Optional[int] = ...) -> None: ...
    FRHT_FIELD_NUMBER: _ClassVar[int]
    FRHU_FIELD_NUMBER: _ClassVar[int]
    FRHV_FIELD_NUMBER: _ClassVar[int]
    frht: _containers.RepeatedCompositeFieldContainer[lfq]
    frhu: _containers.RepeatedCompositeFieldContainer[lfn.lfl]
    frhv: bool
    def __init__(self, frht: _Optional[_Iterable[_Union[lfq, _Mapping]]] = ..., frhu: _Optional[_Iterable[_Union[lfn.lfl, _Mapping]]] = ..., frhv: bool = ...) -> None: ...

class lfq(_message.Message):
    __slots__ = ("frhz", "fria", "frib")
    class lfo(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    FRHZ_FIELD_NUMBER: _ClassVar[int]
    FRIA_FIELD_NUMBER: _ClassVar[int]
    FRIB_FIELD_NUMBER: _ClassVar[int]
    frhz: lft
    fria: lfq.lfo
    frib: _containers.RepeatedCompositeFieldContainer[lgd]
    def __init__(self, frhz: _Optional[_Union[lft, _Mapping]] = ..., fria: _Optional[_Union[lfq.lfo, _Mapping]] = ..., frib: _Optional[_Iterable[_Union[lgd, _Mapping]]] = ...) -> None: ...

class lft(_message.Message):
    __slots__ = ("frif", "frig", "frih")
    class lfr(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    FRIF_FIELD_NUMBER: _ClassVar[int]
    FRIG_FIELD_NUMBER: _ClassVar[int]
    FRIH_FIELD_NUMBER: _ClassVar[int]
    frif: int
    frig: lft.lfr
    frih: lee
    def __init__(self, frif: _Optional[int] = ..., frig: _Optional[_Union[lft.lfr, _Mapping]] = ..., frih: _Optional[_Union[lee, _Mapping]] = ...) -> None: ...

class lee(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class lgd(_message.Message):
    __slots__ = ("frjj", "frjk", "frjl", "frjm", "frjn")
    class lgb(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class lga(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    FRJJ_FIELD_NUMBER: _ClassVar[int]
    FRJK_FIELD_NUMBER: _ClassVar[int]
    FRJL_FIELD_NUMBER: _ClassVar[int]
    FRJM_FIELD_NUMBER: _ClassVar[int]
    FRJN_FIELD_NUMBER: _ClassVar[int]
    frjj: str
    frjk: lgd.lgb
    frjl: lgd.lga
    frjm: int
    frjn: str
    def __init__(self, frjj: _Optional[str] = ..., frjk: _Optional[_Union[lgd.lgb, _Mapping]] = ..., frjl: _Optional[_Union[lgd.lga, _Mapping]] = ..., frjm: _Optional[int] = ..., frjn: _Optional[str] = ...) -> None: ...

class lfx(_message.Message):
    __slots__ = ("friv", "friw", "frix", "friy", "friz")
    FRIV_FIELD_NUMBER: _ClassVar[int]
    FRIW_FIELD_NUMBER: _ClassVar[int]
    FRIX_FIELD_NUMBER: _ClassVar[int]
    FRIY_FIELD_NUMBER: _ClassVar[int]
    FRIZ_FIELD_NUMBER: _ClassVar[int]
    friv: bool
    friw: int
    frix: str
    friy: str
    friz: lfn
    def __init__(self, friv: bool = ..., friw: _Optional[int] = ..., frix: _Optional[str] = ..., friy: _Optional[str] = ..., friz: _Optional[_Union[lfn, _Mapping]] = ...) -> None: ...

class lgu(_message.Message):
    __slots__ = ("frle", "frlf", "frlg")
    FRLE_FIELD_NUMBER: _ClassVar[int]
    FRLF_FIELD_NUMBER: _ClassVar[int]
    FRLG_FIELD_NUMBER: _ClassVar[int]
    frle: str
    frlf: str
    frlg: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, frle: _Optional[str] = ..., frlf: _Optional[str] = ..., frlg: _Optional[_Iterable[int]] = ...) -> None: ...

class lfk(_message.Message):
    __slots__ = ("frhh", "frhi")
    class lfi(_message.Message):
        __slots__ = ("frhb", "frhc", "frhd")
        FRHB_FIELD_NUMBER: _ClassVar[int]
        FRHC_FIELD_NUMBER: _ClassVar[int]
        FRHD_FIELD_NUMBER: _ClassVar[int]
        frhb: str
        frhc: str
        frhd: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, frhb: _Optional[str] = ..., frhc: _Optional[str] = ..., frhd: _Optional[_Iterable[int]] = ...) -> None: ...
    class lfh(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    FRHH_FIELD_NUMBER: _ClassVar[int]
    FRHI_FIELD_NUMBER: _ClassVar[int]
    frhh: lfk.lfi
    frhi: lfk.lfh
    def __init__(self, frhh: _Optional[_Union[lfk.lfi, _Mapping]] = ..., frhi: _Optional[_Union[lfk.lfh, _Mapping]] = ...) -> None: ...

class lfw(_message.Message):
    __slots__ = ("frip", "friq")
    FRIP_FIELD_NUMBER: _ClassVar[int]
    FRIQ_FIELD_NUMBER: _ClassVar[int]
    frip: lfx
    friq: lfy
    def __init__(self, frip: _Optional[_Union[lfx, _Mapping]] = ..., friq: _Optional[_Union[lfy, _Mapping]] = ...) -> None: ...

class lfy(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class lgl(_message.Message):
    __slots__ = ("frke", "frkf")
    class lgj(_message.Message):
        __slots__ = ("frka",)
        class lgh(_message.Message):
            __slots__ = ("frju", "frjv", "frjw")
            FRJU_FIELD_NUMBER: _ClassVar[int]
            FRJV_FIELD_NUMBER: _ClassVar[int]
            FRJW_FIELD_NUMBER: _ClassVar[int]
            frju: str
            frjv: str
            frjw: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, frju: _Optional[str] = ..., frjv: _Optional[str] = ..., frjw: _Optional[_Iterable[int]] = ...) -> None: ...
        FRKA_FIELD_NUMBER: _ClassVar[int]
        frka: _containers.RepeatedCompositeFieldContainer[lgl.lgj.lgh]
        def __init__(self, frka: _Optional[_Iterable[_Union[lgl.lgj.lgh, _Mapping]]] = ...) -> None: ...
    class lgg(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    FRKE_FIELD_NUMBER: _ClassVar[int]
    FRKF_FIELD_NUMBER: _ClassVar[int]
    frke: lgl.lgj
    frkf: lgl.lgg
    def __init__(self, frke: _Optional[_Union[lgl.lgj, _Mapping]] = ..., frkf: _Optional[_Union[lgl.lgg, _Mapping]] = ...) -> None: ...

class lgt(_message.Message):
    __slots__ = ("frky", "frkz")
    class lgo(_message.Message):
        __slots__ = ("frkq",)
        FRKQ_FIELD_NUMBER: _ClassVar[int]
        frkq: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, frkq: _Optional[_Iterable[int]] = ...) -> None: ...
    class lgr(_message.Message):
        __slots__ = ("frku",)
        class lgp(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        FRKU_FIELD_NUMBER: _ClassVar[int]
        frku: lgt.lgr.lgp
        def __init__(self, frku: _Optional[_Union[lgt.lgr.lgp, _Mapping]] = ...) -> None: ...
    FRKY_FIELD_NUMBER: _ClassVar[int]
    FRKZ_FIELD_NUMBER: _ClassVar[int]
    frky: lgt.lgo
    frkz: lgt.lgr
    def __init__(self, frky: _Optional[_Union[lgt.lgo, _Mapping]] = ..., frkz: _Optional[_Union[lgt.lgr, _Mapping]] = ...) -> None: ...

class lem(_message.Message):
    __slots__ = ("fred",)
    FRED_FIELD_NUMBER: _ClassVar[int]
    fred: lep
    def __init__(self, fred: _Optional[_Union[lep, _Mapping]] = ...) -> None: ...

class lep(_message.Message):
    __slots__ = ("frep",)
    FREP_FIELD_NUMBER: _ClassVar[int]
    frep: lfq
    def __init__(self, frep: _Optional[_Union[lfq, _Mapping]] = ...) -> None: ...
