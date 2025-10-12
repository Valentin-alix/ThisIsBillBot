"""Allocate and validate stable neutral names for unknown protobuf symbols."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, cast

from DBDofusUnity.consts import NON_OBF_PROTO_OUTPUT, PROTO_MAPPER_DATA_ROOT


UNKNOWN_NAME_REGISTRY_FILE = PROTO_MAPPER_DATA_ROOT / "unknown_name_registry.json"
_DECLARATION_PATTERN = re.compile(r"\b(message|enum)\s+([A-Za-z][A-Za-z0-9_]*)\b")
_BRACE_PATTERN = re.compile(r"\b(?:message|enum)\s+[A-Za-z][A-Za-z0-9_]*\b|[{}]")
_FIELD_PATTERN = re.compile(
    r"(?m)^\s*(?:(?:repeated|optional)\s+)?(?:map<[^>]+>|[A-Za-z_.][A-Za-z0-9_.]*)\s+(unknown_[A-Za-z0-9_]+)\s*=\s*\d+"
)
_ONEOF_PATTERN = re.compile(r"(?m)^\s*oneof\s+(unknown_[A-Za-z0-9_]+)\s*\{")
_PACKAGE_PATTERN = re.compile(r"(?m)^package\s+([A-Za-z0-9_.]+)\s*;")
_TOKEN_PATTERN = re.compile(r"\b(?:Unknown[A-Za-z0-9_]+|unknown_[A-Za-z0-9_]+|UNKNOWN_[A-Za-z0-9_]+)\b")


@dataclass(frozen=True, slots=True)
class ProtoSymbol:
    path: str
    name: str
    start: int
    end: int
    body_start: int
    body_end: int
    scope: tuple[str, ...]
    kind: str


def _cardinal(number: int) -> str:
    assert number > 0, f"Unknown-name number must be positive: {number}"
    units = ("", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine")
    teens = ("Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen")
    tens = ("", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety")
    if number < 10:
        return units[number]
    if number < 20:
        return teens[number - 10]
    if number < 100:
        return tens[number // 10] + units[number % 10]
    if number < 1000:
        return units[number // 100] + "Hundred" + _cardinal(number % 100) if number % 100 else units[number // 100] + "Hundred"
    raise ValueError(f"Unknown-name registry supports fewer than 1000 symbols: {number}")


def _snake_cardinal(number: int) -> str:
    return re.sub(r"(?<!^)([A-Z])", r"_\1", _cardinal(number)).lower()


def _load_registry(path: Path = UNKNOWN_NAME_REGISTRY_FILE) -> dict[str, dict[str, int]]:
    with path.open(encoding="utf-8") as handle:
        payload: dict[str, Any] = json.load(handle)
    assert isinstance(payload, dict), f"Unknown-name registry must be an object: {path}"
    types: Any = payload.get("types")
    fields: Any = payload.get("fields")
    assert isinstance(types, dict) and isinstance(fields, dict), f"Unknown-name registry must contain types and fields: {path}"
    type_items = cast(dict[Any, Any], types)
    field_items = cast(dict[Any, Any], fields)
    parsed_types: dict[str, int] = {}
    parsed_fields: dict[str, int] = {}
    for key, value in type_items.items():
        assert isinstance(key, str) and isinstance(value, int), f"Invalid type allocation: {path}"
        parsed_types[key] = value
    for key, value in field_items.items():
        assert isinstance(key, str) and isinstance(value, int), f"Invalid field allocation: {path}"
        parsed_fields[key] = value
    return {"types": parsed_types, "fields": parsed_fields}


def _write_registry(registry: dict[str, dict[str, int]], path: Path = UNKNOWN_NAME_REGISTRY_FILE) -> None:
    path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_proto(proto_path: Path) -> str:
    return proto_path.read_bytes().decode("utf-8")


def _find_symbols(proto_path: Path) -> tuple[list[ProtoSymbol], list[ProtoSymbol]]:
    content = _read_proto(proto_path)
    package_match = _PACKAGE_PATTERN.search(content)
    assert package_match is not None, f"Missing protobuf package: {proto_path}"
    package = package_match.group(1)
    declarations: list[ProtoSymbol] = []
    all_declarations: list[ProtoSymbol] = []
    stack: list[ProtoSymbol | None] = []
    pending: ProtoSymbol | None = None
    for token in _BRACE_PATTERN.finditer(content):
        value = token.group()
        declaration_match = _DECLARATION_PATTERN.fullmatch(value)
        if declaration_match is not None:
            scope = tuple(symbol.name for symbol in stack if symbol is not None)
            name = declaration_match.group(2)
            name_start = token.start() + value.rfind(name)
            pending = ProtoSymbol(
                path=".".join((package, *scope, name)), name=name, start=name_start, end=name_start + len(name),
                body_start=-1, body_end=-1, scope=scope, kind=declaration_match.group(1),
            )
        elif value == "{":
            stack.append(pending)
            pending = None
        elif value == "}":
            symbol = stack.pop()
            if symbol is not None:
                completed = replace(symbol, body_start=symbol.end, body_end=token.start())
                all_declarations.append(completed)
                if completed.name.startswith("Unknown"):
                    declarations.append(completed)
    assert not stack, f"Unbalanced protobuf braces: {proto_path}"
    fields: list[ProtoSymbol] = []
    for pattern in (_FIELD_PATTERN, _ONEOF_PATTERN):
        for field_match in pattern.finditer(content):
            containing = [symbol for symbol in all_declarations if symbol.body_start < field_match.start(1) < symbol.body_end]
            assert containing, f"Unknown field outside a protobuf type: {proto_path}:{field_match.group(1)}"
            parent = max(containing, key=lambda symbol: len(symbol.scope))
            fields.append(
                ProtoSymbol(
                    path=f"{parent.path}.{field_match.group(1)}", name=field_match.group(1), start=field_match.start(1),
                    end=field_match.end(1), body_start=-1, body_end=-1, scope=(*parent.scope, parent.name), kind="field",
                )
            )
    return all_declarations, fields


def _all_symbols(proto_root: Path) -> tuple[dict[Path, tuple[list[ProtoSymbol], list[ProtoSymbol]]], list[ProtoSymbol], list[ProtoSymbol]]:
    by_path: dict[Path, tuple[list[ProtoSymbol], list[ProtoSymbol]]] = {}
    all_types: list[ProtoSymbol] = []
    all_fields: list[ProtoSymbol] = []
    for proto_path in sorted(proto_root.rglob("*.proto")):
        declarations, fields = _find_symbols(proto_path)
        by_path[proto_path] = (declarations, fields)
        all_types.extend(symbol for symbol in declarations if symbol.name.startswith("Unknown"))
        all_fields.extend(fields)
    return by_path, all_types, all_fields


def _next_allocations(symbols: list[ProtoSymbol], current: dict[str, int]) -> dict[str, int]:
    allocations = dict(current)
    next_number = max(allocations.values(), default=0) + 1
    for symbol in sorted(symbols, key=lambda item: item.path):
        if symbol.path not in allocations:
            allocations[symbol.path] = next_number
            next_number += 1
    return allocations


def _canonical_type_path(path: str, allocations: dict[str, int]) -> str:
    source_parts = path.split(".")
    target_parts: list[str] = []
    for index, source_part in enumerate(source_parts):
        source_prefix = ".".join(source_parts[: index + 1])
        target_parts.append("Unknown" + _cardinal(allocations[source_prefix]) if source_prefix in allocations else source_part)
    return ".".join(target_parts)


def _replace_content(content: str, replacements: list[tuple[int, int, str]]) -> str:
    result = content
    distinct_replacements = {(start, end): replacement for start, end, replacement in replacements}
    for (start, end), replacement in sorted(distinct_replacements.items(), reverse=True):
        result = result[:start] + replacement + result[end:]
    return result


def _resolve_type_replacement(
    token: str,
    position: int,
    local_declarations: list[ProtoSymbol],
    all_declarations: list[ProtoSymbol],
    registry: dict[str, int],
) -> str | None:
    candidates = [symbol for symbol in all_declarations if symbol.name == token and symbol.path in registry]
    if not candidates:
        return None
    local_candidates = [symbol for symbol in local_declarations if symbol in candidates]
    containing = [symbol for symbol in local_candidates if symbol.body_start < position < symbol.body_end]
    if containing:
        selected = max(containing, key=lambda symbol: len(symbol.scope))
    else:
        enclosing_scopes = {
            (*symbol.scope, symbol.name)
            for symbol in local_declarations
            if symbol.body_start < position < symbol.body_end
        }
        scoped_candidates = [symbol for symbol in local_candidates if symbol.scope in enclosing_scopes]
        if scoped_candidates:
            selected = max(scoped_candidates, key=lambda symbol: len(symbol.scope))
        else:
            assert len(candidates) == 1, f"Ambiguous unknown type reference: {token}"
            selected = candidates[0]
    return "Unknown" + _cardinal(registry[selected.path])


def _enum_value_replacement(token: str, position: int, declarations: list[ProtoSymbol], registry: dict[str, int]) -> str | None:
    containing = [symbol for symbol in declarations if symbol.kind == "enum" and symbol.body_start < position < symbol.body_end]
    if not containing:
        return None
    enum = max(containing, key=lambda symbol: len(symbol.scope))
    old_prefix = re.sub(r"(?<!^)([A-Z])", r"_\1", enum.name).upper()
    if not token.startswith(old_prefix):
        return None
    return "UNKNOWN_" + _snake_cardinal(registry[enum.path]).upper() + token[len(old_prefix):]


def migrate_unknown_names(*, proto_root: Path = NON_OBF_PROTO_OUTPUT, registry_path: Path = UNKNOWN_NAME_REGISTRY_FILE) -> None:
    by_path, all_types, all_fields = _all_symbols(proto_root)
    registry: dict[str, dict[str, int]] = (
        _load_registry(registry_path) if registry_path.exists() else {"types": {}, "fields": {}}
    )
    registry["types"] = _next_allocations(all_types, registry["types"])
    registry["fields"] = _next_allocations(all_fields, registry["fields"])
    _write_registry(registry, registry_path)
    for proto_path, (declarations, fields) in by_path.items():
        unknown_declarations = [symbol for symbol in declarations if symbol.name.startswith("Unknown")]
        content = _read_proto(proto_path)
        replacements = [
            (symbol.start, symbol.end, "Unknown" + _cardinal(registry["types"][symbol.path]))
            for symbol in unknown_declarations
        ] + [
            (symbol.start, symbol.end, "unknown_" + _snake_cardinal(registry["fields"][symbol.path])) for symbol in fields
        ]
        declared_locations = {(start, end) for start, end, _ in replacements}
        for token_match in _TOKEN_PATTERN.finditer(content):
            if (token_match.start(), token_match.end()) in declared_locations:
                continue
            token = token_match.group()
            if token.startswith("Unknown"):
                replacement = _resolve_type_replacement(
                    token, token_match.start(), declarations, all_types, registry["types"]
                )
            elif token.startswith("UNKNOWN_"):
                replacement = _enum_value_replacement(token, token_match.start(), unknown_declarations, registry["types"])
            else:
                matching_fields = [symbol for symbol in fields if symbol.name == token]
                replacement = None if len(matching_fields) != 1 else "unknown_" + _snake_cardinal(registry["fields"][matching_fields[0].path])
            if replacement is not None:
                replacements.append((token_match.start(), token_match.end(), replacement))
        proto_path.write_text(_replace_content(content, replacements), encoding="utf-8")
    registry = {
        "types": {
            _canonical_type_path(source_path, registry["types"]): number
            for source_path, number in registry["types"].items()
        },
        "fields": {
            _canonical_type_path(source_path.rsplit(".", 1)[0], registry["types"])
            + ".unknown_"
            + _snake_cardinal(number): number
            for source_path, number in registry["fields"].items()
        },
    }
    _write_registry(registry, registry_path)
    validate_unknown_names(proto_root=proto_root, registry_path=registry_path)


def validate_unknown_names(*, proto_root: Path = NON_OBF_PROTO_OUTPUT, registry_path: Path = UNKNOWN_NAME_REGISTRY_FILE) -> None:
    registry = _load_registry(registry_path)
    assert len(set(registry["types"].values())) == len(registry["types"]), "Unknown type allocations must be unique"
    assert len(set(registry["fields"].values())) == len(registry["fields"]), "Unknown field allocations must be unique"
    _, types, fields = _all_symbols(proto_root)
    expected_types = {symbol.path: registry["types"].get(symbol.path) for symbol in types}
    expected_fields = {symbol.path: registry["fields"].get(symbol.path) for symbol in fields}
    assert all(number is not None for number in expected_types.values()), "Unknown type declaration is missing a registry allocation"
    assert all(number is not None for number in expected_fields.values()), "Unknown field declaration is missing a registry allocation"
    for symbol in types:
        expected = "Unknown" + _cardinal(registry["types"][symbol.path])
        assert symbol.name == expected, f"Invalid neutral type name {symbol.path}: expected {expected}"
    for symbol in fields:
        expected = "unknown_" + _snake_cardinal(registry["fields"][symbol.path])
        assert symbol.name == expected, f"Invalid neutral field name {symbol.path}: expected {expected}"
    canonical_type_names = {"Unknown" + _cardinal(number) for number in registry["types"].values()}
    canonical_field_names = {"unknown_" + _snake_cardinal(number) for number in registry["fields"].values()}
    declarations_by_path, _, _ = _all_symbols(proto_root)
    for proto_path in sorted(proto_root.rglob("*.proto")):
        content = _read_proto(proto_path)
        declarations = declarations_by_path[proto_path][0]
        unknown_declarations = [symbol for symbol in declarations if symbol.name.startswith("Unknown")]
        for token_match in _TOKEN_PATTERN.finditer(content):
            token = token_match.group()
            if token.startswith("Unknown"):
                assert token in canonical_type_names, f"Obfuscated unknown type remains: {proto_path}:{token}"
            if token.startswith("unknown_"):
                assert token in canonical_field_names, f"Obfuscated unknown field remains: {proto_path}:{token}"
            if token.startswith("UNKNOWN_"):
                unknown_enums = [
                    symbol
                    for symbol in unknown_declarations
                    if symbol.kind == "enum" and symbol.body_start < token_match.start() < symbol.body_end
                ]
                if unknown_enums:
                    expected = _enum_value_replacement(token, token_match.start(), unknown_declarations, registry["types"])
                    assert expected == token, f"Obfuscated unknown enum value remains: {proto_path}:{token}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--migrate", action="store_true", help="Allocate and rewrite all current unknown protobuf symbols.")
    arguments = parser.parse_args()
    if arguments.migrate:
        migrate_unknown_names()
    else:
        validate_unknown_names()


if __name__ == "__main__":
    main()
