import logging
import traceback
from functools import cached_property

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from openai import APIConnectionError, OpenAIError
from python_utils.singleton import Singleton

from src.const import ENV_PATH
from src.services.logging_utils.loggers import configure_root_logger

load_dotenv(ENV_PATH)

logger = logging.getLogger()


class HumanSoloTalk(metaclass=Singleton):
    @cached_property
    def solo_agent(self):
        system_prompt = (
            "Tu es en train de récolter des ressources sur dofus, ne sois jamais spécifique"
            "parle comme un joueur Dofus : neutre, petites fautes, pas de ponctuation"
        )

        solo_model = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.8,
            top_p=0.6,
        )
        solo_checkpointer = MemorySaver()
        return create_agent(
            solo_model,
            tools=[],
            checkpointer=solo_checkpointer,
            system_prompt=system_prompt,
        )

    def get_solo_human_talk_in_general_msg(self, sender_name: str) -> str | None:
        try:
            ai_msg = self.solo_agent.invoke(
                {"messages": [HumanMessage(content="dit une phrase")]},
                config={"configurable": {"thread_id": sender_name.__hash__()}},
            )
            return ai_msg["messages"][-1].content
        except (APIConnectionError, OpenAIError):
            logger.error(traceback.format_exc())
            return None


if __name__ == "__main__":
    configure_root_logger()
    print(HumanSoloTalk().get_solo_human_talk_in_general_msg("yolo"))
