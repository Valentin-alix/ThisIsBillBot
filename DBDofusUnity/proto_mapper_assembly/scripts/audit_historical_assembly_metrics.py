from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
from itertools import pairwise
from pathlib import Path
from typing import Literal

from consts import (
    GAME_MAPPINGS_JSON_FILE,
    NON_OBF_GAME_DIR,
    NON_OBF_PROTO_ACCESSES_FILE,
    NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    OBF_GAME_SNAPSHOTS_DIR,
    OBF_PROTO_ACCESSES_FILE,
    OBF_PROTOCOL_GAME_DUMP_CS_FILE,
)

from proto_mapper_assembly.controllers.access_signatures import (
    build_message_access_signatures_from_trace,
    count_handler_registrations_by_cls,
)
from proto_mapper_assembly.controllers.message_lookup import (
    build_non_obf_alias_lookup,
    build_obf_alias_lookup,
)
from proto_mapper_assembly.helpers.archived_builds import (
    GAME_MAPPINGS_RELATIVE_PATH,
    NON_OBF_PROTO_ACCESSES_RELATIVE_PATH,
    NON_OBF_PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH,
    PROTO_ACCESSES_RELATIVE_PATH,
    PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH,
    iter_archived_build_dirs,
)
from proto_mapper_assembly.interfaces.assembly_access import (
    AccessAtomKey,
    AccessAtomSequenceKey,
    AccessTraceDocument,
    FieldAccessSignatures,
    MessageAccessSignature,
)
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from proto_mapper_assembly.interfaces.function_access_signature import FunctionSimilarityKey
from proto_mapper_assembly.interfaces.game_mappings import SimpleGameMappingsDocument
from proto_mapper_assembly.parsers.dump_cs_parser import parse_messages
from proto_mapper_assembly.scoring.primitives import (
    counter_overlap_similarity,
    counter_profile_overlap_similarity,
    get_average_best_similarity_sequences,
    ratio_similarity,
)
from proto_mapper_assembly.scoring.signature_scoring import access_atom_sequence_similarity

_WORKING_SET_VERSION_ID = "working_set"
_MINIMUM_SNAPSHOT_COUNT = 2
_WEAK_STABILITY_P10_THRESHOLD = 0.35
_WEAK_STABILITY_MEAN_THRESHOLD = 0.55
_WEAK_MARGIN_THRESHOLD = 0.05
_HIGH_COLLISION_THRESHOLD = 0.35
_NEAR_CONSTANT_COLLISION_THRESHOLD = 0.95
"""Above this, a metric scores almost every wrong pair at least as high as the right one."""

_NEAR_CONSTANT_MARGIN_THRESHOLD = 0.05
_LOW_TOP1_THRESHOLD = 0.30

type JsonScalar = float | int | str | None
type JsonObject = dict[str, JsonScalar | list["JsonObject"] | list[str]]


@dataclass(frozen=True)
class NonObfReference:
    """The non-obfuscated side of one comparison, either archived with a build or substituted."""

    proto_accesses_path: Path
    dump_cs_path: Path

    @property
    def missing_paths(self) -> tuple[Path, ...]:
        return tuple(path for path in (self.proto_accesses_path, self.dump_cs_path) if not path.is_file())


@dataclass(frozen=True)
class VersionSource:
    """One candidate build, before its artifacts have been checked."""

    version_id: str
    obf_proto_accesses_path: Path
    obf_dump_cs_path: Path
    game_mappings_path: Path
    non_obf: NonObfReference | None
    """``None`` when the build archived no reference side, which sends it to the fallback."""

    @property
    def missing_obf_paths(self) -> tuple[Path, ...]:
        return tuple(
            relative_path
            for relative_path, path in (
                (PROTO_ACCESSES_RELATIVE_PATH, self.obf_proto_accesses_path),
                (PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH, self.obf_dump_cs_path),
                (GAME_MAPPINGS_RELATIVE_PATH, self.game_mappings_path),
            )
            if not path.is_file()
        )


@dataclass(frozen=True)
class VersionHead:
    version_id: str
    """Name of the build directory, e.g. ``21_07_2026``."""

    obf_proto_accesses_path: Path
    obf_dump_cs_path: Path
    game_mappings_path: Path
    non_obf_proto_accesses_path: Path
    non_obf_dump_cs_path: Path
    non_obf_source: Literal["snapshot", "fallback"]
    version_hash: str
    mapped_message_count: int


@dataclass(frozen=True)
class VersionSnapshot:
    head: VersionHead
    mapping_by_non_obf_cls: dict[str, str]
    obf_signatures_by_cls: dict[str, MessageAccessSignature]
    non_obf_signatures_by_cls: dict[str, MessageAccessSignature]
    obf_registration_count_by_cls: dict[str, int]
    non_obf_registration_count_by_cls: dict[str, int]


@dataclass(frozen=True)
class IncompleteVersion:
    version_id: str
    missing_paths: tuple[Path, ...]


