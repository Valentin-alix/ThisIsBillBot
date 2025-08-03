import json
from collections.abc import Mapping
from pathlib import Path

from proto_mapper_assembly.controllers.message_lookup import (
    build_non_obf_alias_lookup,
    build_obf_alias_lookup,
    resolve_non_obf_alias,
    resolve_obf_alias,
)
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, normalize_proto_field_name
from proto_mapper_assembly.interfaces.game_mappings import GameMappingEntry
from proto_mapper_assembly.interfaces.pinned_pairs import (
    PinnedPair,
    PinnedPairsConfig,
)


def write_pinned_pairs(path: Path, pinned_pairs: PinnedPairsConfig) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            pinned_pairs.model_dump(mode="json", exclude_defaults=True),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def load_pinned_pairs(path: Path) -> PinnedPairsConfig:
    pinned_pairs = PinnedPairsConfig.model_validate_json(path.read_text(encoding="utf-8"))
    return PinnedPairsConfig(
        pairs=[
            pair.model_copy(
                update={
                    "field_mapping_by_obf": {
                        normalize_proto_field_name(obf_field): normalize_proto_field_name(non_obf_field)
                        for obf_field, non_obf_field in pair.field_mapping_by_obf.items()
                    }
                }
            )
            for pair in pinned_pairs.pairs
        ]
    )


def resolve_pinned_pairs_non_obf_targets(
    *,
    pinned_pairs: PinnedPairsConfig,
    obf_messages_by_cls: Mapping[str, DumpCSMessage],
    non_obf_messages_by_cls: Mapping[str, DumpCSMessage],
) -> PinnedPairsConfig:
    non_obf_alias_to_cls, short_non_obf_alias_to_cls = build_non_obf_alias_lookup(
        non_obf_messages_by_cls=non_obf_messages_by_cls
    )
    obf_alias_to_cls = build_obf_alias_lookup(obf_messages_by_cls=obf_messages_by_cls)
    resolved_pairs: list[PinnedPair] = []
    for pair in pinned_pairs.pairs:
        resolved_obf = resolve_obf_alias(pair.obf, obf_alias_to_cls)
        resolved_non_obf = resolve_non_obf_alias(
            pair.non_obf, non_obf_alias_to_cls, short_non_obf_alias_to_cls
        )
        updates: dict[str, str] = {}
        if resolved_obf != pair.obf:
            updates["obf"] = resolved_obf
        if resolved_non_obf != pair.non_obf:
            updates["non_obf"] = resolved_non_obf
        resolved_pairs.append(pair.model_copy(update=updates) if updates else pair)
    return PinnedPairsConfig(pairs=resolved_pairs)


def build_resolved_field_mapping(
    pair: PinnedPair,
    game_mapping_entry: GameMappingEntry | None,
) -> dict[str, str]:
    game_mapping_field_mapping = {} if game_mapping_entry is None else game_mapping_entry.field_mapping
    return {**game_mapping_field_mapping, **pair.field_mapping_by_obf}


def upsert_pinned_pair(path: Path, obf_msg_name: str, non_obf_msg_name: str) -> None:
    pinned_pairs = load_pinned_pairs(path) if path.exists() else PinnedPairsConfig(pairs=[])
    for pair in pinned_pairs.pairs:
        if pair.obf == obf_msg_name and pair.non_obf == non_obf_msg_name:
            write_pinned_pairs(path, pinned_pairs)
            return

    updated_pairs = [
        pair for pair in pinned_pairs.pairs if pair.obf != obf_msg_name and pair.non_obf != non_obf_msg_name
    ]
    updated_pairs.append(PinnedPair(obf=obf_msg_name, non_obf=non_obf_msg_name))
    write_pinned_pairs(path, PinnedPairsConfig(pairs=updated_pairs))


def upsert_pinned_field_mapping(
    path: Path,
    obf_msg_name: str,
    non_obf_msg_name: str,
    obf_field_name: str,
    non_obf_field_name: str,
) -> None:
    pinned_pairs = load_pinned_pairs(path) if path.exists() else PinnedPairsConfig(pairs=[])
    target_pair: PinnedPair | None = None
    updated_pairs: list[PinnedPair] = []
    for pair in pinned_pairs.pairs:
        if pair.obf == obf_msg_name and pair.non_obf == non_obf_msg_name:
            target_pair = pair
            continue
        if pair.obf == obf_msg_name or pair.non_obf == non_obf_msg_name:
            continue
        updated_pairs.append(pair)

    field_mapping = dict(target_pair.field_mapping_by_obf) if target_pair else {}
    field_mapping = {
        obf_field: non_obf_field
        for obf_field, non_obf_field in field_mapping.items()
        if obf_field != obf_field_name and non_obf_field != non_obf_field_name
    }
    field_mapping[normalize_proto_field_name(obf_field_name)] = normalize_proto_field_name(non_obf_field_name)
    updated_pairs.append(
        PinnedPair(
            obf=obf_msg_name,
            non_obf=non_obf_msg_name,
            field_mapping_by_obf=field_mapping,
        )
    )
    write_pinned_pairs(path, PinnedPairsConfig(pairs=updated_pairs))
