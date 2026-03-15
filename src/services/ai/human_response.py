from functools import cache
from typing import Protocol, cast

_SYSTEM_PROMPT = (
    "You gather resources in Dofus to level professions and earn kamas. "
    "Speak like a Dofus player: neutral, jaded, small mistakes, no capitals or period, "
    "no questions, and a short response of 3 to 10 words. If someone thanks you or says "
    "'sounds good' or 'ok', reply only with 'good game'. Never say you are a bot. "
    "If no response is appropriate, reply with exactly NO_REPLY."
)


class _ModelResponse(Protocol):
    content: object


class _ResponseModel(Protocol):
    def invoke(self, messages: list[object]) -> _ModelResponse: ...


@cache
def _response_model() -> _ResponseModel:
    from langchain_openai import ChatOpenAI

    return cast(
        _ResponseModel,
        ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.8,
            top_p=0.6,
        ),
    )


def get_private_message_response(msg: str) -> str | None:
    from langchain_core.messages import HumanMessage, SystemMessage
    from openai import APIConnectionError, OpenAIError

    try:
        response = _response_model().invoke(
            [SystemMessage(content=_SYSTEM_PROMPT), HumanMessage(content=msg)]
        )
        if not isinstance(response.content, str):
            return None
        content = response.content.strip()
        return None if not content or content == "NO_REPLY" else content
    except (APIConnectionError, OpenAIError):
        return None