@dataclass(frozen=True)
class VersionCollectionResult:
    version_heads: list[VersionHead]
    incomplete_versions: list[IncompleteVersion]


@dataclass(frozen=True)
class MetricSample:
    metric_name: str
    score: float
    true_score: float | None = None
    best_false_score: float | None = None
    true_rank: int | None = None
    candidate_count: int | None = None


@dataclass(frozen=True)
class MetricSummary:
    metric_name: str
    sample_count: int
    coverage_ratio: float
    mean_score: float
    p10_score: float
    p50_score: float
    p90_score: float
    mean_margin: float | None
    top1_accuracy: float | None
    mean_rank: float | None
    collision_ratio: float | None


type MessageMetric = Callable[[MessageAccessSignature, MessageAccessSignature], float]
type FunctionMetric = Callable[[FunctionSimilarityKey, FunctionSimilarityKey], float]
type FieldMetric = Callable[[FieldAccessSignatures, FieldAccessSignatures], float]


def main() -> None:
    args = _build_argument_parser().parse_args()
    snapshots_root = args.snapshots_root.resolve()
    non_obf_dir: Path | None = args.non_obf_dir
    non_obf_fallback = (
        NonObfReference(
            proto_accesses_path=non_obf_dir / PROTO_ACCESSES_RELATIVE_PATH,
            dump_cs_path=non_obf_dir / PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH,
        )
        if non_obf_dir is not None
        else _default_non_obf_reference()
    )
    collection_result = _collect_version_heads(
        snapshots_root=snapshots_root,
        non_obf_game_dir=NON_OBF_GAME_DIR,
        non_obf_fallback=non_obf_fallback,
        force_non_obf_fallback=non_obf_dir is not None,
        extra_sources=() if args.no_working_set else (_build_working_set_source(),),
    )
    version_heads = collection_result.version_heads
    if args.max_versions is not None:
        version_heads = version_heads[: args.max_versions]

    print(f"snapshots root: {snapshots_root}")
    print(f"usable version groups: {len(version_heads)}")
    print(f"incomplete build directories skipped: {len(collection_result.incomplete_versions)}")
    for incomplete_version in collection_result.incomplete_versions:
        missing = ", ".join(str(path) for path in incomplete_version.missing_paths)
        print(f"  - {incomplete_version.version_id}: missing {missing}")
    if len(version_heads) < _MINIMUM_SNAPSHOT_COUNT:
        error_message = (
            f"Need at least {_MINIMUM_SNAPSHOT_COUNT} complete build directories under "
            f"{snapshots_root} to compare stability across versions. Re-run the IDA tracer and the "
            "mapper on the directories listed above, or archive a new build."
        )
        raise SystemExit(error_message)
    print("loading snapshots...")
    snapshots = [_load_version_snapshot(version_head) for version_head in version_heads]

    stability_samples = _collect_stability_samples(snapshots)
    discriminative_samples = _collect_discriminative_samples(
        snapshots=snapshots,
        max_candidates_per_message=args.max_candidates_per_message,
    )
    summaries = _summarize_samples(stability_samples, discriminative_samples)
    recommendations = _build_recommendations(summaries)
    payload: JsonObject = {
        "versions": [
            {
                "version_id": snapshot.head.version_id,
                "version_hash": snapshot.head.version_hash,
                "mapped_message_count": snapshot.head.mapped_message_count,
                "resolved_message_count": len(snapshot.mapping_by_non_obf_cls),
                "non_obf_source": snapshot.head.non_obf_source,
            }
            for snapshot in snapshots
        ],
        "stability": _serialize_samples(stability_samples),
        "discrimination": _serialize_samples(discriminative_samples),
        "summary": _serialize_summaries(summaries),
        "recommendations": list(recommendations),
    }

    _print_report(snapshots, summaries, recommendations)
    if args.json_output is not None:
        args.json_output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        print(f"\njson output: {args.json_output}")


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit assembly-access metrics across archived game builds.")
    parser.add_argument(
        "--snapshots-root",
        type=Path,
        default=OBF_GAME_SNAPSHOTS_DIR,
        help="Directory holding one sub-directory per archived obfuscated build.",
    )
    parser.add_argument(
        "--max-versions",
        type=int,
        help="Limit newest detected obfuscation-version groups for faster local runs.",
    )
    parser.add_argument(
        "--max-candidates-per-message",
        type=int,
        default=None,
        help=(
            "Optional deterministic candidate cap per non-obf message. "
            "Unset means full candidate set for exact ranks."
        ),
    )
    parser.add_argument(
        "--non-obf-dir",
        type=Path,
        default=None,
        help=(
            "Force this non-obfuscated reference for every build, ignoring any archived beside "
            "them. Recommended: holding the reference fixed leaves the obfuscated build as the "
            "only thing that changed between two snapshots."
        ),
    )
    parser.add_argument(
        "--no-working-set",
        action="store_true",
        default=False,
        help="Audit only archived builds, leaving out the one currently loaded in datas/.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=None,
        help="Optional path for detailed JSON output.",
    )
    return parser


