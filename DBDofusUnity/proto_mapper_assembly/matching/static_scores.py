from collections.abc import Mapping, Sequence
from typing import NamedTuple

import numpy as np
from tqdm import tqdm

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.interfaces.matching import MatchingWorkspace, StaticScoreMatrices
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPairsConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.runtime_data import RuntimeInstance
from DBDofusUnity.proto_mapper_assembly.matching.score_constraints import build_prospective_constraint_mask
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore
from DBDofusUnity.proto_mapper_assembly.scoring.message_scoring import (
    StructureSimilarityContext,
    build_structure_hardening,
    compute_message_similarity,
    deep_structure_score,
    shallow_structure_score,
)

_OBVIOUS_INCOMPATIBILITY_MIN_FIELD_COUNT = 4
_MIN_STRUCTURE_SIMILARITY = 0.5

_ROOT_MESSAGE_NAME_SUFFIXES = ("Request", "Response", "Event")
_SERVER_MESSAGE_NAME_SUFFIXES = ("Response", "Event")


class _ObfGateInputs(NamedTuple):
    message_cls: str
    observed_instance: RuntimeInstance | None
    pinned_non_obf_cls: str | None
    declared_field_count: int
    top_level_declared_field_shapes: frozenset[FieldCategoryEnum]


class _NonObfGateInputs(NamedTuple):
    message_cls: str
    is_game_msg: bool
    is_root_msg_name: bool
    is_from_server_name: bool
    pinned_obf_cls: str | None
    declared_field_count: int
    top_level_declared_field_shapes: frozenset[FieldCategoryEnum]


class _NonObfCandidate(NamedTuple):
    non_obf_index: int
    signature: MessageAccessSignature
    gate_inputs: _NonObfGateInputs


def build_static_score_data(
    *,
    obf_signatures: Sequence[MessageAccessSignature],
    non_obf_signatures: Sequence[MessageAccessSignature],
    pinned_pairs_config: PinnedPairsConfig,
    runtime_data_store: RuntimeDataStore,
    structure_context: StructureSimilarityContext,
) -> StaticScoreMatrices:
    structure_scores_matrix = np.zeros((len(non_obf_signatures), len(obf_signatures)))
    assembly_scores_matrix = np.zeros((len(non_obf_signatures), len(obf_signatures)))
    static_scores_matrix = np.zeros((len(non_obf_signatures), len(obf_signatures)))

    non_obf_candidates_by_root: dict[bool, list[_NonObfCandidate]] = {True: [], False: []}
    for non_obf_index, non_obf_signature in enumerate(non_obf_signatures):
        non_obf_candidates_by_root[non_obf_signature.dump_cs_msg.is_root_msg].append(
            _NonObfCandidate(
                non_obf_index=non_obf_index,
                signature=non_obf_signature,
                gate_inputs=_build_non_obf_gate_inputs(non_obf_signature, pinned_pairs_config),
            )
        )

    for obf_index, obf_signature in enumerate(tqdm(obf_signatures, "build static score matrix")):
        obf_gate_inputs = _build_obf_gate_inputs(obf_signature, pinned_pairs_config, runtime_data_store)
        is_pinned_obf = obf_gate_inputs.pinned_non_obf_cls is not None
        for non_obf_candidate in non_obf_candidates_by_root[obf_signature.dump_cs_msg.is_root_msg]:
            if _are_gate_inputs_obviously_incompatible(obf_gate_inputs, non_obf_candidate.gate_inputs):
                continue

            non_obf_index = non_obf_candidate.non_obf_index
            non_obf_signature = non_obf_candidate.signature
            hardening = build_structure_hardening(obf_signature, non_obf_signature)

            structure_similarity = hardening.apply(shallow_structure_score(obf_signature, non_obf_signature))
            if structure_similarity < _MIN_STRUCTURE_SIMILARITY and not is_pinned_obf:
                structure_scores_matrix[non_obf_index, obf_index] = structure_similarity
                continue

            structure_similarity = hardening.apply(
                deep_structure_score(obf_signature, non_obf_signature, context=structure_context)
            )
            if structure_similarity < _MIN_STRUCTURE_SIMILARITY and not is_pinned_obf:
                structure_scores_matrix[non_obf_index, obf_index] = structure_similarity
                continue
            structure_scores_matrix[non_obf_index, obf_index] = structure_similarity
            pair_score = compute_message_similarity(
                obf_signature, non_obf_signature, structure_score=structure_similarity
            )
            assembly_scores_matrix[non_obf_index, obf_index] = (
                pair_score.assembly_sim_data.assembly_similarity
            )
            static_scores_matrix[non_obf_index, obf_index] = pair_score.static_similarity
    _apply_pinned_pair_score_overrides(
        scores_matrix=static_scores_matrix,
        obf_index_by_cls={signature.message_cls: index for index, signature in enumerate(obf_signatures)},
        non_obf_index_by_cls={
            signature.message_cls: index for index, signature in enumerate(non_obf_signatures)
        },
        pinned_pairs_config=pinned_pairs_config,
    )
    return StaticScoreMatrices(
        structure_scores_matrix=structure_scores_matrix,
        assembly_scores_matrix=assembly_scores_matrix,
        static_scores_matrix=static_scores_matrix,
    )


