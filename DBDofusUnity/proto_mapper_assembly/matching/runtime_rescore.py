from collections import defaultdict
from collections.abc import Mapping
from typing import NamedTuple

import numpy as np
from tqdm import tqdm

from DBDofusUnity.proto_mapper_assembly.field_mapping.field_mapper import build_field_mapping
from DBDofusUnity.proto_mapper_assembly.interfaces.field_mapping import FieldMappingContext
from DBDofusUnity.proto_mapper_assembly.interfaces.matching import MatchingWorkspace
from DBDofusUnity.proto_mapper_assembly.interfaces.matching_inputs import MatchingInputs, MatchingRunConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair
from DBDofusUnity.proto_mapper_assembly.interfaces.runtime import RuntimeValidationCandidate
from DBDofusUnity.proto_mapper_assembly.matching.score_lookup import build_lazy_score_by_pair_lookup_from_matrix
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_field_validation import (
    build_runtime_field_validator_confidence,
)

_RUNTIME_GUARANTEED_TOP_CANDIDATE_COUNT = 3
_RUNTIME_MAX_CANDIDATE_COUNT = 10
_RUNTIME_MAX_STATIC_SCORE_GAP_FROM_BEST = 0.10
_VALIDATED_RUNTIME_BONUS_RATE = 0.10


class RuntimeCandidateIndexes(NamedTuple):
    non_obf_index: int
    obf_index: int


class RuntimeRescoredScores(NamedTuple):
    scores_matrix: np.ndarray
    runtime_confidence_by_pair: dict[MatchPairKey, float | None]
    rejected_pairs_by_reason: dict[MatchPairKey, str]


def build_runtime_rescored_scores(
    *,
    workspace: MatchingWorkspace,
    inputs: MatchingInputs,
    run_config: MatchingRunConfig,
    scores_matrix: np.ndarray,
) -> RuntimeRescoredScores:
    """Rescore only capture-backed candidates; absent runtime evidence is neutral."""
    rescored_matrix = np.array(scores_matrix, copy=True)
    runtime_confidence_by_pair: dict[MatchPairKey, float | None] = {}
    rejected_pairs_by_reason: dict[MatchPairKey, str] = {}
    candidates_by_non_obf = _build_runtime_candidates_by_non_obf(
        workspace=workspace,
        inputs=inputs,
        run_config=run_config,
        scores_matrix=scores_matrix,
        score_by_pair_lookup=build_lazy_score_by_pair_lookup_from_matrix(
            workspace=workspace, scores_matrix=scores_matrix
        ),
    )
    for candidate_by_obf in tqdm(candidates_by_non_obf.values()):
        for candidate in candidate_by_obf.values():
            runtime_confidence: float | None = build_runtime_field_validator_confidence(
                field_mapping=candidate.field_mapping_result.field_mapping,
                obf_message=inputs.obf_messages_by_cls[candidate.obf_msg_sig.message_cls],
                obf_messages_by_cls=inputs.obf_messages_by_cls,
                non_obf_message=inputs.non_obf_messages_by_cls[candidate.non_obf_msg_sig.message_cls],
                validated_non_obf_field_names={
                    field.clean_field_name for field in candidate.non_obf_msg_sig.get_exportable_fields()
                },
                runtime_data_store=run_config.runtime_data_store,
            )
            pair_key = MatchPairKey(candidate.obf_msg_sig.message_cls, candidate.non_obf_msg_sig.message_cls)
            if candidate.field_mapping_result.has_validation_failure:
                runtime_confidence = 0.0
                rejected_pairs_by_reason[pair_key] = "runtime_field_validation"

            rescored_matrix[candidate.non_obf_index, candidate.obf_index] = _apply_runtime_confidence_score(
                static_similarity=float(scores_matrix[candidate.non_obf_index, candidate.obf_index]),
                runtime_confidence=runtime_confidence,
            )
            runtime_confidence_by_pair[pair_key] = runtime_confidence
    return RuntimeRescoredScores(rescored_matrix, runtime_confidence_by_pair, rejected_pairs_by_reason)


