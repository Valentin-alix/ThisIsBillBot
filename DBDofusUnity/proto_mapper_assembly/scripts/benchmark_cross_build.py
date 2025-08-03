"""
Replay past game updates and score the matcher against the messages the bot actually used.

``benchmark_no_pins`` grades against ``game_mappings_detailed.json``, which the matcher produced,
so its agreement rate mostly rewards not changing anything. Here each archived build is replayed
with no pins and no overrides, and scored against the mapping and the ``MSG_TO_MAP`` list of its
own era -- the pairs someone actually relied on, and so the only ones known to be right.

The obfuscated side comes from the archived build, the non-obfuscated side from the current
reference: a game update replaces the former and not the latter.

Nothing is written outside the cache directory.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from consts import (
    NON_OBF_NEW_DUMP_CS_FILE,
    NON_OBF_PROTO_ACCESSES_FILE,
    NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    OBF_GAME_SNAPSHOTS_DIR,
    PROJECT_ROOT,
)

from proto_mapper_assembly.controllers.game_mappings import build_game_mappings_document
from proto_mapper_assembly.controllers.matching_inputs_loader import load_matching_inputs
from proto_mapper_assembly.controllers.new_dump_cs import load_new_dump_cs_messages
from proto_mapper_assembly.controllers.message_lookup import (
    build_non_obf_alias_lookup,
    build_obf_alias_lookup,
    resolve_non_obf_alias,
    resolve_obf_alias,
)
from proto_mapper_assembly.controllers.pinned_pairs import load_pinned_pairs, write_pinned_pairs
from proto_mapper_assembly.interfaces.capture_sequence_hints import CaptureSequenceHintsConfig
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from proto_mapper_assembly.interfaces.game_mappings import (
    GameMappingEntry,
    GameMappingsDocument,
    SimpleGameMappingsDocument,
)
from proto_mapper_assembly.interfaces.matching_inputs import MatchingRunConfig
from proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig
from proto_mapper_assembly.matching.orchestrator import match_messages
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore
from proto_mapper_assembly.scripts.benchmark_no_pins import PinOutcome, _normalize_name
from proto_mapper_assembly.scripts.export_signature_overrides import (
    SignatureOverrideExportPaths,
    run_export_signature_overrides,
)
from proto_mapper_assembly.scripts.recover_archived_game_mappings import (
    iter_mapping_commits,
    resolve_build_window,
)

_PINNED_PAIRS_PATH = Path("datas/proto_mapper/pinned_pairs.json")
_ERA_PATHS = (_PINNED_PAIRS_PATH,)
"""
Only the pins are taken from the era. The non-obfuscated side is deliberately the current one.

