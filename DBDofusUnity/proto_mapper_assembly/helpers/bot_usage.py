import logging
import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from tqdm import tqdm

from DBDofusUnity.proto_mapper_assembly.helpers.proto_helpers import resolve_child_message_cls
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.interfaces.matching import MatchResult

_IMPORT_PATTERN = re.compile(
    r"from\s+datas\.protos\.non_obf\.game\.(\w+)_pb2\s+import\s+(\([^()]+\)|[^\n#]+)",
)
_IMPORTED_NAME_PATTERN = re.compile(r"\b([A-Z]\w+)\b")
_ATTR_ACCESS_PATTERN = re.compile(r"\.([a-z_][a-z0-9_]*)\b")

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BotUsage:
    bot_used_messages: frozenset[str]
    directly_imported_messages: frozenset[str]
    accessed_attrs_per_message: Mapping[str, frozenset[str]]


def analyze_bot_usage(
    messages_by_cls: Mapping[str, DumpCSMessage],
    src_root: Path,
) -> BotUsage:
    module_to_message: dict[tuple[str, str], str] = {}
    type_index_builder: dict[str, list[DumpCSMessage]] = defaultdict(list)
    for message in messages_by_cls.values():
        type_index_builder[message.name].append(message)
        if message.parent_name is not None or message.namespace is None:
            continue
        ns_last = message.namespace.rsplit(".", 1)[-1].lower()
        module_to_message[(ns_last, message.name)] = message.composed_name
    type_index: dict[str, tuple[DumpCSMessage, ...]] = {
        name: tuple(msgs) for name, msgs in type_index_builder.items()
    }

    accessed_attrs_per_message: dict[str, set[str]] = defaultdict(set)
    bot_used: set[str] = set()
    py_files = list(src_root.rglob("*.py"))
    for py_file in tqdm(py_files, "analyzing bot usage"):
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        file_imports: set[str] = set()
        for import_match in _IMPORT_PATTERN.finditer(text):
            module_seg = import_match.group(1)
            for short in _IMPORTED_NAME_PATTERN.findall(import_match.group(2)):
                composed = module_to_message.get((module_seg, short))
                if composed is not None:
                    file_imports.add(composed)
        if not file_imports:
            continue
        bot_used.update(file_imports)
        file_attrs = set(_ATTR_ACCESS_PATTERN.findall(text))
        for composed in file_imports:
            accessed_attrs_per_message[composed].update(file_attrs)

    directly_imported = frozenset(bot_used)

    mutable_messages_by_cls = dict(messages_by_cls)
    queue: list[str] = list(bot_used)
    while queue:
        composed = queue.pop()
        message = mutable_messages_by_cls.get(composed)
        if message is None:
            continue
        attrs = accessed_attrs_per_message[composed]
        for field in message.fields:
            if field.clean_field_name not in attrs:
                continue
            child_composed = resolve_child_message_cls(
                field=field,
                parent_message=message,
                messages_by_cls=mutable_messages_by_cls,
                type_index=type_index,
            )
            if child_composed is None or child_composed in bot_used:
                continue
            bot_used.add(child_composed)
            accessed_attrs_per_message[child_composed].update(attrs)
            queue.append(child_composed)

    return BotUsage(
        bot_used_messages=frozenset(bot_used),
        directly_imported_messages=directly_imported,
        accessed_attrs_per_message={
            composed: frozenset(attrs) for composed, attrs in accessed_attrs_per_message.items()
        },
    )


def log_missing_field_mappings(
    bot_usage: BotUsage,
    matches: Sequence[MatchResult],
    non_obf_messages_by_cls: Mapping[str, DumpCSMessage],
) -> None:
    total_messages = 0
    total_fields = 0
    for match in matches:
        composed = match.non_obf_signature.message_cls
        if composed not in bot_usage.directly_imported_messages:
            continue
        non_obf_message = non_obf_messages_by_cls.get(composed)
        if non_obf_message is None:
            continue

        declared_field_names = {
            field.clean_field_name for field in non_obf_message.fields if field.is_declared_proto_shape_field
        }
        accessed = bot_usage.accessed_attrs_per_message.get(composed, frozenset())
        mapped_field_names = set(match.field_mapping.values())
        missing = sorted((declared_field_names & accessed) - mapped_field_names)
        if not missing:
            continue

        total_messages += 1
        total_fields += len(missing)
        _logger.warning(
            "missing field mappings for %s: %s",
            non_obf_message.composed_name,
            ", ".join(missing),
        )

    if total_messages > 0:
        _logger.warning(
            "total %d messages with missing field mappings (%d fields)",
            total_messages,
            total_fields,
        )