def _default_non_obf_reference() -> NonObfReference:
    """The live reference side, used whenever a build archived none of its own."""
    return NonObfReference(
        proto_accesses_path=NON_OBF_PROTO_ACCESSES_FILE,
        dump_cs_path=NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    )


def _build_working_set_source() -> VersionSource:
    """
    The build currently loaded in the repository, which no snapshot directory describes.

    It lives in ``datas/`` with no ``GameAssembly.dll`` beside it, so ``_iter_version_dirs`` can
    never find it, yet it is the most recent comparison point available and the one the next
    game update will be measured against.
    """
    return VersionSource(
        version_id=_WORKING_SET_VERSION_ID,
        obf_proto_accesses_path=OBF_PROTO_ACCESSES_FILE,
        obf_dump_cs_path=OBF_PROTOCOL_GAME_DUMP_CS_FILE,
        game_mappings_path=GAME_MAPPINGS_JSON_FILE,
        non_obf=_default_non_obf_reference(),
    )


def _build_snapshot_source(version_dir: Path) -> VersionSource:
    archived_non_obf = NonObfReference(
        proto_accesses_path=version_dir / NON_OBF_PROTO_ACCESSES_RELATIVE_PATH,
        dump_cs_path=version_dir / NON_OBF_PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH,
    )
    return VersionSource(
        version_id=version_dir.name,
        obf_proto_accesses_path=version_dir / PROTO_ACCESSES_RELATIVE_PATH,
        obf_dump_cs_path=version_dir / PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH,
        game_mappings_path=version_dir / GAME_MAPPINGS_RELATIVE_PATH,
        non_obf=None if archived_non_obf.missing_paths else archived_non_obf,
    )


def _collect_version_heads(
    *,
    snapshots_root: Path,
    non_obf_game_dir: Path,
    non_obf_fallback: NonObfReference | None = None,
    force_non_obf_fallback: bool = False,
    extra_sources: Sequence[VersionSource] = (),
) -> VersionCollectionResult:
    """
    Turn candidate builds into comparable heads, newest first.

    A build qualifies on its obfuscated artifacts alone. The reference side is substitutable:
    most archived builds predate the habit of copying it next to them, and comparing every build
    against one reference is in fact the sharper measurement, since it removes the reference from
    the list of things that changed between two snapshots.
    """
    resolved_fallback = non_obf_fallback if non_obf_fallback is not None else _default_non_obf_reference()
    version_heads: list[VersionHead] = []
    incomplete_versions: list[IncompleteVersion] = []
    seen_version_hashes: set[str] = set()
    snapshot_sources = [
        _build_snapshot_source(version_dir)
        for version_dir in _iter_version_dirs(
            snapshots_root=snapshots_root, non_obf_game_dir=non_obf_game_dir
        )
    ]
    for source in (*extra_sources, *snapshot_sources):
        missing_paths = source.missing_obf_paths
        if missing_paths:
            incomplete_versions.append(
                IncompleteVersion(version_id=source.version_id, missing_paths=missing_paths)
            )
            continue

        archived_non_obf = None if force_non_obf_fallback else source.non_obf
        non_obf = archived_non_obf if archived_non_obf is not None else resolved_fallback
        non_obf_missing = non_obf.missing_paths
        if non_obf_missing:
            incomplete_versions.append(
                IncompleteVersion(version_id=source.version_id, missing_paths=non_obf_missing)
            )
            continue

        # The obf dump is what obfuscation actually reshuffles, so two sources sharing it describe
        # the same build and must not be compared against each other.
        version_hash = sha256(source.obf_dump_cs_path.read_bytes()).hexdigest()
        if version_hash in seen_version_hashes:
            continue
        seen_version_hashes.add(version_hash)
        mappings = SimpleGameMappingsDocument.model_validate_json(source.game_mappings_path.read_bytes()).root
        version_heads.append(
            VersionHead(
                version_id=source.version_id,
                obf_proto_accesses_path=source.obf_proto_accesses_path,
                obf_dump_cs_path=source.obf_dump_cs_path,
                game_mappings_path=source.game_mappings_path,
                non_obf_proto_accesses_path=non_obf.proto_accesses_path,
                non_obf_dump_cs_path=non_obf.dump_cs_path,
                non_obf_source="snapshot" if archived_non_obf is not None else "fallback",
                version_hash=version_hash,
                mapped_message_count=len(mappings),
            )
        )
    return VersionCollectionResult(
        version_heads=version_heads,
        incomplete_versions=incomplete_versions,
    )


def _iter_version_dirs(*, snapshots_root: Path, non_obf_game_dir: Path) -> list[Path]:
    """List the obfuscated build directories, newest first.

    ``_collect_stability_samples`` pairs consecutive snapshots, so the ordering matters here.
    """
    return iter_archived_build_dirs(snapshots_root=snapshots_root, exclude_dir=non_obf_game_dir)


