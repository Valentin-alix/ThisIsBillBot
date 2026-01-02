from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from DBDofusUnity.proto_mapper_assembly.helpers.proto_helpers import build_types_by_short_name
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig

from .field_builders import make_field, number_field
from .message_builders import make_message

GAME_NS = "Com.Ankama.Dofus.Server.Game.Protocol.Game.Action"
MAP_NS = "Com.Ankama.Dofus.Server.Game.Protocol.Gamemap"
FIGHT_NS = "Com.Ankama.Dofus.Server.Game.Protocol.Fight"


@dataclass(frozen=True)
class ResolveMessageCase:
    type_name: str
    parent_message: DumpCSMessage
    messages_by_cls: dict[str, DumpCSMessage]
    expected: str | None


@dataclass(frozen=True)
class PinnedResolveCase:
    pinned_pairs: PinnedPairsConfig
    obf_messages_by_cls: dict[str, DumpCSMessage]
    non_obf_messages_by_cls: dict[str, DumpCSMessage]
    expected_obf: str
    expected_non_obf: str


@dataclass(frozen=True)
class PinnedResolveErrorCase:
    pinned_pairs: PinnedPairsConfig
    obf_messages_by_cls: dict[str, DumpCSMessage]
    non_obf_messages_by_cls: dict[str, DumpCSMessage]
    match: str


@dataclass(frozen=True)
class SnapshotLayout:
    real_game_dir: Path
    snapshots_root: Path
    non_obf_game_dir: Path


def message_lookup(*messages: DumpCSMessage) -> dict[str, DumpCSMessage]:
    return {message.composed_name: message for message in messages}


def type_index(messages_by_cls: dict[str, DumpCSMessage]) -> dict[str, tuple[DumpCSMessage, ...]]:
    return build_types_by_short_name(messages_by_cls)


def proto_field(category: FieldCategoryEnum, normalized_type: str) -> DumpCSMessageField:
    return make_field(category, normalized_type)


def resolve_message_case(kind: str) -> ResolveMessageCase:
    parent = make_message("Parent")
    match kind:
        case "direct":
            child = make_message("ChildMsg")
            return ResolveMessageCase("ChildMsg", parent, message_lookup(child), "ChildMsg")
        case "namespace":
            child = make_message("ChildMsg", namespace="GameNs")
            parent = make_message("Parent", namespace="GameNs")
            return ResolveMessageCase("ChildMsg", parent, message_lookup(child), "GameNs.ChildMsg")
        case "parent":
            child = make_message("ChildMsg", parent_name="ParentTypes")
            parent = make_message("Parent", parent_name="ParentTypes")
            return ResolveMessageCase("ChildMsg", parent, message_lookup(child), "ParentTypes.ChildMsg")
        case "single_short_name":
            child = make_message("ChildMsg")
            return ResolveMessageCase("SomePkg.ChildMsg", parent, message_lookup(child), "ChildMsg")
        case "ambiguous_namespace_match":
            child_a = make_message("ChildMsg", namespace="NsA")
            child_b = make_message("ChildMsg", namespace="NsB")
            parent = make_message("Parent", namespace="NsA")
            return ResolveMessageCase(
                "SomePkg.ChildMsg",
                parent,
                message_lookup(child_a, child_b),
                "NsA.ChildMsg",
            )
        case "ambiguous_no_match":
            child_a = make_message("ChildMsg", namespace="NsA")
            child_b = make_message("ChildMsg", namespace="NsB")
            return ResolveMessageCase("SomePkg.ChildMsg", parent, message_lookup(child_a, child_b), None)
        case "missing":
            return ResolveMessageCase("NonExistent", parent, {}, None)
        case _:
            raise ValueError(kind)


