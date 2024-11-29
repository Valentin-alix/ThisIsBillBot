class BaseMessage:
    content: str

    def __init__(self, content: str) -> None: ...


class HumanMessage(BaseMessage): ...


class SystemMessage(BaseMessage): ...