def _load_version_snapshot(version_head: VersionHead) -> VersionSnapshot:
    obf_access_trace = AccessTraceDocument.model_validate_json(
        version_head.obf_proto_accesses_path.read_bytes()
    )
    non_obf_access_trace = AccessTraceDocument.model_validate_json(
        version_head.non_obf_proto_accesses_path.read_bytes()
    )
    obf_messages_by_cls = _parse_messages_by_cls(version_head.obf_dump_cs_path)
    non_obf_messages_by_cls = _parse_messages_by_cls(version_head.non_obf_dump_cs_path)

    mapping_by_non_obf_cls = _build_resolved_mapping_by_non_obf_cls(
        mapping_raw=version_head.game_mappings_path.read_bytes(),
        obf_messages_by_cls=obf_messages_by_cls,
        non_obf_messages_by_cls=non_obf_messages_by_cls,
    )
    obf_signatures_by_cls = build_message_access_signatures_from_trace(
        access_trace=obf_access_trace, messages=list(obf_messages_by_cls.values())
    )
    non_obf_signatures_by_cls = build_message_access_signatures_from_trace(
        access_trace=non_obf_access_trace, messages=list(non_obf_messages_by_cls.values())
    )
    return VersionSnapshot(
        head=version_head,
        mapping_by_non_obf_cls=mapping_by_non_obf_cls,
        obf_signatures_by_cls=obf_signatures_by_cls,
        non_obf_signatures_by_cls=non_obf_signatures_by_cls,
        obf_registration_count_by_cls=count_handler_registrations_by_cls(obf_access_trace),
        non_obf_registration_count_by_cls=count_handler_registrations_by_cls(non_obf_access_trace),
    )


def _parse_messages_by_cls(dump_path: Path) -> dict[str, DumpCSMessage]:
    return {message.composed_name: message for message in parse_messages(str(dump_path))}


def _build_resolved_mapping_by_non_obf_cls(
    *,
    mapping_raw: bytes,
    obf_messages_by_cls: Mapping[str, DumpCSMessage],
    non_obf_messages_by_cls: Mapping[str, DumpCSMessage],
) -> dict[str, str]:
    mappings = SimpleGameMappingsDocument.model_validate_json(mapping_raw).root
    obf_alias_to_cls = build_obf_alias_lookup(obf_messages_by_cls=obf_messages_by_cls)
    non_obf_alias_to_cls, non_obf_short_alias_to_cls = build_non_obf_alias_lookup(
        non_obf_messages_by_cls=non_obf_messages_by_cls
    )
    resolved_mapping: dict[str, str] = {}
    for exported_non_obf_name, mapping_entry in mappings.items():
        non_obf_cls = _resolve_unique_mapping_candidate(
            exported_non_obf_name,
            primary_alias_to_cls=non_obf_alias_to_cls,
            fallback_alias_to_cls=non_obf_short_alias_to_cls,
        )
        obf_cls = _resolve_unique_mapping_candidate(
            mapping_entry.obf_msg_namespace,
            primary_alias_to_cls=obf_alias_to_cls,
            fallback_alias_to_cls={},
        )
        if non_obf_cls is not None and obf_cls is not None:
            resolved_mapping[non_obf_cls] = obf_cls
    return resolved_mapping


def _resolve_unique_mapping_candidate(
    exported_name: str,
    *,
    primary_alias_to_cls: Mapping[str, frozenset[str]],
    fallback_alias_to_cls: Mapping[str, frozenset[str]],
) -> str | None:
    candidates = primary_alias_to_cls.get(exported_name)
    if not candidates:
        candidates = fallback_alias_to_cls.get(exported_name.rsplit(".", 1)[-1])
    if not candidates or len(candidates) != 1:
        return None
    return next(iter(candidates))


def _collect_stability_samples(snapshots: Sequence[VersionSnapshot]) -> list[MetricSample]:
    samples: list[MetricSample] = []
    for newer_snapshot, older_snapshot in pairwise(snapshots):
        shared_non_obf_messages = (
            newer_snapshot.mapping_by_non_obf_cls.keys() & older_snapshot.mapping_by_non_obf_cls.keys()
        )
        for non_obf_cls in shared_non_obf_messages:
            newer_obf_cls = newer_snapshot.mapping_by_non_obf_cls[non_obf_cls]
            older_obf_cls = older_snapshot.mapping_by_non_obf_cls[non_obf_cls]
            newer_signature = newer_snapshot.obf_signatures_by_cls.get(newer_obf_cls)
            older_signature = older_snapshot.obf_signatures_by_cls.get(older_obf_cls)
            if newer_signature is None or older_signature is None:
                continue
            metric_by_name = _build_message_metrics(
                left_registration_count_by_cls=newer_snapshot.obf_registration_count_by_cls,
                right_registration_count_by_cls=older_snapshot.obf_registration_count_by_cls,
            )
            for metric_name, scorer in metric_by_name.items():
                samples.append(
                    MetricSample(
                        metric_name=metric_name,
                        score=scorer(newer_signature, older_signature),
                    )
                )
    return samples


