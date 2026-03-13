from collections.abc import Iterable, Sequence

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import (
    AccessAtomSignature,
    FieldAccessSignatures,
    FunctionAccessSignature,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField, FieldKey

# Rebuild models: model_copy retains stale cached similarity keys.


def rekey_access_atom(
    atom: AccessAtomSignature,
    obf_to_non_obf_offset: dict[int, int],
) -> AccessAtomSignature:
    """Keep unmapped offsets so positional access matching does not shift subsequent atoms."""
    if atom.field_offset is None:
        return atom
    return _build_atom(atom, obf_to_non_obf_offset.get(atom.field_offset, atom.field_offset))


def rekey_atom_list(
    atoms: Sequence[AccessAtomSignature],
    obf_to_non_obf_offset: dict[int, int],
) -> list[AccessAtomSignature]:
    return [rekey_access_atom(atom, obf_to_non_obf_offset) for atom in atoms]


def rekey_field_signatures(
    field_signatures: Sequence[FieldAccessSignatures],
    non_obf_field_by_obf_field_key: dict[FieldKey, DumpCSMessageField],
    obf_to_non_obf_offset: dict[int, int],
) -> dict[str, FieldAccessSignatures]:
    """Drop unnamed fields; the loader retains their real non-obfuscated signatures."""
    result: dict[str, FieldAccessSignatures] = {}
    for field_sig in field_signatures:
        non_obf_field = non_obf_field_by_obf_field_key.get(field_sig.field_key)
        if non_obf_field is None:
            continue
        assert non_obf_field.property_name is not None, "mapped fields must be property-backed"
        result[non_obf_field.property_name] = FieldAccessSignatures(
            field_key=non_obf_field.field_key,
            field_type_shape=field_sig.field_type_shape,
            accesses=rekey_atom_list(field_sig.accesses, obf_to_non_obf_offset),
            is_traced=field_sig.is_traced,
        )
    return result


def rekey_function_signatures(
    function_signatures: Sequence[FunctionAccessSignature],
    obf_to_non_obf_offset: dict[int, int],
) -> list[FunctionAccessSignature]:
    return dedupe_function_signatures(
        _build_function(function_sig, rekey_atom_list(function_sig.self_accesses, obf_to_non_obf_offset))
        for function_sig in function_signatures
    )


def dedupe_function_signatures(
    function_signatures: Iterable[FunctionAccessSignature],
) -> list[FunctionAccessSignature]:
    deduped: dict[object, FunctionAccessSignature] = {}
    for function_sig in function_signatures:
        deduped.setdefault(function_sig.similarity_key, function_sig)
    return list(deduped.values())


def _build_atom(atom: AccessAtomSignature, field_offset: int | None) -> AccessAtomSignature:
    return AccessAtomSignature(
        entry_type=atom.entry_type,
        access_kind=atom.access_kind,
        field_type_shape=atom.field_type_shape,
        field_offset=field_offset,
        index_in_function=atom.index_in_function,
    )


def _build_function(
    function_sig: FunctionAccessSignature,
    self_accesses: list[AccessAtomSignature],
) -> FunctionAccessSignature:
    return FunctionAccessSignature(
        return_role=function_sig.return_role,
        takes_message_parameter=function_sig.takes_message_parameter,
        size=function_sig.size,
        self_accesses=self_accesses,
        foreign_access_summary=function_sig.foreign_access_summary,
        opcode_histogram=function_sig.opcode_histogram,
        stable_callees=function_sig.stable_callees,
        cfg_stats=function_sig.cfg_stats,
    )