def pinned_resolve_case(kind: str) -> PinnedResolveCase:
    match kind:
        case "root_non_obf":
            root = DumpCSMessage(
                file_descriptor="GameReflection",
                name="MapCurrentEvent",
                namespace=MAP_NS,
                fields=[number_field()],
            )
            return PinnedResolveCase(
                PinnedPairsConfig(pairs=[PinnedPair(obf="isy", non_obf=f"{MAP_NS}.MapCurrentEvent")]),
                {},
                message_lookup(root),
                "isy",
                root.composed_name,
            )
        case "nested_types_non_obf":
            root = DumpCSMessage(
                file_descriptor="GameReflection",
                name="GameActionFightEvent",
                namespace=GAME_NS,
                fields=[number_field()],
            )
            types = DumpCSMessage(
                file_descriptor="GameReflection",
                name="Types",
                namespace=GAME_NS,
                parent_name="GameActionFightEvent",
            )
            child = DumpCSMessage(
                file_descriptor="GameReflection",
                name="LifePointsLost",
                namespace=GAME_NS,
                parent_name="GameActionFightEvent.Types",
                fields=[number_field("loss_")],
            )
            return PinnedResolveCase(
                PinnedPairsConfig(
                    pairs=[
                        PinnedPair(obf="ixc.iwj", non_obf=f"{GAME_NS}.GameActionFightEvent.LifePointsLost")
                    ]
                ),
                {},
                message_lookup(root, types, child),
                "ixc.iwj",
                "GameActionFightEvent.Types.LifePointsLost",
            )
        case "obf_static_container":
            parent = DumpCSMessage(file_descriptor="FD", name="iyw", fields=[number_field()])
            static_container = DumpCSMessage(file_descriptor="FD", name="iyv", parent_name="iyw")
            nested = DumpCSMessage(
                file_descriptor="FD",
                name="iyu",
                parent_name="iyw.iyv",
                fields=[number_field("fjai_")],
            )
            non_obf = DumpCSMessage(
                file_descriptor="FD",
                name="FightEntityState",
                namespace=FIGHT_NS,
                parent_name="FightLiveStateEvent",
            )
            return PinnedResolveCase(
                PinnedPairsConfig(
                    pairs=[
                        PinnedPair(
                            obf="iyw.iyu",
                            non_obf=f"{FIGHT_NS}.FightLiveStateEvent.FightEntityState",
                        )
                    ]
                ),
                message_lookup(parent, static_container, nested),
                message_lookup(non_obf),
                "iyw.iyv.iyu",
                non_obf.composed_name,
            )
        case _:
            raise ValueError(kind)


def pinned_resolve_error_case(kind: Literal["unknown", "ambiguous"]) -> PinnedResolveErrorCase:
    match kind:
        case "unknown":
            return PinnedResolveErrorCase(
                PinnedPairsConfig(pairs=[PinnedPair(obf="xyz", non_obf="UnknownMessage")]),
                {},
                {},
                "Unknown non-obf message alias",
            )
        case "ambiguous":
            outer = DumpCSMessage(file_descriptor="FD", name="Outer", fields=[number_field()])
            direct_child = DumpCSMessage(
                file_descriptor="FD",
                name="Inner",
                parent_name="Outer",
                fields=[number_field("direct_")],
            )
            types = DumpCSMessage(file_descriptor="FD", name="Types", parent_name="Outer")
            types_child = DumpCSMessage(
                file_descriptor="FD",
                name="Inner",
                parent_name="Outer.Types",
                fields=[number_field("types_")],
            )
            return PinnedResolveErrorCase(
                PinnedPairsConfig(pairs=[PinnedPair(obf="xyz", non_obf="Outer.Inner")]),
                {},
                message_lookup(outer, direct_child, types, types_child),
                "Ambiguous non-obf message alias",
            )


def snapshot_layout(tmp_path: Path) -> SnapshotLayout:
    return SnapshotLayout(
        real_game_dir=tmp_path / "real",
        snapshots_root=tmp_path / "D3",
        non_obf_game_dir=tmp_path / "D3" / "BETA",
    )


def write_real_game_files(real_game_dir: Path, *, mtime_ns: int) -> tuple[Path, Path]:
    metadata_dir = real_game_dir / "Dofus_Data" / "il2cpp_data" / "Metadata"
    metadata_dir.mkdir(parents=True)
    assembly = real_game_dir / "GameAssembly.dll"
    metadata = metadata_dir / "global-metadata.dat"
    assembly.write_bytes(b"real-assembly")
    metadata.write_bytes(b"real-metadata")
    set_mtime_ns(assembly, mtime_ns)
    set_mtime_ns(metadata, mtime_ns)
    return assembly, metadata


def write_snapshot(snapshot_dir: Path, *, assembly_mtime_ns: int) -> Path:
    snapshot_dir.mkdir(parents=True)
    assembly = snapshot_dir / "GameAssembly.dll"
    metadata = snapshot_dir / "global-metadata.dat"
    assembly.write_bytes(b"snapshot-assembly")
    metadata.write_bytes(b"snapshot-metadata")
    set_mtime_ns(assembly, assembly_mtime_ns)
    set_mtime_ns(metadata, assembly_mtime_ns)
    return snapshot_dir


def set_mtime_ns(path: Path, mtime_ns: int) -> None:
    os.utime(path, ns=(mtime_ns, mtime_ns))
