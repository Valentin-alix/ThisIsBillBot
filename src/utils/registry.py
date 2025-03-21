import importlib
import os
import sys

from google.protobuf.message import Message


def import_and_get_all_msg_from_folder(folder_path: str):
    """Load all proto message types from a folder into memory (registers them in the descriptor pool)."""
    sys.path.append(folder_path)
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if not (filename.endswith(".py") and not filename.startswith("__")):
                continue
            module_name = filename[:-3]
            relative_module_path = os.path.relpath(root, folder_path).replace(
                os.sep, "."
            )
            if relative_module_path == ".":
                full_module_name = module_name
            else:
                full_module_name = f"{relative_module_path}.{module_name}"
            module = importlib.import_module(full_module_name)
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isinstance(attribute, type(Message)):
                    globals()[attribute_name] = attribute
