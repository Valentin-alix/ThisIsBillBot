from functools import cached_property
from typing import cast

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from openai import APIConnectionError, OpenAIError

from src.core.logic.chat.llm_classifier import ClassifierChat
from src.interfaces.metaclasses.singleton import Singleton


class HumanResponse(metaclass=Singleton):
    @cached_property
    def response_agent(self):
        system_prompt = (
            "Tu es en train de récolter des ressources sur dofus pour monter tes "
            "métiers et te faire des kamas, parle comme un joueur Dofus : neutre, "
            "blasé, petites fautes,pas de majuscule ni de point, jamais de questions, réponse "
            "courte (3 à 10 mots grand maximum), si on te remercie ou qu'on te répond 'ca marche' ou 'ok', tu réponds "
            "uniquement : 'bon jeu' tu ne dis rien d'autre jamais de retour du style"
            "bon jeu à toi aussi ou équivalent, ne dis jamais que tu es un bot"
        )

        response_model = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.8,
            top_p=0.6,
        )
        response_checkpointer = MemorySaver()
        return create_agent(
            response_model,
            tools=[],
            checkpointer=response_checkpointer,
            system_prompt=system_prompt,
        )

    def get_human_response_to_private_msg(
        self, msg: str, sender_name: str, from_name: str
    ) -> str | None:
        agent = self.response_agent
        try:
            if not ClassifierChat().llm_should_respond(msg):
                return None
            ai_msg = agent.invoke(
                {"messages": [HumanMessage(content=msg)]},
                config={
                    "configurable": {"thread_id": (sender_name, from_name).__hash__()}
                },
            )
            return cast(str, ai_msg["messages"][-1].content)
        except (APIConnectionError, OpenAIError):
            return None
