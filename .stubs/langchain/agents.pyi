from collections.abc import Callable, Sequence
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver


class AgentGraph:
    def invoke(
        self,
        input: dict[str, list[BaseMessage]],
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> dict[str, list[BaseMessage]]: ...


def create_agent(
    model: str | BaseChatModel,
    tools: Sequence[BaseTool | Callable[..., Any] | dict[str, Any]] | None = None,
    *,
    system_prompt: str | SystemMessage | None = None,
    middleware: Sequence[object] = (),
    response_format: object | None = None,
    state_schema: type[object] | None = None,
    context_schema: type[object] | None = None,
    checkpointer: BaseCheckpointSaver[str] | None = None,
    store: object | None = None,
    interrupt_before: list[str] | None = None,
    interrupt_after: list[str] | None = None,
    debug: bool = False,
    name: str | None = None,
    cache: object | None = None,
) -> AgentGraph: ...
