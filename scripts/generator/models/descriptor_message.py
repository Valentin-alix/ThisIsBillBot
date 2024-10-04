from collections import OrderedDict

from pydantic import BaseModel

from scripts.generator.models.descriptor_enum_type import DescriptorEnumType
from scripts.generator.models.descriptor_message_field import (
    DescriptorMessageField,
)


class OneOfDecl(BaseModel):
    name: str


class DescriptorMessage(BaseModel):
    name: str
    field: list[DescriptorMessageField] = []
    nestedType: list["DescriptorMessage"] = []
    enumType: list[DescriptorEnumType] = []
    oneofDecl: list[OneOfDecl] = []

    def get_content(self, package: str, imported_files: list[str]) -> tuple[str, str]:
        top_content: str = ""
        msg_content: str = f"message {self.name}" + "{\n"
        one_of_contents: OrderedDict[str, str] = OrderedDict()

        for one_of_decl in self.oneofDecl:
            one_of_contents[one_of_decl.name] = f"oneof {one_of_decl.name}" + "{\n"

        for nested_descriptor_msg in self.nestedType:
            sub_top_content, sub_content = nested_descriptor_msg.get_content(
                package, imported_files
            )
            top_content += sub_top_content
            msg_content += sub_content

        for enum_type in self.enumType:
            msg_content += enum_type.get_content()

        for field in self.field:
            protoc_import_content = field.get_import(package)
            if protoc_import_content not in imported_files:
                imported_files.append(protoc_import_content)
                top_content += protoc_import_content

            field_content = f"\t{field.get_type()} {field.name} = {field.number};\n"
            if (
                field.oneofIndex is not None
                and (
                    related_one_of_declr := list(one_of_contents.keys())[
                        field.oneofIndex
                    ]
                )[0]
                != "_"
            ):
                one_of_contents[related_one_of_declr] += field_content
            else:
                msg_content += field_content

        for one_of_decl in self.oneofDecl:
            if one_of_decl.name[0] == "_":
                continue
            one_of_contents[one_of_decl.name] += "}\n"
            msg_content += one_of_contents[one_of_decl.name]

        msg_content += "}\n"

        return top_content, msg_content