def _build_obf_gate_inputs(
    obf_signature: MessageAccessSignature,
    pinned_pairs_config: PinnedPairsConfig,
    runtime_data_store: RuntimeDataStore,
) -> _ObfGateInputs:
    pinned_pair = pinned_pairs_config.pinned_pair_msg_by_obf.get(obf_signature.message_cls)
    observed_instances = runtime_data_store.content_by_name.root.get(obf_signature.message_cls, ())
    return _ObfGateInputs(
        message_cls=obf_signature.message_cls,
        observed_instance=next(iter(observed_instances), None),
        pinned_non_obf_cls=pinned_pair.non_obf if pinned_pair is not None else None,
        declared_field_count=obf_signature.declared_field_count,
        top_level_declared_field_shapes=obf_signature.top_level_declared_field_shapes,
    )


def _build_non_obf_gate_inputs(
    non_obf_signature: MessageAccessSignature,
    pinned_pairs_config: PinnedPairsConfig,
) -> _NonObfGateInputs:
    message_name = non_obf_signature.dump_cs_msg.name
    pinned_pair = pinned_pairs_config.pinned_pair_msg_by_non_obf.get(non_obf_signature.message_cls)
    return _NonObfGateInputs(
        message_cls=non_obf_signature.message_cls,
        is_game_msg=message_name in {"Message", "GameMessage"},
        is_root_msg_name=any(
            message_name.endswith(suffix) and len(message_name) > len(suffix)
            for suffix in _ROOT_MESSAGE_NAME_SUFFIXES
        ),
        is_from_server_name=non_obf_signature.message_cls.endswith(_SERVER_MESSAGE_NAME_SUFFIXES),
        pinned_obf_cls=pinned_pair.obf if pinned_pair is not None else None,
        declared_field_count=non_obf_signature.declared_field_count,
        top_level_declared_field_shapes=non_obf_signature.top_level_declared_field_shapes,
    )


def _apply_pinned_pair_score_overrides(
    *,
    scores_matrix: np.ndarray,
    obf_index_by_cls: Mapping[str, int],
    non_obf_index_by_cls: Mapping[str, int],
    pinned_pairs_config: PinnedPairsConfig,
) -> None:
    for pinned_pair in pinned_pairs_config.pairs:
        obf_index = obf_index_by_cls.get(pinned_pair.obf)
        non_obf_index = non_obf_index_by_cls.get(pinned_pair.non_obf)
        if obf_index is None or non_obf_index is None:
            continue

        scores_matrix[:, obf_index] = 0.0
        scores_matrix[non_obf_index, :] = 0.0
        scores_matrix[non_obf_index, obf_index] = 1.0


def apply_pinned_pair_overrides_around_prospective_mask(
    *,
    workspace: MatchingWorkspace,
    scores_matrix: np.ndarray,
    pinned_pairs_config: PinnedPairsConfig,
) -> np.ndarray:
    _apply_pinned_pair_score_overrides(
        scores_matrix=scores_matrix,
        obf_index_by_cls=workspace.signature_indexes.obf_index_by_cls,
        non_obf_index_by_cls=workspace.signature_indexes.non_obf_index_by_cls,
        pinned_pairs_config=pinned_pairs_config,
    )
    prospective_mask = build_prospective_constraint_mask(
        workspace=workspace,
        base_scores_matrix=scores_matrix,
    )
    masked_scores_matrix = scores_matrix * prospective_mask
    _apply_pinned_pair_score_overrides(
        scores_matrix=masked_scores_matrix,
        obf_index_by_cls=workspace.signature_indexes.obf_index_by_cls,
        non_obf_index_by_cls=workspace.signature_indexes.non_obf_index_by_cls,
        pinned_pairs_config=pinned_pairs_config,
    )
    return masked_scores_matrix


def _are_gate_inputs_obviously_incompatible(
    obf: _ObfGateInputs,
    non_obf: _NonObfGateInputs,
) -> bool:
    observed_instance = obf.observed_instance
    if observed_instance:
        if non_obf.is_game_msg != observed_instance.is_game_msg:
            return True
        if non_obf.is_game_msg:
            return False

        if non_obf.is_root_msg_name != observed_instance.is_root_msg:
            return True

        if non_obf.is_root_msg_name and non_obf.is_from_server_name != observed_instance.from_server:
            return True

    if obf.pinned_non_obf_cls is not None:
        return obf.pinned_non_obf_cls != non_obf.message_cls

    if non_obf.pinned_obf_cls is not None:
        return non_obf.pinned_obf_cls != obf.message_cls

    if obf.declared_field_count == 0 or non_obf.declared_field_count == 0:
        return False

    obf_count = obf.declared_field_count
    non_obf_count = non_obf.declared_field_count
    smaller_count = min(obf_count, non_obf_count)
    larger_count = max(obf_count, non_obf_count)
    if smaller_count >= _OBVIOUS_INCOMPATIBILITY_MIN_FIELD_COUNT and larger_count >= (smaller_count * 3):
        return True

    return bool(
        obf.top_level_declared_field_shapes
        and non_obf.top_level_declared_field_shapes
        and obf.top_level_declared_field_shapes.isdisjoint(non_obf.top_level_declared_field_shapes)
    )
