from typing import cast

from langchain_openai import ChatOpenAI


def get_human_response_to_private_msg(msg: str):
    model = ChatOpenAI(model="gpt-4.1-mini", temperature=0.8, top_p=0.6)
    messages = [
        (
            "system",
            "Tu es en train de récolter des ressources sur dofus pour monter tes métiers et te faire des kamas, parle comme un joueur Dofus : neutre, blasé, petites fautes, pas de ponctuation, jamais de questions, réponse courte (maximum 4 à 9 mots), si on te remercie, ou qu'on te réponds par une phrase du type ca marche ou ok par message alors souhaite lui bon jeu, tu n'es surtout pas un bot",
        ),
        ("human", msg),
    ]
    ai_msg = model.invoke(messages)
    return cast(str, ai_msg.content)


def get_solo_human_talk_in_general_msg():
    model = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7, top_p=0.6)
    messages = [
        (
            "system",
            "Tu es en train de récolter des ressources sur dofus, parle comme un joueur Dofus : neutre, blasé, petites fautes, pas de ponctuation, 3 à 6 mots maximum",
        )
    ]
    ai_msg = model.invoke(messages)
    return cast(str, ai_msg.content)
