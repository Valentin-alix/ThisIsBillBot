from pydantic import BaseModel


class DescriptorEnumValueType(BaseModel):
    name: str
    number: int


class DescriptorEnumType(BaseModel):
    name: str
    value: list[DescriptorEnumValueType]

    def get_content(self) -> str:
        content: str = f"enum {self.name}" + "{\n"

        for enum_value in self.value:
            content += f"\t{enum_value.name} = {enum_value.number};\n"

        content += "}\n"
        return content
