import re
import unicodedata
from functools import lru_cache

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    without_accents = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return " ".join(without_accents.casefold().split())


def get_reply_text(reply_id: int) -> str | None:
    i18n_id = DataReader().npc_reply_i18n_by_reply_id.get(reply_id)
    if i18n_id is None:
        return None
    return I18N().name_by_id.get(i18n_id)


def get_question_text(message_id: int) -> str | None:
    i18n_id = DataReader().npc_message_i18n_by_message_id.get(message_id)
    if i18n_id is None:
        return None
    return I18N().name_by_id.get(i18n_id)


@lru_cache(maxsize=512)
def _compile(pattern: str) -> re.Pattern[str]:
    return re.compile(normalize(pattern))


def matches(pattern: str, text: str | None) -> bool:
    if text is None:
        return False
    return _compile(pattern).search(normalize(text)) is not None


def find_npc_reply_ids_matching(npc_id: int, pattern: str) -> list[int]:
    reply_ids = DataReader().npc_reply_ids_by_npc_id.get(npc_id, [])
    return [reply_id for reply_id in reply_ids if matches(pattern, get_reply_text(reply_id))]
