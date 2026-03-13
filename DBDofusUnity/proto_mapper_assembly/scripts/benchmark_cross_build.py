"""
Replay past game updates and score the matcher against the messages the bot actually used.

The default ``--mode cross-build`` replays each archived build with no pins and no overrides, and
scores it against the mapping and the ``MSG_TO_MAP`` list of its own era -- the pairs someone
actually relied on, and so the only ones known to be right.

The obfuscated side comes from the archived build, the non-obfuscated side from the current
reference: a game update replaces the former and not the latter.

Nothing is written outside the cache directory.

``--mode current`` runs the cheaper counterpart on the working set instead: the exact pipeline with
an empty pin set, diffed against the committed mappings. It grades against
``game_mappings_detailed.json``, which the matcher produced, so its agreement rate mostly rewards
not changing anything -- but the pins it recovers on its own are still independently verified
ground truth, and it needs no archived build.
"""


import argparse
import json
import re
import subprocess
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path

from DBDofusUnity.consts import (
    CAPTURE_SEQUENCE_HINTS_FILE,
    GAME_MAPPINGS_DETAILED_JSON_FILE,
    NON_OBF_NEW_DUMP_CS_FILE,
    NON_OBF_PROTO_ACCESSES_FILE,
    NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    NON_OBF_SIGNATURE_OVERRIDES_FILE,
    OBF_GAME_SNAPSHOTS_DIR,
    OBF_PROTO_ACCESSES_FILE,
    OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    PINNED_PAIRS_FILE,
    PROJECT_ROOT,
)

