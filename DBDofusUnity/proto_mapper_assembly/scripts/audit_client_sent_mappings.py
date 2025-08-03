from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from consts import GAME_MAPPINGS_JSON_FILE


@dataclass(frozen=True)
class MissingMappingSample:
    log_path: Path
    line_number: int
    datetime: str | None
    origin: str
    obfuscated_type: str
    non_obfuscated_type: str | None
    obfuscated_content: object


@dataclass(frozen=True)
class AuditResult:
    scanned_messages: int
    scanned_client_messages: int
    missing_samples: list[MissingMappingSample]
    client_messages_by_log_path: dict[Path, int]
    missing_mappings_by_log_path: dict[Path, int]


def main() -> None:
    args = build_argument_parser().parse_args()
    log_paths = resolve_log_paths(args.logs)
    resolved_obfuscated_types = load_resolved_obfuscated_types(Path(args.game_mappings))
    result = audit_logs(
        log_paths=log_paths,
        include_server=bool(args.include_server),
        resolved_obfuscated_types=resolved_obfuscated_types,
    )

    if args.json:
        print(json.dumps(serialize_result(result), indent=2, ensure_ascii=False))
        return

    print_text_report(result)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit unmapped game protocol messages sent by the client in JSONL logs."
    )
    parser.add_argument(
        "logs",
        nargs="+",
        help="JSONL log paths or glob patterns, for example ../resources/logs/renaissance.haha*.debug.jsonl.",
    )
    parser.add_argument(
        "--include-server",
        action="store_true",
        help="Also include unmapped server-origin messages. By default only Client messages are reported.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a machine-readable JSON report instead of text.",
    )
    parser.add_argument(
        "--game-mappings",
        default=str(GAME_MAPPINGS_JSON_FILE),
        help="Current game_mappings.json used to ignore log-time misses already resolved now.",
    )
    return parser


def resolve_log_paths(patterns: Sequence[str]) -> list[Path]:
    resolved_paths: list[Path] = []
    for pattern in patterns:
        matched_paths = resolve_log_pattern(pattern)
        if matched_paths:
            resolved_paths.extend(matched_paths)
            continue
        resolved_paths.append(Path(pattern))

    existing_paths = [path for path in resolved_paths if path.exists()]
    missing_paths = [path for path in resolved_paths if not path.exists()]
    if missing_paths:
        missing_labels = ", ".join(str(path) for path in missing_paths)
        message = f"Log path does not exist: {missing_labels}"
        raise SystemExit(message)

    return sorted(set(existing_paths))


def resolve_log_pattern(pattern: str) -> list[Path]:
    if not has_glob_pattern(pattern):
        return []

    pattern_path = Path(pattern)
    if pattern_path.is_absolute():
        return list(pattern_path.parent.glob(pattern_path.name))

    return list(Path.cwd().glob(pattern))


def has_glob_pattern(pattern: str) -> bool:
    return any(glob_marker in pattern for glob_marker in ("*", "?", "["))


def load_resolved_obfuscated_types(game_mappings_path: Path) -> frozenset[str]:
    with game_mappings_path.open("r", encoding="utf-8") as mappings_handle:
        parsed_value: object = json.load(mappings_handle)

    if not isinstance(parsed_value, Mapping):
        message = f"Invalid game mappings document: {game_mappings_path}"
        raise SystemExit(message)

    mappings_document = cast("Mapping[object, object]", parsed_value)
    resolved_obfuscated_types: set[str] = set()
    for mapping_value in mappings_document.values():
        if not isinstance(mapping_value, Mapping):
            continue
        mapping = cast("Mapping[object, object]", mapping_value)
        obfuscated_type = mapping.get("obf_msg_namespace")
        if isinstance(obfuscated_type, str):
            resolved_obfuscated_types.add(obfuscated_type)

    return frozenset(resolved_obfuscated_types)


def audit_logs(
    *,
    log_paths: Sequence[Path],
    include_server: bool = False,
    resolved_obfuscated_types: frozenset[str] = frozenset(),
) -> AuditResult:
    scanned_messages = 0
    scanned_client_messages = 0
    missing_samples: list[MissingMappingSample] = []
    client_messages_by_log_path: dict[Path, int] = {}
    missing_mappings_by_log_path: dict[Path, int] = {}

    for log_path in log_paths:
        client_messages_by_log_path.setdefault(log_path, 0)
        missing_mappings_by_log_path.setdefault(log_path, 0)
        with log_path.open("r", encoding="utf-8") as log_handle:
            for line_number, raw_line in enumerate(log_handle, start=1):
                record = parse_json_record(raw_line=raw_line, log_path=log_path, line_number=line_number)
                if record is None:
                    continue

                category = record.get("categorie")
                if category != "message":
                    continue

                origin_value = record.get("origine")
                if not isinstance(origin_value, str):
                    continue

                scanned_messages += 1
                if origin_value == "Client":
                    scanned_client_messages += 1
                    client_messages_by_log_path[log_path] += 1
                elif not include_server:
                    continue

                sample = build_missing_sample(
                    record=record,
                    log_path=log_path,
                    line_number=line_number,
                    origin=origin_value,
                    resolved_obfuscated_types=resolved_obfuscated_types,
                )
                if sample is not None:
                    missing_samples.append(sample)
                    missing_mappings_by_log_path[log_path] += 1

    return AuditResult(
        scanned_messages=scanned_messages,
        scanned_client_messages=scanned_client_messages,
        missing_samples=missing_samples,
        client_messages_by_log_path=client_messages_by_log_path,
        missing_mappings_by_log_path=missing_mappings_by_log_path,
    )


