import logging


class ContextAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        context = self.extra.get("context") if self.extra else None
        if context:
            msg = f"[{context}] {msg}"
        return msg, kwargs