def _build_runtime_candidates_by_non_obf(
    *,
    workspace: MatchingWorkspace,
    inputs: MatchingInputs,
    run_config: MatchingRunConfig,
    scores_matrix: np.ndarray,
    score_by_pair_lookup: Mapping[MatchPairKey, float],
) -> dict[str, dict[str, RuntimeValidationCandidate]]:
    candidates_by_non_obf: dict[str, dict[str, RuntimeValidationCandidate]] = defaultdict(dict)
    obf_signatures = workspace.obf_signatures
    non_obf_signatures = workspace.non_obf_signatures
    runtime_candidate_indexes = _iter_runtime_candidate_indexes(scores_matrix)
    for non_obf_index, obf_index in tqdm(runtime_candidate_indexes, total=len(runtime_candidate_indexes)):
        obf_signature = obf_signatures[obf_index]
        non_obf_signature = non_obf_signatures[non_obf_index]

        pinned_by_obf = run_config.pinned_pairs_config.pinned_pair_msg_by_obf
        if obf_signature.message_cls in pinned_by_obf:
            pinned_pair = pinned_by_obf[obf_signature.message_cls]
            assert pinned_pair.non_obf == non_obf_signature.message_cls
        else:
            assert (
                non_obf_signature.message_cls not in run_config.pinned_pairs_config.pinned_pair_msg_by_non_obf
            )
            pinned_pair = None

        candidates_by_non_obf[non_obf_signature.message_cls][obf_signature.message_cls] = (
            _build_runtime_validation_candidate(
                workspace=workspace,
                inputs=inputs,
                run_config=run_config,
                score_by_pair_lookup=score_by_pair_lookup,
                pinned_pair=pinned_pair,
                obf_message_cls=obf_signature.message_cls,
                non_obf_message_cls=non_obf_signature.message_cls,
                non_obf_index=non_obf_index,
                obf_index=obf_index,
            )
        )

    return candidates_by_non_obf


def _iter_runtime_candidate_indexes(
    scores_matrix: np.ndarray,
) -> tuple[RuntimeCandidateIndexes, ...]:
    candidate_indexes: list[RuntimeCandidateIndexes] = []
    for obf_index in range(scores_matrix.shape[1]):
        obf_scores = scores_matrix[:, obf_index]
        best_score = float(obf_scores.max())
        if best_score <= 0.0:
            continue
        ranked_non_obf_indexes = np.argsort(obf_scores)[::-1]
        for candidate_rank, non_obf_index_value in enumerate(
            ranked_non_obf_indexes[:_RUNTIME_MAX_CANDIDATE_COUNT]
        ):
            non_obf_index = int(non_obf_index_value)
            candidate_score = float(obf_scores[non_obf_index])
            if candidate_score <= 0.0:
                continue
            if (
                candidate_rank >= _RUNTIME_GUARANTEED_TOP_CANDIDATE_COUNT
                and candidate_score < best_score - _RUNTIME_MAX_STATIC_SCORE_GAP_FROM_BEST
            ):
                continue
            candidate_indexes.append(RuntimeCandidateIndexes(non_obf_index, obf_index))
    return tuple(candidate_indexes)


def _apply_runtime_confidence_score(*, static_similarity: float, runtime_confidence: float | None) -> float:
    if runtime_confidence is None:
        return static_similarity
    if runtime_confidence <= 0.0:
        return 0.0
    return static_similarity * (1.0 + runtime_confidence * _VALIDATED_RUNTIME_BONUS_RATE)


def _build_runtime_validation_candidate(
    *,
    workspace: MatchingWorkspace,
    inputs: MatchingInputs,
    run_config: MatchingRunConfig,
    score_by_pair_lookup: Mapping[MatchPairKey, float],
    pinned_pair: PinnedPair | None,
    obf_message_cls: str,
    non_obf_message_cls: str,
    obf_index: int,
    non_obf_index: int,
) -> RuntimeValidationCandidate:
    field_mapping_result = build_field_mapping(
        non_obf_signature=workspace.non_obf_signatures_by_cls[non_obf_message_cls],
        obf_signature=workspace.obf_signatures_by_cls[obf_message_cls],
        non_obf_messages_by_cls=inputs.non_obf_messages_by_cls,
        obf_messages_by_cls=inputs.obf_messages_by_cls,
        field_mapping_context=FieldMappingContext(
            score_by_pair=score_by_pair_lookup,
            runtime_data_store=run_config.runtime_data_store,
            signature_overrides_by_non_obf_cls=inputs.signature_overrides_by_non_obf_cls,
            obf_enum_signatures_by_name=inputs.obf_enum_signatures_by_name,
            non_obf_enum_signatures_by_name=inputs.non_obf_enum_signatures_by_name,
            obf_access_trace=inputs.obf_access_trace,
            non_obf_access_trace=inputs.non_obf_access_trace,
        ),
        obf_type_index=workspace.obf_type_index,
        non_obf_type_index=workspace.non_obf_type_index,
        pinned_pair=pinned_pair,
    )
    return RuntimeValidationCandidate(
        non_obf_msg_sig=workspace.non_obf_signatures_by_cls[non_obf_message_cls],
        obf_msg_sig=workspace.obf_signatures_by_cls[obf_message_cls],
        field_mapping_result=field_mapping_result,
        obf_index=obf_index,
        non_obf_index=non_obf_index,
    )
