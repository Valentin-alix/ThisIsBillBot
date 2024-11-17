import ast
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from D3Mapping.d3_mapping.consts import PROTO_GAME_PATH, RESOURCE_PATH


@dataclass
class MessageFieldInfo:
    full_proto_name: str
    fields: dict[str, str] = field(default_factory=dict)
    nested_messages: dict[str, "MessageFieldInfo"] = field(default_factory=dict)


@dataclass
class ProtoRegistry:
    messages_by_simple_name: dict[str, MessageFieldInfo] = field(default_factory=dict)
    messages_by_full_name: dict[str, MessageFieldInfo] = field(default_factory=dict)


def parse_proto_files(proto_path: str) -> dict[str, str]:
    package_by_file: dict[str, str] = {}

    for proto_file in Path(proto_path).glob("*.proto"):
        with open(proto_file, "r", encoding="utf-8") as f:
            content = f.read()

        package_match = re.search(r"^package\s+([\w.]+)\s*;", content, re.MULTILINE)
        if package_match:
            package_name = package_match.group(1)
            file_stem = proto_file.stem
            package_by_file[file_stem] = package_name

    return package_by_file


def parse_pyi_files(proto_path: str, package_by_file: dict[str, str]) -> ProtoRegistry:
    registry = ProtoRegistry()

    for pyi_file in Path(proto_path).glob("*.pyi"):
        with open(pyi_file, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        file_stem = pyi_file.stem.replace("_pb2", "")
        package_name = package_by_file.get(
            file_stem, f"com.ankama.dofus.server.game.protocol.{file_stem}"
        )

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if _is_message_class(node):
                    _extract_message_info(node, registry, package_name, [])

    return registry


def _is_message_class(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Attribute):
            if base.attr == "Message":
                return True
        elif isinstance(base, ast.Subscript):
            if isinstance(base.value, ast.Attribute) and base.value.attr == "Message":
                return True
    return False


def _extract_message_info(
    node: ast.ClassDef,
    registry: ProtoRegistry,
    package_name: str,
    parent_path: list[str],
):
    current_path = parent_path + [node.name]

    if parent_path:
        full_proto_name = f".{package_name}.{'.'.join(current_path)}"
    else:
        full_proto_name = f".{package_name}.{node.name}"

    msg_info = MessageFieldInfo(full_proto_name=full_proto_name)

    slots_value: list[str] = []
    for item in node.body:
        if isinstance(item, ast.AnnAssign):
            if isinstance(item.target, ast.Name) and item.target.id == "__slots__":
                if isinstance(item.value, ast.Tuple):
                    for elt in item.value.elts:
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            slots_value.append(elt.value)

    for field_name in slots_value:
        msg_info.fields[field_name] = "unknown"

    for item in node.body:
        if isinstance(item, ast.ClassDef) and _is_message_class(item):
            _extract_message_info(item, registry, package_name, current_path)
            nested_name = ".".join(current_path + [item.name])
            nested_full = f".{package_name}.{nested_name}"
            if nested_full in registry.messages_by_full_name:
                msg_info.nested_messages[item.name] = registry.messages_by_full_name[
                    nested_full
                ]

    registry.messages_by_simple_name[node.name] = msg_info
    registry.messages_by_full_name[full_proto_name] = msg_info


def extract_imports_from_file(file_path: str) -> dict[str, str]:
    imports: dict[str, str] = {}

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if (
                node.module
                and "D3Mapping.d3_mapping.resources.protos.game" in node.module
            ):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports[name] = alias.name

    return imports


class FieldAccessVisitor(ast.NodeVisitor):
    def __init__(
        self,
        proto_imports: dict[str, str],
        registry: ProtoRegistry,
        type_hints: dict[str, str],
    ):
        self.proto_imports = proto_imports
        self.registry = registry
        self.type_hints = type_hints
        self.used_fields: dict[str, set[str]] = defaultdict(set)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "HasField":
            if node.args and isinstance(node.args[0], ast.Constant):
                field_name = node.args[0].value
                if isinstance(field_name, str):
                    var_name = self._get_root_var(node.func.value)
                    if var_name and var_name in self.type_hints:
                        msg_type = self.type_hints[var_name]
                        chain = self._get_attr_chain(node.func.value)
                        if chain and len(chain) > 1:
                            self._record_field_chain(msg_type, chain[1:] + [field_name])
                        else:
                            self._record_field(msg_type, field_name)

        if isinstance(node.func, ast.Name) and node.func.id in self.proto_imports:
            msg_name = self.proto_imports[node.func.id]
            if msg_name in self.registry.messages_by_simple_name:
                msg_info = self.registry.messages_by_simple_name[msg_name]
                for keyword in node.keywords:
                    if keyword.arg:
                        self.used_fields[msg_info.full_proto_name].add(keyword.arg)

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        chain = self._get_attr_chain(node)
        if chain and len(chain) > 1:
            root_var = chain[0]
            if root_var in self.type_hints:
                msg_type = self.type_hints[root_var]
                self._record_field_chain(msg_type, chain[1:])

        self.generic_visit(node)

    def _get_root_var(self, node: ast.expr) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_root_var(node.value)
        return None

    def _get_attr_chain(self, node: ast.expr) -> list[str]:
        chain: list[str] = []
        current = node

        while True:
            if isinstance(current, ast.Attribute):
                chain.insert(0, current.attr)
                current = current.value
            elif isinstance(current, ast.Name):
                chain.insert(0, current.id)
                break
            elif isinstance(current, ast.Subscript):
                current = current.value
            else:
                break

        return chain

    def _record_field(self, msg_type: str, field_name: str):
        if field_name in ("HasField", "WhichOneof", "ListFields", "SerializeToString"):
            return
        if msg_type in self.registry.messages_by_simple_name:
            msg_info = self.registry.messages_by_simple_name[msg_type]
            self.used_fields[msg_info.full_proto_name].add(field_name)

    def _record_field_chain(self, msg_type: str, fields: list[str]):
        if not fields:
            return

        if msg_type not in self.registry.messages_by_simple_name:
            return

        current_msg_info = self.registry.messages_by_simple_name[msg_type]
        current_full_name = current_msg_info.full_proto_name

        for field_name in fields:
            if not current_msg_info:
                break

            if field_name in (
                "HasField",
                "WhichOneof",
                "ListFields",
                "SerializeToString",
            ):
                continue

            self.used_fields[current_full_name].add(field_name)

            if field_name in current_msg_info.nested_messages:
                current_msg_info = current_msg_info.nested_messages[field_name]
                current_full_name = current_msg_info.full_proto_name


def extract_type_hints_from_function(
    func_node: ast.FunctionDef | ast.AsyncFunctionDef,
    proto_imports: dict[str, str],
) -> dict[str, str]:
    type_hints: dict[str, str] = {}

    for arg in func_node.args.args:
        if arg.annotation:
            type_name = _get_type_name(arg.annotation)
            if type_name and type_name in proto_imports:
                type_hints[arg.arg] = proto_imports[type_name]

    return type_hints


def _get_type_name(annotation: ast.expr) -> str | None:
    if isinstance(annotation, ast.Name):
        return annotation.id
    elif isinstance(annotation, ast.Attribute):
        return annotation.attr
    elif isinstance(annotation, ast.Subscript):
        return _get_type_name(annotation.value)
    return None


def analyze_file(file_path: str, registry: ProtoRegistry) -> dict[str, set[str]]:
    proto_imports = extract_imports_from_file(file_path)
    if not proto_imports:
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return {}

    all_used_fields: dict[str, set[str]] = defaultdict(set)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            type_hints = extract_type_hints_from_function(node, proto_imports)

            visitor = FieldAccessVisitor(proto_imports, registry, type_hints)
            visitor.visit(node)

            for msg_name, fields in visitor.used_fields.items():
                all_used_fields[msg_name].update(fields)

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "on":
                if node.args and isinstance(node.args[0], ast.Name):
                    msg_class = node.args[0].id
                    if msg_class in proto_imports:
                        original_name = proto_imports[msg_class]
                        if original_name in registry.messages_by_simple_name:
                            msg_info = registry.messages_by_simple_name[original_name]
                            all_used_fields[msg_info.full_proto_name]

    return all_used_fields


def extract_used_fields(src_dir: str, registry: ProtoRegistry) -> dict[str, set[str]]:
    all_used_fields: dict[str, set[str]] = defaultdict(set)

    for root, _, files in os.walk(src_dir):
        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)
            file_fields = analyze_file(file_path, registry)

            for msg_name, fields in file_fields.items():
                all_used_fields[msg_name].update(fields)

    return all_used_fields


