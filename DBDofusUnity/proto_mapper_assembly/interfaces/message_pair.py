from typing import NamedTuple


class MatchPairKey(NamedTuple):
    obf_message_cls: str
    non_obf_message_cls: str