from DBDofusUnity.proto_mapper_assembly.controllers.capture_sequence_hints import (
    load_capture_sequence_hints,
    resolve_capture_sequence_hints_non_obf_targets,
)
from DBDofusUnity.proto_mapper_assembly.controllers.game_mappings import (
    build_game_mappings_document,
    load_game_mappings_document,
)
from DBDofusUnity.proto_mapper_assembly.controllers.matching_inputs_loader import load_matching_inputs
from DBDofusUnity.proto_mapper_assembly.controllers.new_dump_cs import load_new_dump_cs_messages
from DBDofusUnity.proto_mapper_assembly.controllers.message_lookup import (
    build_non_obf_alias_lookup,
    build_obf_alias_lookup,
    resolve_non_obf_alias,
    resolve_obf_alias,
)
from DBDofusUnity.proto_mapper_assembly.controllers.pinned_pairs import (
    load_pinned_pairs,
    resolve_pinned_pairs_non_obf_targets,
    write_pinned_pairs,
)
from DBDofusUnity.proto_mapper_assembly.helpers.archived_builds import (
    GAME_MAPPINGS_RELATIVE_PATH,
    PROTO_ACCESSES_RELATIVE_PATH,
    PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH,
    iter_archived_build_dirs,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.capture_sequence_hints import CaptureSequenceHintsConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.interfaces.game_mappings import (
    GameMappingEntry,
    GameMappingsDocument,
    SimpleGameMappingsDocument,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.matching_inputs import MatchingRunConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig
from DBDofusUnity.proto_mapper_assembly.matching.orchestrator import match_messages
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore
from DBDofusUnity.proto_mapper_assembly.scripts.export_signature_overrides import (
    SignatureOverrideExportPaths,
    run_export_signature_overrides,
)
from DBDofusUnity.proto_mapper_assembly.scripts.recover_archived_game_mappings import (
    iter_mapping_commits,
    resolve_build_window,
)

_PINNED_PAIRS_PATH = Path("datas/proto_mapper/pinned_pairs.json")
_ERA_PATHS = (_PINNED_PAIRS_PATH,)
"""Use the current non-obfuscated reference for every era to keep comparisons consistent."""


@dataclass(frozen=True)
class EraReplay:
    build_id: str
    era_commit: str
    recovered_pin_count: int
    in_scope_pin_count: int

    bot_matched_count: int
    bot_wrong_count: int

    bot_unmapped_count: int
    bot_total_count: int

    @property
    def bot_ratio(self) -> float:
        if self.bot_total_count == 0:
            return 0.0
        return self.bot_matched_count / self.bot_total_count


@dataclass(frozen=True)
class OverrideComparison:
    source_build_id: str
    baseline: EraReplay
    with_overrides: EraReplay


def main() -> None:
    arguments = _build_argument_parser().parse_args()
    if arguments.mode == "current":
        _run_current_build_benchmark(arguments)
        return

    cache_root: Path = arguments.cache_dir
    build_dirs = _resolve_build_dirs(snapshots_root=arguments.snapshots_root, requested=arguments.builds)
    if not build_dirs:
        raise SystemExit("no archived build with both an obf dump and an obf trace")

    eras = [_resolve_era(build_dir) for build_dir in build_dirs]
    print(f"replaying {len(eras)} builds\n")

    replays: list[EraReplay] = []
    documents: list[GameMappingsDocument] = []
    for build_dir, era_commit in eras:
        print(f"--- {build_dir.name}  era={era_commit[:8]}")
        replay, document = _replay_era(build_dir=build_dir, era_commit=era_commit, cache_root=cache_root)
        replays.append(replay)
        documents.append(document)

    _print_report(replays)

    if arguments.with_previous_era_overrides:
        _print_override_report(
            _compare_with_previous_era_overrides(
                eras=eras, replays=replays, documents=documents, cache_root=cache_root
            )
        )


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--mode",
        choices=("cross-build", "current"),
        default="cross-build",
        help=(
            "'cross-build' replays every archived build against the mappings of its own era. "
            "'current' runs the working set once with no pin and diffs it against the committed "
            "mappings."
        ),
    )
    parser.add_argument(
        "--snapshots-root",
        type=Path,
        default=OBF_GAME_SNAPSHOTS_DIR,
        help="Directory holding one sub-directory per archived build.",
    )
    parser.add_argument(
        "--builds",
        nargs="*",
        default=None,
        help="Restrict to these build directory names, newest first. Defaults to every usable one.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=PROJECT_ROOT / "datas" / "proto_mapper" / ".era_cache",
        help="Where era inputs materialised out of git are kept between runs.",
    )
    parser.add_argument(
        "--with-previous-era-overrides",
        action="store_true",
        help=(
            "Also replay each build with the signature overrides its predecessor would have "
            "exported, and print the two side by side. This is what measures whether an "
            "override survives a game update."
        ),
    )
    current_mode = parser.add_argument_group("--mode current")
    current_mode.add_argument(
        "--with-pins",
        action="store_true",
        help="Run with pinned_pairs.json applied, to sanity-check the harness itself.",
    )
    current_mode.add_argument(
        "--signature-overrides",
        type=Path,
        default=None,
        help=(
            "Signature override file to inject, defaulting to the current one. Point it at a "
            "previous build's file to reproduce the state right after a game update: the current "
            "file was exported from the current build, so it makes every stored index and offset "
            "self-match and hides exactly the build-to-build drift this benchmark should expose."
        ),
    )
    current_mode.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Also dump the --mode current report as JSON, to diff two runs.",
    )
    return parser


def _run_current_build_benchmark(arguments: argparse.Namespace) -> None:
    report = run_benchmark(
        use_pinned_pairs=bool(arguments.with_pins),
        signature_overrides_path=arguments.signature_overrides,
    )
    print(format_report(report))
    json_path: Path | None = arguments.json
    if json_path is None:
        return
    payload = asdict(report) | {"recovered_pin_count": report.recovered_pin_count}
    json_path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")
    print(f"Written to {json_path}")


def _resolve_build_dirs(*, snapshots_root: Path, requested: list[str] | None) -> list[Path]:
    usable = iter_archived_build_dirs(
        snapshots_root=snapshots_root,
        required_files=(PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH, PROTO_ACCESSES_RELATIVE_PATH),
    )
    if requested is None:
        return usable
    requested_names = set(requested)
    return [build_dir for build_dir in usable if build_dir.name in requested_names]


