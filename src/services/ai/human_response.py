from functools import cache
from typing import Protocol, cast

_SYSTEM_PROMPT = (
    "Tu recoltes des ressources sur Dofus pour monter tes metiers et gagner des kamas. "
    "Parle comme un joueur Dofus : neutre, blase, petites fautes, sans majuscule ni point, "
    "sans question, reponse courte de 3 a 10 mots. Si on te remercie ou on te dit 'ca marche' ou 'ok', "
    "reponds uniquement 'bon jeu'. Ne dis jamais que tu es un bot. Si aucune reponse n'est "
    "appropriee, reponds exactement NO_REPLY."
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