def _collect_discriminative_samples(
    *,
    snapshots: Sequence[VersionSnapshot],
    max_candidates_per_message: int | None,
) -> list[MetricSample]:
    samples: list[MetricSample] = []
    for snapshot in snapshots:
        metric_by_name = _build_message_metrics(
            left_registration_count_by_cls=snapshot.obf_registration_count_by_cls,
            right_registration_count_by_cls=snapshot.non_obf_registration_count_by_cls,
        )
        obf_candidates = list(snapshot.obf_signatures_by_cls.values())
        for non_obf_cls, true_obf_cls in snapshot.mapping_by_non_obf_cls.items():
            non_obf_signature = snapshot.non_obf_signatures_by_cls.get(non_obf_cls)
            true_obf_signature = snapshot.obf_signatures_by_cls.get(true_obf_cls)
            if non_obf_signature is None or true_obf_signature is None:
                continue
            candidates = _build_candidate_subset(
                true_obf_signature=true_obf_signature,
                obf_candidates=obf_candidates,
                max_candidates_per_message=max_candidates_per_message,
            )
            for metric_name, scorer in metric_by_name.items():
                scored_candidates = [
                    (scorer(obf_signature, non_obf_signature), obf_signature.message_cls)
                    for obf_signature in candidates
                ]
                scored_candidates.sort(key=lambda score_pair: score_pair[0], reverse=True)
                true_score = scorer(true_obf_signature, non_obf_signature)
                true_rank = 1 + sum(
                    candidate_score > true_score
                    for candidate_score, candidate_cls in scored_candidates
                    if candidate_cls != true_obf_cls
                )
                false_scores = [
                    candidate_score
                    for candidate_score, candidate_cls in scored_candidates
                    if candidate_cls != true_obf_cls
                ]
                best_false_score = max(false_scores) if false_scores else None
                samples.append(
                    MetricSample(
                        metric_name=metric_name,
                        score=true_score,
                        true_score=true_score,
                        best_false_score=best_false_score,
                        true_rank=true_rank,
                        candidate_count=len(candidates),
                    )
                )
    return samples


def _build_candidate_subset(
    *,
    true_obf_signature: MessageAccessSignature,
    obf_candidates: Sequence[MessageAccessSignature],
    max_candidates_per_message: int | None,
) -> list[MessageAccessSignature]:
    compatible_candidates = [
        candidate
        for candidate in obf_candidates
        if candidate.dump_cs_msg.is_root_msg == true_obf_signature.dump_cs_msg.is_root_msg
    ]
    if max_candidates_per_message is None or len(compatible_candidates) <= max_candidates_per_message:
        return compatible_candidates

    ordered_candidates = sorted(
        compatible_candidates,
        key=lambda candidate: (
            candidate.message_cls != true_obf_signature.message_cls,
            abs(candidate.declared_field_count - true_obf_signature.declared_field_count),
            candidate.message_cls,
        ),
    )
    return ordered_candidates[:max_candidates_per_message]


def _build_message_metrics(
    *,
    left_registration_count_by_cls: Mapping[str, int],
    right_registration_count_by_cls: Mapping[str, int],
) -> dict[str, MessageMetric]:
    return {
        "structure_declared_shape_cosine": _structure_declared_shape_similarity,
        "structure_oneof_partition": _structure_oneof_partition_similarity,
        "handler_registration_count": lambda left, right: _handler_registration_count_similarity(
            left,
            right,
            left_registration_count_by_cls=left_registration_count_by_cls,
            right_registration_count_by_cls=right_registration_count_by_cls,
        ),
        "function_access_sequence_indexed": lambda left, right: _average_function_metric(
            left, right, _function_access_sequence_indexed_similarity
        ),
        "function_access_sequence_order": lambda left, right: _average_function_metric(
            left, right, _function_access_sequence_order_similarity
        ),
        "function_opcode_histogram": lambda left, right: _average_function_metric(
            left, right, _function_opcode_histogram_similarity
        ),
        "function_foreign_access_summary": lambda left, right: _average_function_metric(
            left, right, _function_foreign_access_summary_similarity
        ),
        "function_size_ratio": lambda left, right: _average_function_metric(
            left, right, _function_size_ratio_similarity
        ),
        "function_return_role": lambda left, right: _average_function_metric(
            left, right, _function_return_role_similarity
        ),
        "function_takes_message_parameter": lambda left, right: _average_function_metric(
            left, right, _function_takes_message_parameter_similarity
        ),
        "function_stable_callees": lambda left, right: _average_function_metric(
            left, right, _function_stable_callees_similarity
        ),
        "function_cfg_shape": lambda left, right: _average_function_metric(
            left, right, _function_cfg_shape_similarity
        ),
        "field_access_sequence_indexed": lambda left, right: _average_field_metric(
            left, right, _field_access_sequence_indexed_similarity
        ),
        "field_access_sequence_order": lambda left, right: _average_field_metric(
            left, right, _field_access_sequence_order_similarity
        ),
        "field_type_shape": lambda left, right: _average_field_metric(
            left, right, _field_type_shape_similarity
        ),
        "field_offset_ratio": lambda left, right: _average_field_metric(
            left, right, _field_offset_ratio_similarity
        ),
    }


