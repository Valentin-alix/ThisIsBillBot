import re

from DBDofusUnity.proto_mapper_assembly.parsers._clr_type_utils import normalize_clr_type, split_top_level_tokens

CORE_METHOD_DECLARATION_RE = re.compile(
    r"^\s*(?P<declaration>.+?\([^;]*\))\s*;\s*//\s*"
    r"(?P<start>0x[0-9A-Fa-f]+)-(?P<end>0x[0-9A-Fa-f]+)\s*$"
)

CSHARP_DECLARATION_MODIFIERS: frozenset[str] = frozenset(
    {
        "public",
        "private",
        "protected",
        "internal",
        "static",
        "virtual",
        "override",
        "sealed",
        "abstract",
        "extern",
        "unsafe",
        "partial",
        "new",
        "async",
    }
)

CSHARP_PARAMETER_MODIFIERS: frozenset[str] = frozenset(
    {
        "ref",
        "out",
        "in",
        "params",
        "this",
        "scoped",
        "readonly",
    }
)

CSHARP_PARAMETER_NAME_RE = re.compile(r"\s+[A-Za-z_][A-Za-z0-9_]*$")


def canonicalize_csharp_method_declaration(declaration: str) -> str | None:
    stripped_declaration = declaration.strip()
    opening_paren_index = stripped_declaration.find("(")
    closing_paren_index = stripped_declaration.rfind(")")
    if opening_paren_index <= 0 or closing_paren_index <= opening_paren_index:
        return None
    head = stripped_declaration[:opening_paren_index].strip()
    params_raw = stripped_declaration[opening_paren_index + 1 : closing_paren_index]
    head_tokens = head.split()
    while head_tokens and head_tokens[0] in CSHARP_DECLARATION_MODIFIERS:
        head_tokens.pop(0)
    if not head_tokens:
        return None
    method_name = head_tokens[-1]
    return_type = " ".join(head_tokens[:-1]) if len(head_tokens) > 1 else None
    parameter_types = [
        normalize_csharp_parameter_type(parameter)
        for parameter in split_top_level_tokens(params_raw)
        if parameter.strip()
    ]
    if any(parameter_type is None for parameter_type in parameter_types):
        return None
    normalized_params = ", ".join(parameter_type for parameter_type in parameter_types if parameter_type)
    if return_type is None:
        return f"{method_name}({normalized_params})"
    return f"{return_type} {method_name}({normalized_params})"


def normalize_csharp_parameter_type(parameter: str) -> str | None:
    parameter_without_default = parameter.split("=", 1)[0].strip()
    if not parameter_without_default:
        return None
    normalized_parameter = CSHARP_PARAMETER_NAME_RE.sub("", parameter_without_default).strip()
    if not normalized_parameter:
        return None
    parameter_tokens = normalized_parameter.split()
    while parameter_tokens and parameter_tokens[0] in CSHARP_PARAMETER_MODIFIERS:
        parameter_tokens.pop(0)
    if not parameter_tokens:
        return None
    return " ".join(parameter_tokens)


def get_normalized_short_type_name(type_name: str) -> str:
    normalized_type = normalize_clr_type(type_name)
    stripped_type = normalized_type.split("[", maxsplit=1)[0].split("<", maxsplit=1)[0].strip()
    return stripped_type.rsplit(".", maxsplit=1)[-1].rsplit("+", maxsplit=1)[-1]
