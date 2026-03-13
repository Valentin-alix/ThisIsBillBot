from collections import Counter
from math import log

import numpy as np

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import AccessTraceDocument
from DBDofusUnity.proto_mapper_assembly.interfaces.affinity import AffinityResult, AffinitySignalInputs

_SMOOTHING = 1e-9


def build_callee_affinity(signal_inputs: AffinitySignalInputs, /) -> AffinityResult:
    """Return affinity and evidence mask from shared callees, weighted by rarity across both builds."""
    workspace = signal_inputs.workspace
    obf_access_trace = signal_inputs.obf_access_trace
    non_obf_access_trace = signal_inputs.non_obf_access_trace

    obf_callees_by_cls = _collect_callees_by_cls(obf_access_trace)
    non_obf_callees_by_cls = _collect_callees_by_cls(non_obf_access_trace)

    obf_classes = [signature.message_cls for signature in workspace.obf_signatures]
    non_obf_classes = [signature.message_cls for signature in workspace.non_obf_signatures]

    vocabulary = _build_shared_vocabulary(
        left_callees_by_cls=non_obf_callees_by_cls,
        right_callees_by_cls=obf_callees_by_cls,
        left_classes=non_obf_classes,
        right_classes=obf_classes,
    )
    affinity = np.zeros((len(non_obf_classes), len(obf_classes)))
    if not vocabulary:
        return AffinityResult(affinity, np.zeros_like(affinity, dtype=bool))

    weight_by_callee = _build_inverse_frequency_weights(
        vocabulary=vocabulary,
        left_callees_by_cls=non_obf_callees_by_cls,
        right_callees_by_cls=obf_callees_by_cls,
        left_classes=non_obf_classes,
        right_classes=obf_classes,
    )
    non_obf_vectors = _build_weighted_vectors(
        classes=non_obf_classes,
        callees_by_cls=non_obf_callees_by_cls,
        vocabulary=vocabulary,
        weight_by_callee=weight_by_callee,
    )
    obf_vectors = _build_weighted_vectors(
        classes=obf_classes,
        callees_by_cls=obf_callees_by_cls,
        vocabulary=vocabulary,
        weight_by_callee=weight_by_callee,
    )
    affinity = non_obf_vectors @ obf_vectors.T
    applicable_mask = (non_obf_vectors.any(axis=1)[:, None]) & (obf_vectors.any(axis=1)[None, :])
    return AffinityResult(affinity, applicable_mask)


def _collect_callees_by_cls(access_trace: AccessTraceDocument) -> dict[str, Counter[str]]:
    """Read callees from traces because older signature overrides omit them."""
    callees_by_cls: dict[str, Counter[str]] = {}
    for traced_function in access_trace.functions_by_address.values():
        stable_callees = traced_function.stable_callees
        if not stable_callees:
            continue
        touched_classes = {
            access_entry.cls for access_entry in traced_function.access_infos if access_entry.cls
        }
        for message_cls in touched_classes:
            callees_by_cls.setdefault(message_cls, Counter()).update(stable_callees)
    return callees_by_cls


def _build_shared_vocabulary(
    *,
    left_callees_by_cls: dict[str, Counter[str]],
    right_callees_by_cls: dict[str, Counter[str]],
    left_classes: list[str],
    right_classes: list[str],
) -> tuple[str, ...]:
    left_document_frequency = _document_frequency(left_callees_by_cls, left_classes)
    right_document_frequency = _document_frequency(right_callees_by_cls, right_classes)
    return tuple(sorted(left_document_frequency.keys() & right_document_frequency.keys()))


def _document_frequency(callees_by_cls: dict[str, Counter[str]], classes: list[str]) -> Counter[str]:
    document_frequency: Counter[str] = Counter()
    for message_cls in classes:
        document_frequency.update(callees_by_cls.get(message_cls, Counter()).keys())
    return document_frequency


def _build_inverse_frequency_weights(
    *,
    vocabulary: tuple[str, ...],
    left_callees_by_cls: dict[str, Counter[str]],
    right_callees_by_cls: dict[str, Counter[str]],
    left_classes: list[str],
    right_classes: list[str],
) -> dict[str, float]:
    """Average rarity across both builds to keep scores symmetric."""
    left_document_frequency = _document_frequency(left_callees_by_cls, left_classes)
    right_document_frequency = _document_frequency(right_callees_by_cls, right_classes)
    left_total = max(len(left_classes), 1)
    right_total = max(len(right_classes), 1)
    return {
        callee: log(
            2.0
            / (
                left_document_frequency[callee] / left_total
                + right_document_frequency[callee] / right_total
                + _SMOOTHING
            )
        )
        for callee in vocabulary
    }


def _build_weighted_vectors(
    *,
    classes: list[str],
    callees_by_cls: dict[str, Counter[str]],
    vocabulary: tuple[str, ...],
    weight_by_callee: dict[str, float],
) -> np.ndarray:
    column_by_callee = {callee: column for column, callee in enumerate(vocabulary)}
    vectors = np.zeros((len(classes), len(vocabulary)))
    for row, message_cls in enumerate(classes):
        for callee, count in callees_by_cls.get(message_cls, Counter()).items():
            column = column_by_callee.get(callee)
            if column is None:
                continue
            # Sublinear counts reduce sensitivity to inlining changes across builds.
            vectors[row, column] = (1.0 + log(count)) * weight_by_callee[callee]
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return np.divide(vectors, norms, out=np.zeros_like(vectors), where=norms > 0.0)
