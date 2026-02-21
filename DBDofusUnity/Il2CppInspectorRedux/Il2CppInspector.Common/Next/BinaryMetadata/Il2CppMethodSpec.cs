using VersionedSerialization.Attributes;

namespace Il2CppInspector.Next.BinaryMetadata;

using MethodIndex = int;
using GenericInstIndex = int;

[VersionedStruct]
public partial record struct Il2CppMethodSpec
{
    public MethodIndex MethodDefinitionIndex;
    public GenericInstIndex ClassIndexIndex;
    public GenericInstIndex MethodIndexIndex;
}