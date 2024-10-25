import os

from proto_schema_parser import Message, Parser
from proto_schema_parser.ast import File, Package, Enum

from d3_mapping.factories.p_enum_factory import PEnumFactory
from d3_mapping.factories.p_message_factory import PMessageFactory
from d3_mapping.models.p_enum import PEnum
from d3_mapping.models.p_message import PMessage


class PNamespaceFactory:
    @staticmethod
    def create_namespace_on_directory(
        directory: str,
    ) -> tuple[dict[str, list[str]], dict[str, PMessage | PEnum]]:
        msg_by_namespace: dict[str, PMessage | PEnum] = {}
        root_namespaces_by_filename: dict[str, list[str]] = {}
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if not filename.endswith(".proto"):
                    continue
                with open(os.path.join(root, filename)) as file:
                    datas = file.read()
                parsed_proto = Parser().parse(datas)
                file_root_struct, file_namespace = (
                    PNamespaceFactory._get_namespace_for_file(parsed_proto)
                )
                root_namespaces_by_filename[filename] = file_root_struct
                msg_by_namespace |= file_namespace

        return root_namespaces_by_filename, msg_by_namespace

    @staticmethod
    def _get_namespace_for_file(
        proto_file: File,
    ) -> tuple[list[str], dict[str, PMessage | PEnum]]:
        namespace = ""
        struct_by_namespace: dict[str, PMessage | PEnum] = {}
        root_namespaces: list[str] = []
        for file_element in proto_file.file_elements:
            if type(file_element) is Package:
                namespace += "." + file_element.name + "."
            elif type(file_element) is Message:
                msg_namespace = namespace + file_element.name
                sub_namespace = PMessageFactory.create_p_messages_with_namespace(
                    file_element, msg_namespace
                )
                root_namespaces.append(msg_namespace)
                struct_by_namespace |= sub_namespace
            elif type(file_element) is Enum:
                enum_namespace = namespace + file_element.name
                struct_by_namespace[enum_namespace] = PEnumFactory.create_p_enum(
                    file_element, namespace=enum_namespace
                )
                root_namespaces.append(enum_namespace)
        return root_namespaces, struct_by_namespace