def _structure_declared_shape_similarity(
    left: MessageAccessSignature,
    right: MessageAccessSignature,
) -> float:
    """
    Mirrors ``_declared_shape_similarity``, weighted 0.3 in ``_harden_structure_score``.

    Reimplemented rather than imported because it is private to the scoring module, and because
    the audit must keep measuring the current definition even once that one is changed.
    ``TestMetricsMirrorTheScoringModule`` fails when the two stop agreeing, so the divergence is
    a decision someone makes rather than a drift nobody notices.
    """
    return counter_profile_overlap_similarity(
        left=left.declared_shape_profile, right=right.declared_shape_profile
    )


def _structure_oneof_partition_similarity(
    left: MessageAccessSignature,
    right: MessageAccessSignature,
) -> float:
    """Mirrors ``_oneof_partition_similarity``, the factor scaling every structure score."""
    return get_average_best_similarity_sequences(
        left.dump_cs_msg.oneof_group_sizes,
        right.dump_cs_msg.oneof_group_sizes,
        lambda left_size, right_size: ratio_similarity(
            left_size, right_size, max_value=max(left_size, right_size)
        ),
    )


def _handler_registration_count_similarity(
    left: MessageAccessSignature,
    right: MessageAccessSignature,
    *,
    left_registration_count_by_cls: Mapping[str, int],
    right_registration_count_by_cls: Mapping[str, int],
) -> float:
    """
    Mirrors the ``min/max`` count ratio blended at weight 0.25 in ``score_preparation``.

    A message absent from both traces registers nowhere on either side, which is agreement, so it
    scores 1.0; present on one side only is a genuine disagreement and scores 0.0. That is what
    ``ratio_similarity`` already does with ``None``.
    """
    left_count = left_registration_count_by_cls.get(left.message_cls)
    right_count = right_registration_count_by_cls.get(right.message_cls)
    return ratio_similarity(left_count, right_count, max_value=max(left_count or 0, right_count or 0, 1))


def _average_function_metric(
    left: MessageAccessSignature,
    right: MessageAccessSignature,
    scorer: FunctionMetric,
) -> float:
    return get_average_best_similarity_sequences(
        left.function_similarity_keys,
        right.function_similarity_keys,
        scorer,
    )


def _average_field_metric(
    left: MessageAccessSignature,
    right: MessageAccessSignature,
    scorer: FieldMetric,
) -> float:
    return get_average_best_similarity_sequences(left.field_signatures, right.field_signatures, scorer)


def _function_access_sequence_indexed_similarity(
    left: FunctionSimilarityKey,
    right: FunctionSimilarityKey,
) -> float:
    return access_atom_sequence_similarity(left.self_accesses, right.self_accesses)


def _function_access_sequence_order_similarity(
    left: FunctionSimilarityKey,
    right: FunctionSimilarityKey,
) -> float:
    return _access_atom_sequence_order_similarity(left.self_accesses, right.self_accesses)


def _function_stable_callees_similarity(
    left: FunctionSimilarityKey,
    right: FunctionSimilarityKey,
) -> float:
    return counter_overlap_similarity(
        left_counter=Counter(left.stable_callees),
        right_counter=Counter(right.stable_callees),
    )


def _function_cfg_shape_similarity(
    left: FunctionSimilarityKey,
    right: FunctionSimilarityKey,
) -> float:
    if left.cfg_shape is None or right.cfg_shape is None:
        return 0.0
    ratios = [
        ratio_similarity(left_value, right_value, max_value=max(left_value, right_value, 1))
        for left_value, right_value in zip(left.cfg_shape, right.cfg_shape, strict=True)
    ]
    return sum(ratios) / len(ratios)


def _function_opcode_histogram_similarity(
    left: FunctionSimilarityKey,
    right: FunctionSimilarityKey,
) -> float:
    return counter_overlap_similarity(
        left_counter=Counter(dict(left.opcode_histogram)),
        right_counter=Counter(dict(right.opcode_histogram)),
    )


def _function_foreign_access_summary_similarity(
    left: FunctionSimilarityKey,
    right: FunctionSimilarityKey,
) -> float:
    return counter_overlap_similarity(
        left_counter=Counter(left.foreign_access_summary),
        right_counter=Counter(right.foreign_access_summary),
    )


