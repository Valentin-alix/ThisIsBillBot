import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from src.services.ai.human_response import HumanResponse
from src.services.ai.human_solo_talk import HumanSoloTalk
from src.services.ai.llm_classifier import ClassifierChat
from src.utils.metaclasses.singleton import Singleton


class TestLangchainServices(unittest.TestCase):
    def setUp(self) -> None:
        Singleton._instances.clear()

    def _fake_agent(self, content: str) -> object:
        return SimpleNamespace(
            invoke=Mock(return_value={"messages": [SimpleNamespace(content=content)]})
        )

    def test_classifier_chat_returns_boolean(self) -> None:
        with (
            patch("src.services.ai.llm_classifier.ChatOpenAI", return_value=object()),
            patch(
                "src.services.ai.llm_classifier.create_agent",
                return_value=self._fake_agent("oui"),
            ),
        ):
            classifier = ClassifierChat()
            self.assertTrue(classifier.llm_should_respond("hello"))

    def test_human_response_returns_reply(self) -> None:
        with (
            patch("src.services.ai.human_response.ChatOpenAI", return_value=object()),
            patch("src.services.ai.human_response.MemorySaver", return_value=object()),
            patch(
                "src.services.ai.human_response.create_agent",
                return_value=self._fake_agent("bon jeu"),
            ),
            patch(
                "src.services.ai.human_response.ClassifierChat",
                return_value=SimpleNamespace(
                    llm_should_respond=Mock(return_value=True)
                ),
            ),
        ):
            response = HumanResponse().get_human_response_to_private_msg(
                "salut", "sender", "from"
            )
            self.assertEqual(response, "bon jeu")

    def test_human_solo_talk_returns_reply(self) -> None:
        with (
            patch("src.services.ai.human_solo_talk.ChatOpenAI", return_value=object()),
            patch("src.services.ai.human_solo_talk.MemorySaver", return_value=object()),
            patch(
                "src.services.ai.human_solo_talk.create_agent",
                return_value=self._fake_agent("ok"),
            ),
        ):
            response = HumanSoloTalk().get_solo_human_talk_in_general_msg("sender")
            self.assertEqual(response, "ok")
