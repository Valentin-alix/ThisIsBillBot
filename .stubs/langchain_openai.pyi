from langchain_core.language_models.chat_models import BaseChatModel


class ChatOpenAI(BaseChatModel):
    def __init__(self, model: str, temperature: float = 0, top_p: float | None = None) -> None: ...
