from pydantic import BaseModel

from scripts.generator.models.descriptor_enum_type import DescriptorEnumType
from scripts.generator.models.descriptor_message import DescriptorMessage


class Descriptor(BaseModel):
    name: str  # filename
    package: str | None = None
    enumType: list[DescriptorEnumType] = []
    messageType: list[DescriptorMessage]
    dependency: list[str] = []

    def get_top_content(self) -> str:
        top_content: str = 'syntax = "proto3";\n'
        top_content += f"package {self.package};\n"

        for dependency in self.dependency:
            sanitized_dependency = dependency.replace("includes/", "")
            if not sanitized_dependency.startswith("google"):
                continue
            top_content += f'import "{sanitized_dependency}";\n'

        return top_content

    def get_content(self) -> str:
        if not self.package:
            return ""

        top_content: str = self.get_top_content()
        imported_files: list[str] = []

        content: str = ""

        for enum_type in self.enumType:
            content += enum_type.get_content()

        for descriptor_msg in self.messageType:
            msg_top, msg_content = descriptor_msg.get_content(
                self.package, imported_files
            )
            top_content += msg_top
            content += msg_content

        return top_content + content