def _function_size_ratio_similarity(left: FunctionSimilarityKey, right: FunctionSimilarityKey) -> float:
    return ratio_similarity(left.size, right.size, max_value=max(left.size, right.size))


def _function_return_role_similarity(left: FunctionSimilarityKey, right: FunctionSimilarityKey) -> float:
    return 1.0 if left.return_role == right.return_role else 0.0


def _function_takes_message_parameter_similarity(
    left: FunctionSimilarityKey,
    right: FunctionSimilarityKey,
) -> float:
    return 1.0 if left.takes_message_parameter == right.takes_message_parameter else 0.0


def _field_access_sequence_indexed_similarity(
    left: FieldAccessSignatures,
    right: FieldAccessSignatures,
) -> float:
    if left.field_type_shape != right.field_type_shape:
        return 0.0
    return access_atom_sequence_similarity(left.accesses_key, right.accesses_key)


def _field_access_sequence_order_similarity(
    left: FieldAccessSignatures,
    right: FieldAccessSignatures,
) -> float:
    if left.field_type_shape != right.field_type_shape:
        return 0.0
    return _access_atom_sequence_order_similarity(left.accesses_key, right.accesses_key)


def _field_type_shape_similarity(left: FieldAccessSignatures, right: FieldAccessSignatures) -> float:
    return 1.0 if left.field_type_shape == right.field_type_shape else 0.0


def _field_offset_ratio_similarity(left: FieldAccessSignatures, right: FieldAccessSignatures) -> float:
    return ratio_similarity(
        left.field_offset, right.field_offset, max_value=max(left.field_offset, right.field_offset)
    )


def _access_atom_sequence_order_similarity(
    left: AccessAtomSequenceKey,
    right: AccessAtomSequenceKey,
) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0

    shared_length = min(len(left), len(right))
    total_similarity = sum(
        _access_atom_order_similarity(left_access, right_access)
        for left_access, right_access in zip(left[:shared_length], right[:shared_length], strict=True)
    )
    return total_similarity / max(len(left), len(right))


def _access_atom_order_similarity(left: AccessAtomKey, right: AccessAtomKey) -> float:
    if left.entry_type != right.entry_type:
        return 0.0
    if left.field_type_shape != right.field_type_shape:
        return 0.0
    if left.access_kind != right.access_kind:
        return 0.0
    return 1.0


