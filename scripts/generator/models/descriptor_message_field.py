from enum import StrEnum

from pydantic import BaseModel


class DescriptorFieldTypeEnum(StrEnum):
    STRING = "TYPE_STRING"
    FLOAT = "TYPE_FLOAT"
    MESSAGE = "TYPE_MESSAGE"
    INTEGER_64 = "TYPE_INT64"
    INTEGER_32 = "TYPE_INT32"
    BOOLEAN = "TYPE_BOOL"
    ENUM = "TYPE_ENUM"


class DescriptorLabelEnum(StrEnum):
    OPTIONAL = "LABEL_OPTIONAL"
    REPEATED = "LABEL_REPEATED"


class DescriptorMessageField(BaseModel):
    name: str
    number: int
    label: DescriptorLabelEnum
    type: DescriptorFieldTypeEnum
    typeName: str | None = None
    oneofIndex: int | None = None
    proto3Optional: bool = False

    def get_import(self, package: str) -> str:
        top_content: str = ""

        if (
            self.type in [DescriptorFieldTypeEnum.MESSAGE, DescriptorFieldTypeEnum.ENUM]
            and self.typeName is not None
            and package not in self.typeName
            and not self.typeName.startswith(".google")
        ):
            related_file = "/".join(self.typeName[1:].split(".")[:-1])

            related_import_file = f'import "{related_file}.proto";\n'

            top_content += related_import_file

        return top_content

    def get_type(self) -> str:
        extra_field_type_content: str = ""

        if self.proto3Optional:
            extra_field_type_content += "optional "

        if self.label == DescriptorLabelEnum.REPEATED:
            extra_field_type_content += "repeated "

        if self.type == DescriptorFieldTypeEnum.STRING:
            return extra_field_type_content + "string"
        if self.type == DescriptorFieldTypeEnum.FLOAT:
            return extra_field_type_content + "float"
        if self.type == DescriptorFieldTypeEnum.BOOLEAN:
            return extra_field_type_content + "bool"
        if self.type == DescriptorFieldTypeEnum.INTEGER_32:
            return extra_field_type_content + "int32"
        if self.type == DescriptorFieldTypeEnum.INTEGER_64:
            return extra_field_type_content + "int64"
        if self.typeName is None:
            raise ValueError(
                "Type Name should be defined if field type is not basic type"
            )

        return extra_field_type_content + self.typeName
