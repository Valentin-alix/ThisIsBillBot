"""
Measure how well the matcher does on its own, without any manual pin.

Every obfuscated build wipes ``pinned_pairs.json``, so the pins have to be rebuilt by hand. This
script quantifies how much of that manual work the automatic scoring already covers: it runs the
exact matching pipeline with an empty pin set and diffs the result against the committed mappings.

The pinned pairs are the only independently verified ground truth we have, so they are reported
separately from the global agreement rate, which mostly measures non-regression.

Nothing is written: ``build_game_mappings_document`` is called directly instead of
``write_game_mappings``, so the committed artifacts stay untouched.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from consts import (
    CAPTURE_SEQUENCE_HINTS_FILE,
    GAME_MAPPINGS_DETAILED_JSON_FILE,
    NON_OBF_NEW_DUMP_CS_FILE,
    NON_OBF_PROTO_ACCESSES_FILE,
    NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    NON_OBF_SIGNATURE_OVERRIDES_FILE,
    OBF_PROTO_ACCESSES_FILE,
    OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    PINNED_PAIRS_FILE,
)
from proto_mapper_assembly.controllers.capture_sequence_hints import (
    load_capture_sequence_hints,
    resolve_capture_sequence_hints_non_obf_targets,
)
from proto_mapper_assembly.controllers.game_mappings import (
    build_game_mappings_document,
    load_game_mappings_document,
)
from proto_mapper_assembly.controllers.matching_inputs_loader import load_matching_inputs
from proto_mapper_assembly.controllers.new_dump_cs import load_new_dump_cs_messages
from proto_mapper_assembly.controllers.pinned_pairs import (
    load_pinned_pairs,
    resolve_pinned_pairs_non_obf_targets,
)
from proto_mapper_assembly.interfaces.game_mappings import GameMappingsDocument
from proto_mapper_assembly.interfaces.matching_inputs import MatchingRunConfig
from proto_mapper_assembly.interfaces.pinned_pairs import PinnedPairsConfig
from proto_mapper_assembly.matching.orchestrator import match_messages
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


@dataclass(frozen=True)
class PinOutcome:
    non_obf_key: str
    """Mapping-document key when the pinned message exists there, else the pinned name as written."""
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
    """(non-obf key, reference obf, candidate obf) for keys present on both sides but disagreeing."""
    dropped: tuple[str, ...]
    """Reference keys the pin-less run did not map at all."""
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

    # Pins name their target as a composed class (``Com.Ankama...Foo``) while the documents key it as
    # a namespace (``.com.ankama...Foo``), so both sides go through the same normalization.
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
    """Same normalization as the auto-mode contract check, so both agree on what a pin points at."""
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


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--with-pins",
        action="store_true",
        help="Run with pinned_pairs.json applied, to sanity-check the harness itself.",
    )
    parser.add_argument(
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
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Also dump the report as JSON, to diff two runs.",
    )
    return parser


def main() -> None:
    args = build_argument_parser().parse_args()
    report = run_benchmark(
        use_pinned_pairs=bool(args.with_pins),
        signature_overrides_path=args.signature_overrides,
    )
    print(format_report(report))
    json_path: Path | None = args.json
    if json_path is not None:
        # ``recovered_pin_count`` is a property, so it is not part of the dataclass fields; it is
        # the first thing anyone looks at, so it is worth carrying explicitly.
        payload = asdict(report) | {"recovered_pin_count": report.recovered_pin_count}
        json_path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")
        print(f"Written to {json_path}")


if __name__ == "__main__":
    main()
