from dataclasses import dataclass
from unittest.mock import patch

import src.services.ai.human_response as human_response


@dataclass
class FakeResponse:
    content: str


class FakeResponseModel:
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls: list[list[object]] = []

    def invoke(self, messages: list[object]) -> FakeResponse:
        self.calls.append(messages)
        return FakeResponse(self.content)


def test_private_message_uses_one_model_request() -> None:
    model = FakeResponseModel(" bon jeu ")

    with patch.object(human_response, "_response_model", return_value=model):
        response = human_response.get_private_message_response("merci")

    assert response == "bon jeu"
    assert len(model.calls) == 1
    assert len(model.calls[0]) == 2


def test_private_message_ignores_no_reply() -> None:
    model = FakeResponseModel("NO_REPLY")

    with patch.object(human_response, "_response_model", return_value=model):
        response = human_response.get_private_message_response("salut")

    assert response is None