CORE_MESSAGES: dict[str, list[str]] = {
    ".com.ankama.dofus.server.game.protocol.GameMessage": [
        "request",
        "response",
        "event",
    ],
    ".com.ankama.dofus.server.game.protocol.Request": ["uid", "content"],
    ".com.ankama.dofus.server.game.protocol.Response": ["uid", "content"],
    ".com.ankama.dofus.server.game.protocol.Event": ["content"],
}


def add_core_messages(used_fields: dict[str, set[str]]) -> None:
    for msg_name, fields in CORE_MESSAGES.items():
        used_fields[msg_name].update(fields)


def dump_all_used_fields():
    src_dir = os.path.join(Path(__file__).parent.parent.parent, "src")
    output_path = os.path.join(RESOURCE_PATH, "used_fields.json")

    print("Parsing protobuf package definitions...")
    package_by_file = parse_proto_files(PROTO_GAME_PATH)
    print(f"Found {len(package_by_file)} proto packages")

    print("Parsing protobuf message definitions...")
    registry = parse_pyi_files(PROTO_GAME_PATH, package_by_file)
    print(f"Found {len(registry.messages_by_full_name)} message types")

    print(f"Analyzing source files in {src_dir}...")
    used_fields = extract_used_fields(src_dir, registry)

    print("Adding core protocol messages...")
    add_core_messages(used_fields)

    print(f"Found fields used in {len(used_fields)} message types")

    output = {
        "_metadata": {
            "generated_at": datetime.now().isoformat(),
            "source_directory": str(src_dir),
            "total_messages": len(used_fields),
            "total_fields": sum(len(fields) for fields in used_fields.values()),
        },
        "messages": {k: sorted(v) for k, v in sorted(used_fields.items())},
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Output written to {output_path}")
    print(f"Total messages: {len(used_fields)}")
    print(f"Total fields: {sum(len(fields) for fields in used_fields.values())}")


if __name__ == "__main__":
    dump_all_used_fields()
