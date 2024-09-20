import importlib
import os
import sys
from inspect import isclass


def import_all_classes_from_folder(folder_path: str):
    """useful to load proto msg type in memory

    Args:
        folder_path (str): root folder
    """
    sys.path.append(folder_path)

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".py") and not filename.startswith("__"):
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
                    if isclass(attribute):
                        globals()[attribute_name] = attribute
