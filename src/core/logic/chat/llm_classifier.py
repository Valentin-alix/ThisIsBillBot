from functools import cached_property

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_openai import ChatOpenAI

from src.interfaces.metaclasses.singleton import Singleton


class ClassifierChat(metaclass=Singleton):
    @cached_property
    def classifier_agent(self):
        classifier_model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
        return create_agent(classifier_model, tools=[])

    def llm_should_respond(self, msg: str) -> bool:
        result = self.classifier_agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=f"""Tu es un classifieur.
                                    Réponds uniquement par "oui" ou "non".
                                    Le message suivant nécessite-t-il une réponse utile ?
                                    - Réponds "oui" s'il contient une question, une demande, ou un souhait de bon jeu ou de bon farm, ou une affirmation selon laquel tu es un bot, ou que tu es report, une requête, une invitation à poursuivre la conversation, ou une salutation à laquelle il est naturel de répondre.
                                    - Réponds "non" si c'est juste un un acquiescement ou une réaction du genre mdr ou lol.

                                    Message : "{msg}"
                                    """
                    )
                ]
            }
        )

        answer = result["messages"][-1].content.strip().lower()
        return answer == "oui"
