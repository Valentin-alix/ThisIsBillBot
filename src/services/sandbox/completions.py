from dataclasses import dataclass
from typing import Any, cast

import jedi


@dataclass
class CompletionItem:
    name: str
    complete: str
    type: str


def get_completions(code: str, line: int, column: int, namespace: dict[str, object]) -> list[CompletionItem]:
    interpreter = cast(Any, jedi.Interpreter(code, [namespace]))
    completions = cast(list[Any], interpreter.complete(line=line, column=column))

    items: list[CompletionItem] = []
    for completion in completions:
        name = completion.name
        complete = completion.complete
        completion_type = completion.type
        assert isinstance(name, str)
        assert isinstance(complete, str)
        assert isinstance(completion_type, str)
        items.append(CompletionItem(name=name, complete=complete, type=completion_type))
    return items
