import importlib
import pkgutil
from functools import cache

from google.protobuf.message import Message


@cache
def load_non_obf_game_message_names() -> list[str]:
    import datas.protos.non_obf.game as game_pkg

    names: set[str] = set()
    for module_info in pkgutil.walk_packages(
        game_pkg.__path__, f"{game_pkg.__name__}."
    ):
        if module_info.ispkg or module_info.name.endswith(".__init__"):
            continue
        module = importlib.import_module(module_info.name)
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if (
                isinstance(attribute, type)
                and issubclass(attribute, Message)
                and getattr(attribute, "DESCRIPTOR", None) is not None
            ):
                names.add(attribute.__name__)
    return sorted(names)
