from pydantic import BaseModel, Field


class MethodDefinition(BaseModel):
    virtual_address: str = Field(alias="virtualAddress")
    name: str
    signature: str
    dot_net_signature: str | None = Field(default=None, alias="dotNetSignature")
    group: str


class TypeInfoPointer(BaseModel):
    virtual_address: str = Field(alias="virtualAddress")
    name: str
    type: str
    dot_net_type: str = Field(alias="dotNetType")


class MethodInfoPointer(BaseModel):
    virtual_address: str = Field(alias="virtualAddress")
    name: str
    dot_net_signature: str = Field(alias="dotNetSignature")
    method_address: str | None = Field(default=None, alias="methodAddress")


class Il2CppApiDefinition(BaseModel):
    virtual_address: str = Field(alias="virtualAddress")
    name: str
    signature: str | None = None


class AddressMap(BaseModel):
    method_definitions: list[MethodDefinition] = Field(alias="methodDefinitions")
    method_info_pointers: list[MethodInfoPointer] = Field(
        default_factory=list[MethodInfoPointer], alias="methodInfoPointers"
    )
    type_info_pointers: list[TypeInfoPointer] = Field(
        default_factory=list[TypeInfoPointer], alias="typeInfoPointers"
    )
    apis: list[Il2CppApiDefinition] = Field(default_factory=list[Il2CppApiDefinition])
    exports: list[Il2CppApiDefinition] = Field(default_factory=list[Il2CppApiDefinition])


class Il2CppJson(BaseModel):
    address_map: AddressMap = Field(alias="addressMap")
