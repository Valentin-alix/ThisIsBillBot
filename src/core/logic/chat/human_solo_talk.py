from functools import cached_property
from typing import cast

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from openai import APIConnectionError, OpenAIError

from src.interfaces.metaclasses.singleton import Singleton


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
            return cast(str, ai_msg["messages"][-1].content)
        except (APIConnectionError, OpenAIError):
            return None