A game update replaces the obfuscated build, not the reference it is mapped against, so holding the
reference fixed is what actually happens rather than a simplification. It also keeps every era
comparable, and avoids the era's own traces, which predate the tracer's current schema.
"""
_GAME_MAPPINGS_PATH = Path("game_mappings.json")
_OBF_DUMP_CS_PATH = Path("cs") / "Ankama.Dofus.Protocol.Game.cs"
_OBF_PROTO_ACCESSES_PATH = Path("proto_accesses.json")


@dataclass(frozen=True)
class EraReplay:
    build_id: str
    era_commit: str
    recovered_pin_count: int
    in_scope_pin_count: int

    bot_matched_count: int
    bot_wrong_count: int
    """
    Mapped, but not to the class this era's verified mapping had.

    Kept apart from ``bot_unmapped_count``: an unmapped message fails loudly and gets pinned by
    hand, a wrongly mapped one parses the wrong fields and fails quietly. A change that turns the
    second into the first is an improvement even when the matched count does not move.
    """

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
    parser = argparse.ArgumentParser(description=__doc__)
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
    return parser


def _resolve_build_dirs(*, snapshots_root: Path, requested: list[str] | None) -> list[Path]:
    """Return archived builds carrying both obf artifacts, newest first."""
    usable = [
        build_dir
        for build_dir in snapshots_root.iterdir()
        if build_dir.is_dir()
        and (build_dir / _OBF_DUMP_CS_PATH).is_file()
        and (build_dir / _OBF_PROTO_ACCESSES_PATH).is_file()
        and (build_dir / "GameAssembly.dll").is_file()
    ]
    if requested is not None:
        requested_names = set(requested)
        usable = [build_dir for build_dir in usable if build_dir.name in requested_names]
    return sorted(
        usable,
        key=lambda build_dir: (build_dir / "GameAssembly.dll").stat().st_mtime_ns,
        reverse=True,
    )


def _resolve_era(build_dir: Path) -> tuple[Path, str]:
    """Pin a build to the last commit made while it was the installed one."""
    window_start, window_end = resolve_build_window(obf_dir=build_dir, snapshots_root=build_dir.parent)
    commits = iter_mapping_commits(window_start=window_start, window_end=window_end)
    if not commits:
        error_message = f"{build_dir.name}: no mappings commit inside {window_start} .. {window_end}"
        raise SystemExit(error_message)
    return build_dir, commits[0][0]


def _materialize_era(*, commit: str, cache_root: Path, paths: tuple[Path, ...]) -> Path:
    """Check out the era's inputs into a cache directory, skipping what is already there."""
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
        obf_dump_cs_path=build_dir / _OBF_DUMP_CS_PATH,
        non_obf_dump_cs_path=NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
        obf_proto_accesses_path=build_dir / _OBF_PROTO_ACCESSES_PATH,
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
    # No capture hints, for every era alike. The older files use a shape the loader no longer reads,
    # and feeding them to recent eras only would buy fidelity at the cost of comparability, which is
    # the whole point of running the same matcher against several builds.
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
    """
    Export the overrides this build would have left behind, from the mapping it just produced.

    Generating them is the only way to get a genuinely stale file: the archived ones predate
    ``FieldKey`` and cannot be read, and the current one self-matches the current build. Pins stay
    out, matching the pin-free replay.
    """
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
            obf_dump_cs_path=build_dir / _OBF_DUMP_CS_PATH,
            non_obf_dump_cs_path=NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
            new_dump_cs_path=NON_OBF_NEW_DUMP_CS_FILE,
            obf_proto_accesses_path=build_dir / _OBF_PROTO_ACCESSES_PATH,
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
) -> list[PinOutcome]:
    """
    Score only the messages the bot actually drove at the time, against that era's own mapping.

    The rest of a mapping file is not ground truth. A pair nobody ever exercised was never
    confirmed, so a run that maps it differently, or not at all, has not necessarily got it wrong --
    counting those as regressions makes any change look damaging and hides whether the messages that
    matter still land. ``MSG_TO_MAP`` is the list that matters: every entry is annotated with the
    bot source file that consumes it, so a wrong mapping there breaks something visible.
    """
    bot_message_names = _load_bot_used_message_names(era_commit)
    reference = SimpleGameMappingsDocument.model_validate_json(
        (build_dir / _GAME_MAPPINGS_PATH).read_bytes()
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
    """Read ``MSG_TO_MAP`` as it stood at a commit: the messages the bot consumed back then."""
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
    """
    Resolve an era's pins, dropping the ones naming a message the protocol has since removed.

    The shared resolver raises on those, which is right for the pipeline and wrong for a replay
    that has to survive months of drift.
    """
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
    """
    Every era is replayed without signature overrides.

    A build's overrides are exported *from* its own mapping, so feeding them back in would grade
    the matcher on its own answers; and the archived files cannot be read anyway, predating
    ``FieldKey`` and storing a bare offset where a field identity is now required.
    """
    empty_path = cache_root / "empty_signature_overrides.json"
    if not empty_path.is_file():
        empty_path.parent.mkdir(parents=True, exist_ok=True)
        empty_path.write_text("{}", encoding="utf-8")
    return empty_path


def _score_pins(
    *, candidate_document_root: Mapping[str, GameMappingEntry], era_pins: PinnedPairsConfig
) -> list[PinOutcome]:
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
    """
    Replay each build again with the overrides its predecessor would have exported.

    ``eras`` is newest first, so the entry after a build is the one that came before it in time.
    """
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
    # Wrong is printed beside correct on purpose: a change that turns unmapped into wrong raises
    # both the matched count and the damage, and reading correct alone hides that entirely.
    print(
        f"\nTOTAL bot-used correct={bot_matched} wrong={bot_wrong} unmapped={bot_unmapped} "
        f"of {bot_total} ({bot_matched / max(bot_total, 1):.4f})"
    )
    print(f"TOTAL pins     {recovered}/{in_scope} ({recovered / max(in_scope, 1):.4f})")


if __name__ == "__main__":
    main()