def _resolve_era(build_dir: Path) -> tuple[Path, str]:
    window_start, window_end = resolve_build_window(obf_dir=build_dir, snapshots_root=build_dir.parent)
    commits = iter_mapping_commits(window_start=window_start, window_end=window_end)
    if not commits:
        error_message = f"{build_dir.name}: no mappings commit inside {window_start} .. {window_end}"
        raise SystemExit(error_message)
    return build_dir, commits[0][0]


def _materialize_era(*, commit: str, cache_root: Path, paths: tuple[Path, ...]) -> Path:
    era_dir = cache_root / commit
    for repo_path in paths:
        target = era_dir / repo_path
        if target.is_file():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(_read_blob(commit=commit, repo_path=repo_path))
    return era_dir


def _read_blob(*, commit: str, repo_path: Path) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{repo_path.as_posix()}"],
        cwd=PROJECT_ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


def _replay_era(
    *,
    build_dir: Path,
    era_commit: str,
    cache_root: Path,
    signature_overrides_path: Path | None = None,
) -> tuple[EraReplay, GameMappingsDocument]:
    era_dir = _materialize_era(commit=era_commit, cache_root=cache_root, paths=_ERA_PATHS)
    matching_inputs = load_matching_inputs(
        obf_dump_cs_path=build_dir / PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH,
        non_obf_dump_cs_path=NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
        obf_proto_accesses_path=build_dir / PROTO_ACCESSES_RELATIVE_PATH,
        non_obf_proto_accesses_path=NON_OBF_PROTO_ACCESSES_FILE,
        bootstrap_non_obf_dump_cs_path=NON_OBF_NEW_DUMP_CS_FILE,
        signature_overrides_path=signature_overrides_path or _empty_overrides_path(cache_root),
    )
    non_obf_messages_by_cls = matching_inputs.non_obf_messages_by_cls
    bootstrap_messages_by_cls = load_new_dump_cs_messages(NON_OBF_NEW_DUMP_CS_FILE).root
    known_non_obf_messages = {**non_obf_messages_by_cls, **bootstrap_messages_by_cls}

    era_pins = _resolve_era_pins(
        pinned_pairs=load_pinned_pairs(era_dir / _PINNED_PAIRS_PATH),
        obf_messages_by_cls=matching_inputs.obf_messages_by_cls,
        non_obf_messages_by_cls=known_non_obf_messages,
    )
    # Omit capture hints for every era: legacy shapes are unreadable and comparisons must stay uniform.
    capture_sequence_hints = CaptureSequenceHintsConfig(sequences=())

    matches = match_messages(
        inputs=matching_inputs,
        run_config=MatchingRunConfig(
            runtime_data_store=RuntimeDataStore(),
            pinned_pairs_config=PinnedPairsConfig(pairs=[]),
            capture_sequence_hints_config=capture_sequence_hints,
        ),
    )
    candidate_document = build_game_mappings_document(
        matches,
        obf_messages_by_cls=matching_inputs.obf_messages_by_cls,
        non_obf_messages_by_cls=non_obf_messages_by_cls,
    )
    outcomes = _score_pins(candidate_document_root=candidate_document.root, era_pins=era_pins)
    bot_outcomes = _score_bot_used_messages(
        candidate_document_root=candidate_document.root,
        era_commit=era_commit,
        build_dir=build_dir,
    )
    replay = EraReplay(
        build_id=build_dir.name,
        era_commit=era_commit,
        recovered_pin_count=sum(1 for outcome in outcomes if outcome.is_recovered),
        in_scope_pin_count=len(outcomes),
        bot_matched_count=sum(1 for outcome in bot_outcomes if outcome.is_recovered),
        bot_wrong_count=sum(
            1 for outcome in bot_outcomes if outcome.actual_obf is not None and not outcome.is_recovered
        ),
        bot_unmapped_count=sum(1 for outcome in bot_outcomes if outcome.actual_obf is None),
        bot_total_count=len(bot_outcomes),
    )
    return replay, candidate_document