def parse_json_record(
    *,
    raw_line: str,
    log_path: Path,
    line_number: int,
) -> Mapping[str, object] | None:
    stripped_line = raw_line.strip()
    if not stripped_line:
        return None

    try:
        parsed_value: object = json.loads(stripped_line)
    except json.JSONDecodeError as json_error:
        message = f"{log_path}:{line_number}: invalid JSONL record: {json_error}"
        raise SystemExit(message) from json_error

    if not isinstance(parsed_value, Mapping):
        return None

    parsed_mapping = cast("Mapping[object, object]", parsed_value)
    return {key: value for key, value in parsed_mapping.items() if isinstance(key, str)}


def build_missing_sample(
    *,
    record: Mapping[str, object],
    log_path: Path,
    line_number: int,
    origin: str,
    resolved_obfuscated_types: frozenset[str],
) -> MissingMappingSample | None:
    type_obfusque = record.get("type_obfusque")
    if not isinstance(type_obfusque, str):
        return None

    type_non_obfusque_value = record.get("type_non_obfusque")
    type_non_obfusque = type_non_obfusque_value if isinstance(type_non_obfusque_value, str) else None
    contenu_non_obfusque = record.get("contenu_non_obfusque")

    type_was_not_translated = type_non_obfusque is None or type_non_obfusque == type_obfusque
    payload_was_not_translated = contenu_non_obfusque is None
    if not type_was_not_translated and not payload_was_not_translated:
        return None
    if type_obfusque in resolved_obfuscated_types:
        return None

    datetime_value = record.get("datetime")
    datetime_label = datetime_value if isinstance(datetime_value, str) else None

    return MissingMappingSample(
        log_path=log_path,
        line_number=line_number,
        datetime=datetime_label,
        origin=origin,
        obfuscated_type=type_obfusque,
        non_obfuscated_type=type_non_obfusque,
        obfuscated_content=record.get("contenu_obfusque"),
    )


def print_text_report(result: AuditResult) -> None:
    print(f"scanned_messages: {result.scanned_messages}")
    print(f"scanned_client_messages: {result.scanned_client_messages}")
    print(f"missing_mappings: {len(result.missing_samples)}")
    print("by_log:")
    for log_path in result.client_messages_by_log_path:
        client_messages = result.client_messages_by_log_path[log_path]
        missing_mappings = result.missing_mappings_by_log_path[log_path]
        print(f"  {log_path}: client_messages={client_messages} missing_mappings={missing_mappings}")

    if not result.missing_samples:
        return

    counts_by_type = Counter(sample.obfuscated_type for sample in result.missing_samples)
    print("missing_by_obfuscated_type:")
    for obfuscated_type, count in counts_by_type.most_common():
        print(f"  {obfuscated_type}: {count}")

    print("samples:")
    for sample in result.missing_samples:
        payload = json.dumps(sample.obfuscated_content, ensure_ascii=False, sort_keys=True)
        print(
            f"  {sample.log_path}:{sample.line_number} "
            f"origin={sample.origin} "
            f"obf={sample.obfuscated_type} "
            f"non_obf={sample.non_obfuscated_type} "
            f"datetime={sample.datetime} "
            f"payload={payload}"
        )


def serialize_result(result: AuditResult) -> dict[str, object]:
    return {
        "scanned_messages": result.scanned_messages,
        "scanned_client_messages": result.scanned_client_messages,
        "missing_mappings": len(result.missing_samples),
        "missing_by_obfuscated_type": dict(
            Counter(sample.obfuscated_type for sample in result.missing_samples).most_common()
        ),
        "by_log": [
            {
                "log_path": str(log_path),
                "client_messages": result.client_messages_by_log_path[log_path],
                "missing_mappings": result.missing_mappings_by_log_path[log_path],
            }
            for log_path in result.client_messages_by_log_path
        ],
        "samples": [serialize_sample(sample) for sample in result.missing_samples],
    }


def serialize_sample(sample: MissingMappingSample) -> dict[str, object]:
    return {
        "log_path": str(sample.log_path),
        "line_number": sample.line_number,
        "datetime": sample.datetime,
        "origin": sample.origin,
        "obfuscated_type": sample.obfuscated_type,
        "non_obfuscated_type": sample.non_obfuscated_type,
        "obfuscated_content": sample.obfuscated_content,
    }


if __name__ == "__main__":
    main()
