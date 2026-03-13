import functools
import re

_CLR_TYPE_MODIFIER_PATTERN = re.compile(r"\b(?:static|readonly)\b")
_WHITESPACE_PATTERN = re.compile(r"\s+")

_REPEATED_PREFIX = "RepeatedField<"
_REPEATED_SUFFIX = ">"
_MAP_PREFIX = "MapField<"
_MAP_SUFFIX = ">"
_MAP_TYPE_ARGUMENT_COUNT = 2


def split_top_level_tokens(raw_value: str) -> list[str]:
    tokens: list[str] = []
    current_token: list[str] = []
    angle_depth = 0
    bracket_depth = 0
    paren_depth = 0
    for character in raw_value:
        if character == "," and angle_depth == 0 and bracket_depth == 0 and paren_depth == 0:
            token = "".join(current_token).strip()
            if token:
                tokens.append(token)
            current_token = []
            continue
        current_token.append(character)
        if character == "<":
            angle_depth += 1
        elif character == ">":
            angle_depth = max(angle_depth - 1, 0)
        elif character == "[":
            bracket_depth += 1
        elif character == "]":
            bracket_depth = max(bracket_depth - 1, 0)
        elif character == "(":
            paren_depth += 1
        elif character == ")":
            paren_depth = max(paren_depth - 1, 0)
    final_token = "".join(current_token).strip()
    if final_token:
        tokens.append(final_token)
    return tokens


def extract_repeated_inner_type(normalized_type: str) -> str | None:
    if not normalized_type.startswith(_REPEATED_PREFIX) or not normalized_type.endswith(_REPEATED_SUFFIX):
        return None
    return normalized_type[len(_REPEATED_PREFIX) : -len(_REPEATED_SUFFIX)].strip()


def extract_map_inner_types(normalized_type: str) -> tuple[str, str] | None:
    if not normalized_type.startswith(_MAP_PREFIX) or not normalized_type.endswith(_MAP_SUFFIX):
        return None
    inner_types = normalized_type[len(_MAP_PREFIX) : -len(_MAP_SUFFIX)].strip()
    tokenized_inner_types = split_top_level_tokens(inner_types)
    if len(tokenized_inner_types) != _MAP_TYPE_ARGUMENT_COUNT:
        return None
    return tokenized_inner_types[0], tokenized_inner_types[1]


@functools.lru_cache(maxsize=512)
def normalize_clr_type(clr_type: str) -> str:
    without_modifiers = _CLR_TYPE_MODIFIER_PATTERN.sub("", clr_type)
    normalized_whitespace = _WHITESPACE_PATTERN.sub(" ", without_modifiers).strip()
    return (
        normalized_whitespace.replace(" <", "<")
        .replace("< ", "<")
        .replace(" >", ">")
        .replace("> ", ">")
        .replace(" ,", ",")
        .replace(", ", ",")
    )