def _export_era_overrides(
    *,
    build_dir: Path,
    cache_root: Path,
    candidate_document: GameMappingsDocument,
) -> Path:
    """Regenerate predecessor overrides because archived overrides predate the current field-key schema."""
    export_dir = cache_root / "overrides" / build_dir.name
    export_dir.mkdir(parents=True, exist_ok=True)
    detailed_path = export_dir / "game_mappings_detailed.json"
    detailed_path.write_text(candidate_document.model_dump_json(indent=2), encoding="utf-8")
    empty_pins_path = export_dir / "pinned_pairs.json"
    write_pinned_pairs(empty_pins_path, PinnedPairsConfig(pairs=[]))
    overrides_path = export_dir / "messages_access_signature_override.json"

    run_export_signature_overrides(
        export_paths=SignatureOverrideExportPaths(
            pinned_pairs_path=empty_pins_path,
            signature_overrides_path=overrides_path,
            obf_dump_cs_path=build_dir / PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH,
            non_obf_dump_cs_path=NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
            new_dump_cs_path=NON_OBF_NEW_DUMP_CS_FILE,
            obf_proto_accesses_path=build_dir / PROTO_ACCESSES_RELATIVE_PATH,
            non_obf_proto_accesses_path=NON_OBF_PROTO_ACCESSES_FILE,
            game_mappings_path=detailed_path,
        )
    )
    return overrides_path


def _score_bot_used_messages(
    *,
    candidate_document_root: Mapping[str, GameMappingEntry],
    era_commit: str,
    build_dir: Path,
) -> "list[PinOutcome]":
    """Grade only era-specific MSG_TO_MAP entries; unused mappings are not verified ground truth."""
    bot_message_names = _load_bot_used_message_names(era_commit)
    reference = SimpleGameMappingsDocument.model_validate_json(
        (build_dir / GAME_MAPPINGS_RELATIVE_PATH).read_bytes()
    ).root
    candidate_by_normalized = {_normalize_name(key): entry for key, entry in candidate_document_root.items()}
    outcomes: list[PinOutcome] = []
    for reference_key, reference_entry in reference.items():
        if reference_key.rsplit(".", 1)[-1] not in bot_message_names:
            continue
        entry = candidate_by_normalized.get(_normalize_name(reference_key))
        outcomes.append(
            PinOutcome(
                non_obf_key=reference_key,
                expected_obf=reference_entry.obf_msg_namespace,
                actual_obf=entry.obf_msg_namespace if entry is not None else None,
            )
        )
    return outcomes


def _load_bot_used_message_names(commit: str) -> frozenset[str]:
    source = _read_blob(commit=commit, repo_path=Path("consts.py")).decode("utf-8", errors="replace")
    block = re.search(r"^MSG_TO_MAP.*?=\s*\[(.*?)^\]", source, re.DOTALL | re.MULTILINE)
    if block is None:
        return frozenset()
    return frozenset(re.findall(r'"([^"]+)"', block.group(1)))


def _resolve_era_pins(
    *,
    pinned_pairs: PinnedPairsConfig,
    obf_messages_by_cls: Mapping[str, DumpCSMessage],
    non_obf_messages_by_cls: Mapping[str, DumpCSMessage],
) -> PinnedPairsConfig:
    """Drop pins for removed messages so historical replay tolerates protocol drift."""
    non_obf_alias_to_cls, short_non_obf_alias_to_cls = build_non_obf_alias_lookup(
        non_obf_messages_by_cls=non_obf_messages_by_cls
    )
    obf_alias_to_cls = build_obf_alias_lookup(obf_messages_by_cls=obf_messages_by_cls)
    resolved_pairs: list[PinnedPair] = []
    for pair in pinned_pairs.pairs:
        try:
            resolved_non_obf = resolve_non_obf_alias(
                pair.non_obf, non_obf_alias_to_cls, short_non_obf_alias_to_cls
            )
            resolved_obf = resolve_obf_alias(pair.obf, obf_alias_to_cls)
        except ValueError:
            continue
        resolved_pairs.append(pair.model_copy(update={"obf": resolved_obf, "non_obf": resolved_non_obf}))
    return PinnedPairsConfig(pairs=resolved_pairs)


