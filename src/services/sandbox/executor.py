import ast
import io
import traceback
from collections.abc import Callable
from contextlib import redirect_stdout
from dataclasses import dataclass

from google.protobuf.message import Message
from google.protobuf.message_factory import GetMessageClass

from src.services.background import run_in_background
from src.services.hotreload.reloader import ReloadReport, reload_core_modules
from DBDofusUnity.consts import PINNED_PAIRS_FILE
from DBDofusUnity.proto_mapper_assembly.controllers.pinned_pairs import upsert_pinned_field_mapping, upsert_pinned_pair
from src.core.behaviors.behavior import Behavior
from src.core.bot.bot import Bot
from src.protocol.message_names import find_non_obf_game_message_descriptor, load_non_obf_game_message_full_names
from src.protocol.protocol_game import add_pinned_pair_to_game_mappings

_END_SENTINEL_MODULE_NAME = "<sandbox>"


@dataclass
class SandboxResult:
    stdout: str
    result_repr: str | None
    error: str | None


def _resolve_message_class(name: str) -> type[Message]:
    descriptor = find_non_obf_game_message_descriptor(name)
    if descriptor is None:
        raise ValueError(f"Unknown message {name!r}")
    return GetMessageClass(descriptor)


def _resolve_behavior(bot: Bot, name: str) -> Behavior:
    try:
        return next(behavior for behavior in bot.usable_behaviors if behavior.__class__.__name__ == name)
    except StopIteration:
        raise ValueError(f"Unknown behavior {name!r}") from None


@dataclass
class SandboxExecutor:
    bot: Bot

    def build_namespace(self) -> dict[str, object]:
        return {
            "bot": self.bot,
            "game_state": self.bot.game_state,
            "event_manager": self.bot.event_manager,
            "behaviors": {behavior.__class__.__name__: behavior for behavior in self.bot.usable_behaviors},
            "send_message": self.send_message,
            "trigger_behavior": self.trigger_behavior,
            "replay_behavior": self.replay_behavior,
            "add_pinned_pair": self.add_pinned_pair,
            "list_behaviors": self.list_behaviors,
            "list_messages": self.list_messages,
            "describe_message": self.describe_message,
            "reload": self.reload,
        }

    def list_behaviors(self) -> dict[str, str]:
        return {behavior.__class__.__name__: behavior.state.name for behavior in self.bot.usable_behaviors}

    def list_messages(self, contains: str = "") -> list[str]:
        names = load_non_obf_game_message_full_names()
        if not contains:
            return names
        lowered = contains.lower()
        return [name for name in names if lowered in name.lower()]

    def describe_message(self, name: str) -> list[str]:
        descriptor = find_non_obf_game_message_descriptor(name)
        if descriptor is None:
            raise ValueError(f"Unknown message {name!r}")
        return list(descriptor.fields_by_name.keys())

    def reload(self) -> ReloadReport:
        return reload_core_modules()

    def send_message(self, name: str, **fields: object) -> None:
        message_class = _resolve_message_class(name)
        self.bot.event_manager.send(message_class(**fields))

    def trigger_behavior(self, name: str) -> None:
        _resolve_behavior(self.bot, name)
        self.bot.behavior_coordinator.on_play_usable_behavior(name)

    def add_pinned_pair(
        self,
        obf_msg_name: str,
        non_obf_msg_name: str,
        field_mapping_by_obf: dict[str, str] | None = None,
    ) -> None:
        upsert_pinned_pair(PINNED_PAIRS_FILE, obf_msg_name, non_obf_msg_name)
        for obf_field_name, non_obf_field_name in (field_mapping_by_obf or {}).items():
            upsert_pinned_field_mapping(
                PINNED_PAIRS_FILE, obf_msg_name, non_obf_msg_name, obf_field_name, non_obf_field_name
            )
        add_pinned_pair_to_game_mappings(
            obf_msg_namespace=obf_msg_name,
            non_obf_msg_namespace=non_obf_msg_name,
            field_mapping=field_mapping_by_obf,
        )

    def replay_behavior(self, name: str) -> None:
        behavior = _resolve_behavior(self.bot, name)

        def _replay(_progress: Callable[[str], None]) -> None:
            behavior.replay_run()

        run_in_background(_replay)

    def run(self, code: str) -> SandboxResult:
        namespace = self.build_namespace()
        stdout = io.StringIO()
        try:
            tree = ast.parse(code, filename=_END_SENTINEL_MODULE_NAME, mode="exec")
            last_expr: ast.Expression | None = None
            if tree.body and isinstance(tree.body[-1], ast.Expr):
                last_stmt = tree.body.pop()
                assert isinstance(last_stmt, ast.Expr)
                last_expr = ast.Expression(last_stmt.value)

            with redirect_stdout(stdout):
                exec(
                    compile(tree, filename=_END_SENTINEL_MODULE_NAME, mode="exec"),
                    namespace,
                )
                result_repr = None
                if last_expr is not None:
                    result = eval(  # noqa: S307
                        compile(last_expr, filename=_END_SENTINEL_MODULE_NAME, mode="eval"),
                        namespace,
                    )
                    if result is not None:
                        result_repr = repr(result)
        except Exception:
            return SandboxResult(stdout=stdout.getvalue(), result_repr=None, error=traceback.format_exc())

        return SandboxResult(stdout=stdout.getvalue(), result_repr=result_repr, error=None)


ExecutorFactory = Callable[[str], SandboxExecutor | None]
