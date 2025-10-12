from src.core.bot.bot import Bot
from src.services.sandbox.completions import get_completions


class _Foo:
    def bar(self) -> None:
        pass

    baz = 1


def test_get_completions_on_plain_object_attribute() -> None:
    code = "foo.b"
    completions = get_completions(code, line=1, column=len(code), namespace={"foo": _Foo()})

    names = {item.name for item in completions}
    assert names == {"bar", "baz"}


def test_get_completions_returns_suffix_to_insert() -> None:
    code = "foo.ba"
    completions = get_completions(code, line=1, column=len(code), namespace={"foo": _Foo()})

    (baz_completion,) = [item for item in completions if item.name == "baz"]
    assert baz_completion.complete == "z"


def test_get_completions_against_live_bot(runtime_bot: Bot) -> None:
    code = "bot.game_stat"
    completions = get_completions(code, line=1, column=len(code), namespace={"bot": runtime_bot})

    names = {item.name for item in completions}
    assert "game_state" in names


def test_get_completions_on_unknown_root_returns_empty() -> None:
    code = "not_in_namespace.attr"
    completions = get_completions(code, line=1, column=len(code), namespace={})

    assert completions == []