def _empty_overrides_path(cache_root: Path) -> Path:
    """Exclude each build's own overrides to avoid grading the matcher against its own answers."""
    empty_path = cache_root / "empty_signature_overrides.json"
    if not empty_path.is_file():
        empty_path.parent.mkdir(parents=True, exist_ok=True)
        empty_path.write_text("{}", encoding="utf-8")
    return empty_path


def _score_pins(
    *, candidate_document_root: Mapping[str, GameMappingEntry], era_pins: PinnedPairsConfig
) -> "list[PinOutcome]":
    key_by_normalized_name = {_normalize_name(key): key for key in candidate_document_root}
    outcomes: list[PinOutcome] = []
    for pinned_pair in era_pins.pairs:
        key = key_by_normalized_name.get(_normalize_name(pinned_pair.non_obf))
        entry = candidate_document_root.get(key) if key is not None else None
        actual_obf = entry.full_obf_msg_namespace if entry is not None else None
        outcomes.append(
            PinOutcome(
                non_obf_key=key or pinned_pair.non_obf,
                expected_obf=pinned_pair.obf,
                actual_obf=actual_obf,
            )
        )
    return outcomes


def _compare_with_previous_era_overrides(
    *,
    eras: list[tuple[Path, str]],
    replays: list[EraReplay],
    documents: list[GameMappingsDocument],
    cache_root: Path,
) -> list["OverrideComparison"]:
    """Eras are newest first; the next entry supplies the predecessor's overrides."""
    comparisons: list[OverrideComparison] = []
    for newer_index in range(len(eras) - 1):
        newer_dir, newer_commit = eras[newer_index]
        older_dir, _ = eras[newer_index + 1]
        print(f"--- {newer_dir.name} with overrides exported from {older_dir.name}")
        overrides_path = _export_era_overrides(
            build_dir=older_dir,
            cache_root=cache_root,
            candidate_document=documents[newer_index + 1],
        )
        replay, _ = _replay_era(
            build_dir=newer_dir,
            era_commit=newer_commit,
            cache_root=cache_root,
            signature_overrides_path=overrides_path,
        )
        comparisons.append(
            OverrideComparison(
                source_build_id=older_dir.name,
                baseline=replays[newer_index],
                with_overrides=replay,
            )
        )
    return comparisons


def _print_override_report(comparisons: list["OverrideComparison"]) -> None:
    print("\nOverrides exported at build N-1, replayed against build N.")
    print("\n| build | overrides from | correct | wrong | unmapped |")
    print("|---|---|---:|---:|---:|")
    for comparison in comparisons:
        base = comparison.baseline
        with_overrides = comparison.with_overrides
        print(
            f"| {with_overrides.build_id} "
            f"| {comparison.source_build_id} "
            f"| {base.bot_matched_count} -> {with_overrides.bot_matched_count} "
            f"| {base.bot_wrong_count} -> {with_overrides.bot_wrong_count} "
            f"| {base.bot_unmapped_count} -> {with_overrides.bot_unmapped_count} |"
        )
    base_correct = sum(comparison.baseline.bot_matched_count for comparison in comparisons)
    base_wrong = sum(comparison.baseline.bot_wrong_count for comparison in comparisons)
    base_unmapped = sum(comparison.baseline.bot_unmapped_count for comparison in comparisons)
    correct = sum(comparison.with_overrides.bot_matched_count for comparison in comparisons)
    wrong = sum(comparison.with_overrides.bot_wrong_count for comparison in comparisons)
    unmapped = sum(comparison.with_overrides.bot_unmapped_count for comparison in comparisons)
    print(
        f"\nTOTAL with previous-era overrides  correct={base_correct}->{correct} "
        f"wrong={base_wrong}->{wrong} unmapped={base_unmapped}->{unmapped}"
    )