def _summarize_samples(
    stability_samples: Sequence[MetricSample],
    discriminative_samples: Sequence[MetricSample],
) -> list[MetricSummary]:
    all_metric_names = sorted(
        {sample.metric_name for sample in stability_samples}
        | {sample.metric_name for sample in discriminative_samples}
    )
    stability_by_metric = _group_samples_by_metric(stability_samples)
    discrimination_by_metric = _group_samples_by_metric(discriminative_samples)
    summaries: list[MetricSummary] = []
    expected_stability_count = max(len(stability_samples) // max(len(all_metric_names), 1), 1)
    for metric_name in all_metric_names:
        metric_stability_samples = stability_by_metric.get(metric_name, [])
        metric_discriminative_samples = discrimination_by_metric.get(metric_name, [])
        scores = [sample.score for sample in metric_stability_samples]
        margins = [
            sample.true_score - sample.best_false_score
            for sample in metric_discriminative_samples
            if sample.true_score is not None and sample.best_false_score is not None
        ]
        ranks = [sample.true_rank for sample in metric_discriminative_samples if sample.true_rank is not None]
        summaries.append(
            MetricSummary(
                metric_name=metric_name,
                sample_count=len(scores),
                coverage_ratio=len(scores) / expected_stability_count,
                mean_score=_mean(scores),
                p10_score=_percentile(scores, 0.10),
                p50_score=_percentile(scores, 0.50),
                p90_score=_percentile(scores, 0.90),
                mean_margin=_mean(margins) if margins else None,
                top1_accuracy=_mean([1.0 if rank == 1 else 0.0 for rank in ranks]) if ranks else None,
                mean_rank=_mean([float(rank) for rank in ranks]) if ranks else None,
                collision_ratio=_mean([1.0 if margin <= 0.0 else 0.0 for margin in margins])
                if margins
                else None,
            )
        )
    return summaries


def _group_samples_by_metric(samples: Sequence[MetricSample]) -> dict[str, list[MetricSample]]:
    grouped_samples: dict[str, list[MetricSample]] = {}
    for sample in samples:
        grouped_samples.setdefault(sample.metric_name, []).append(sample)
    return grouped_samples


def _mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = round((len(sorted_values) - 1) * fraction)
    return sorted_values[index]


def _build_recommendations(summaries: Sequence[MetricSummary]) -> list[str]:
    """
    Turn the per-metric numbers into verdicts, ordered from most to least damning.

    Stability alone decides nothing. A metric can be perfectly reproducible across builds and still
    be worthless, either because it scores the wrong candidate above the right one, or because it
    says the same thing about every pair; both dilute the signals that do discriminate. Those two
    cases are checked before the older instability rule, which otherwise never fires on a corpus
    where every metric reproduces well.
    """
    recommendations: list[str] = []
    for summary in summaries:
        weak_stability = summary.mean_score < _WEAK_STABILITY_MEAN_THRESHOLD or (
            summary.p10_score < _WEAK_STABILITY_P10_THRESHOLD
            and summary.mean_margin is not None
            and summary.mean_margin < 0.0
        )
        weak_margin = summary.mean_margin is not None and summary.mean_margin < _WEAK_MARGIN_THRESHOLD
        high_collision = (
            summary.collision_ratio is not None and summary.collision_ratio > _HIGH_COLLISION_THRESHOLD
        )
        low_top1 = summary.top1_accuracy is not None and summary.top1_accuracy < _LOW_TOP1_THRESHOLD
        if summary.mean_margin is not None and summary.mean_margin < 0.0:
            recommendations.append(
                f"remove {summary.metric_name}: anti-signal, the best wrong candidate outscores "
                f"the right one by {abs(summary.mean_margin):.3f} on average"
            )
        elif (
            summary.collision_ratio is not None
            and summary.collision_ratio > _NEAR_CONSTANT_COLLISION_THRESHOLD
            and summary.mean_margin is not None
            and abs(summary.mean_margin) < _NEAR_CONSTANT_MARGIN_THRESHOLD
        ):
            recommendations.append(
                f"remove {summary.metric_name}: near-constant, it separates nothing on "
                f"{summary.collision_ratio:.1%} of pairs"
            )
        elif weak_stability and (weak_margin or high_collision or low_top1):
            recommendations.append(f"lower/remove {summary.metric_name}: unstable and weakly discriminative")
        elif weak_margin and high_collision and low_top1:
            recommendations.append(f"lower {summary.metric_name}: discriminative margin is weak")
    return recommendations


def _print_report(
    snapshots: Sequence[VersionSnapshot],
    summaries: Sequence[MetricSummary],
    recommendations: Sequence[str],
) -> None:
    newest = snapshots[0].head
    oldest = snapshots[-1].head
    print(f"\nversions loaded: {len(snapshots)} | newest={newest.version_id} | oldest={oldest.version_id}")
    # A build mapped against a substituted reference loses every entry whose non-obf name no longer
    # resolves, so the sample count silently shrinks. Show the attrition instead of assuming it away.
    print("\n| build | non-obf side | mapped | resolved |")
    print("|---|---|---:|---:|")
    for snapshot in snapshots:
        print(
            f"| {snapshot.head.version_id} "
            f"| {snapshot.head.non_obf_source} "
            f"| {snapshot.head.mapped_message_count} "
            f"| {len(snapshot.mapping_by_non_obf_cls)} |"
        )
    print("\n| metric | stability mean | p10 | p50 | p90 | margin | top1 | rank | collisions |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for summary in summaries:
        print(
            f"| {summary.metric_name} "
            f"| {summary.mean_score:.3f} "
            f"| {summary.p10_score:.3f} "
            f"| {summary.p50_score:.3f} "
            f"| {summary.p90_score:.3f} "
            f"| {_format_optional_float(summary.mean_margin)} "
            f"| {_format_optional_float(summary.top1_accuracy)} "
            f"| {_format_optional_float(summary.mean_rank)} "
            f"| {_format_optional_float(summary.collision_ratio)} |"
        )
    print("\nrecommendations:")
    if not recommendations:
        print("- no metric crossed the noisy-signal thresholds")
        return
    for recommendation in recommendations:
        print(f"- {recommendation}")


def _format_optional_float(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}"


def _serialize_summaries(summaries: Sequence[MetricSummary]) -> list[JsonObject]:
    return [
        {
            "metric_name": summary.metric_name,
            "sample_count": int(summary.sample_count),
            "coverage_ratio": float(summary.coverage_ratio),
            "mean_score": float(summary.mean_score),
            "p10_score": float(summary.p10_score),
            "p50_score": float(summary.p50_score),
            "p90_score": float(summary.p90_score),
            "mean_margin": _format_json_float(summary.mean_margin),
            "top1_accuracy": _format_json_float(summary.top1_accuracy),
            "mean_rank": _format_json_float(summary.mean_rank),
            "collision_ratio": _format_json_float(summary.collision_ratio),
        }
        for summary in summaries
    ]


def _serialize_samples(samples: Sequence[MetricSample]) -> list[JsonObject]:
    return [
        {
            "metric_name": sample.metric_name,
            "score": float(sample.score),
            "true_score": _format_json_float(sample.true_score),
            "best_false_score": _format_json_float(sample.best_false_score),
            "true_rank": _format_json_int(sample.true_rank),
            "candidate_count": _format_json_int(sample.candidate_count),
        }
        for sample in samples
    ]


def _format_json_float(value: float | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _format_json_int(value: int | None) -> int | None:
    if value is None:
        return None
    return int(value)


if __name__ == "__main__":
    main()