def _print_report(replays: list[EraReplay]) -> None:
    print("\nbot-used messages: the verified set. Everything else in a mapping file is unconfirmed.")
    print("\n| build | era | bot msgs | correct | wrong | unmapped | ratio | pins | recovered |")
    print("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for replay in replays:
        print(
            f"| {replay.build_id} "
            f"| {replay.era_commit[:8]} "
            f"| {replay.bot_total_count} "
            f"| {replay.bot_matched_count} "
            f"| {replay.bot_wrong_count} "
            f"| {replay.bot_unmapped_count} "
            f"| {replay.bot_ratio:.4f} "
            f"| {replay.in_scope_pin_count} "
            f"| {replay.recovered_pin_count} |"
        )
    bot_matched = sum(replay.bot_matched_count for replay in replays)
    bot_wrong = sum(replay.bot_wrong_count for replay in replays)
    bot_unmapped = sum(replay.bot_unmapped_count for replay in replays)
    bot_total = sum(replay.bot_total_count for replay in replays)
    recovered = sum(replay.recovered_pin_count for replay in replays)
    in_scope = sum(replay.in_scope_pin_count for replay in replays)
    print(
        f"\nTOTAL bot-used correct={bot_matched} wrong={bot_wrong} unmapped={bot_unmapped} "
        f"of {bot_total} ({bot_matched / max(bot_total, 1):.4f})"
    )
    print(f"TOTAL pins     {recovered}/{in_scope} ({recovered / max(in_scope, 1):.4f})")


@dataclass(frozen=True)
class PinOutcome:
    non_obf_key: str
    expected_obf: str
    actual_obf: str | None

    @property
    def is_recovered(self) -> bool:
        return self.actual_obf == self.expected_obf


@dataclass(frozen=True)
class BenchmarkReport:
    reference_count: int
    candidate_count: int
    agreed_count: int
    changed: tuple[tuple[str, str, str], ...]
    dropped: tuple[str, ...]
    pin_outcomes: tuple[PinOutcome, ...]

    @property
    def recovered_pin_count(self) -> int:
        return sum(1 for outcome in self.pin_outcomes if outcome.is_recovered)


def run_benchmark(*, use_pinned_pairs: bool, signature_overrides_path: Path | None = None) -> BenchmarkReport:
    matching_inputs = load_matching_inputs(
        obf_dump_cs_path=OBF_PROTOCOL_GAME_DUMP_CS_FILE,
        non_obf_dump_cs_path=NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
        obf_proto_accesses_path=OBF_PROTO_ACCESSES_FILE,
        non_obf_proto_accesses_path=NON_OBF_PROTO_ACCESSES_FILE,
        bootstrap_non_obf_dump_cs_path=NON_OBF_NEW_DUMP_CS_FILE,
        signature_overrides_path=signature_overrides_path or NON_OBF_SIGNATURE_OVERRIDES_FILE,
    )
    obf_messages_by_cls = matching_inputs.obf_messages_by_cls
    non_obf_messages_by_cls = matching_inputs.non_obf_messages_by_cls
    bootstrap_messages_by_cls = load_new_dump_cs_messages(NON_OBF_NEW_DUMP_CS_FILE).root
    resolved_pinned_pairs = resolve_pinned_pairs_non_obf_targets(
        pinned_pairs=load_pinned_pairs(PINNED_PAIRS_FILE),
        obf_messages_by_cls=obf_messages_by_cls,
        non_obf_messages_by_cls={**non_obf_messages_by_cls, **bootstrap_messages_by_cls},
    )
    capture_sequence_hints = resolve_capture_sequence_hints_non_obf_targets(
        capture_sequence_hints=load_capture_sequence_hints(CAPTURE_SEQUENCE_HINTS_FILE),
        non_obf_messages_by_cls={**non_obf_messages_by_cls, **bootstrap_messages_by_cls},
    )
    matches = match_messages(
        inputs=matching_inputs,
        run_config=MatchingRunConfig(
            runtime_data_store=RuntimeDataStore(),
            pinned_pairs_config=resolved_pinned_pairs if use_pinned_pairs else PinnedPairsConfig(pairs=[]),
            capture_sequence_hints_config=capture_sequence_hints,
        ),
    )
    candidate_document = build_game_mappings_document(
        matches,
        obf_messages_by_cls=obf_messages_by_cls,
        non_obf_messages_by_cls=non_obf_messages_by_cls,
    )
    reference_document = load_game_mappings_document(GAME_MAPPINGS_DETAILED_JSON_FILE)
    return build_report(
        reference_document=reference_document,
        candidate_document=candidate_document,
        pinned_pairs=resolved_pinned_pairs,
    )


def build_report(
    *,
    reference_document: GameMappingsDocument,
    candidate_document: GameMappingsDocument,
    pinned_pairs: PinnedPairsConfig,
) -> BenchmarkReport:
    reference_obf_by_key = {
        key: entry.full_obf_msg_namespace for key, entry in reference_document.root.items()
    }
    candidate_obf_by_key = {
        key: entry.full_obf_msg_namespace for key, entry in candidate_document.root.items()
    }
    agreed_count = 0
    changed: list[tuple[str, str, str]] = []
    dropped: list[str] = []
    for key, reference_obf in reference_obf_by_key.items():
        candidate_obf = candidate_obf_by_key.get(key)
        if candidate_obf is None:
            dropped.append(key)
        elif candidate_obf == reference_obf:
            agreed_count += 1
        else:
            changed.append((key, reference_obf, candidate_obf))

    # Normalize composed pin names and namespace-based document keys to the same form.
    key_by_normalized_name = {
        _normalize_name(key): key for key in (*reference_obf_by_key, *candidate_obf_by_key)
    }
    pin_outcomes: list[PinOutcome] = []
    for pinned_pair in pinned_pairs.pairs:
        key = key_by_normalized_name.get(_normalize_name(pinned_pair.non_obf))
        pin_outcomes.append(
            PinOutcome(
                non_obf_key=key or pinned_pair.non_obf,
                expected_obf=pinned_pair.obf,
                actual_obf=candidate_obf_by_key.get(key) if key is not None else None,
            )
        )

    return BenchmarkReport(
        reference_count=len(reference_obf_by_key),
        candidate_count=len(candidate_obf_by_key),
        agreed_count=agreed_count,
        changed=tuple(sorted(changed)),
        dropped=tuple(sorted(dropped)),
        pin_outcomes=tuple(sorted(pin_outcomes, key=lambda outcome: outcome.non_obf_key)),
    )


def _normalize_name(value: str) -> str:
    return value.removeprefix(".").casefold()


def format_report(report: BenchmarkReport) -> str:
    lines = [
        f"reference mappings: {report.reference_count}",
        f"candidate mappings: {report.candidate_count}",
        f"identical: {report.agreed_count}/{report.reference_count} "
        f"({report.agreed_count / max(1, report.reference_count):.4f})",
        f"changed: {len(report.changed)} | dropped: {len(report.dropped)}",
        f"pins recovered without pinning: {report.recovered_pin_count}/{len(report.pin_outcomes)}",
    ]
    for outcome in report.pin_outcomes:
        status = "OK  " if outcome.is_recovered else "MISS"
        lines.append(
            f"  [{status}] {outcome.non_obf_key} expected={outcome.expected_obf} got={outcome.actual_obf}"
        )
    if report.changed:
        lines.append("changed mappings:")
        lines.extend(
            f"  {key}: {reference_obf} -> {candidate_obf}"
            for key, reference_obf, candidate_obf in report.changed
        )
    if report.dropped:
        lines.append("dropped mappings:")
        lines.extend(f"  {key}" for key in report.dropped)
    return "\n".join(lines)


if __name__ == "__main__":
    main()
