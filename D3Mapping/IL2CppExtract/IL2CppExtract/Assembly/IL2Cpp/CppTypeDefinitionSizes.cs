namespace IL2CppExtract.Assembly.IL2Cpp;

public class CppTypeDefinitionSizes
{
    public uint InstanceSize { get; set; }
    public int NativeSize { get; set; }
    public uint StaticFieldsSize { get; set; }
    public uint ThreadStaticFieldsSize { get; set; }
    
    public static CppTypeDefinitionSizes Read(BinaryReader reader)
    {
        return new CppTypeDefinitionSizes
        {
            InstanceSize = reader.ReadUInt32(),
            NativeSize = reader.ReadInt32(),
            StaticFieldsSize = reader.ReadUInt32(),
            ThreadStaticFieldsSize = reader.ReadUInt32(),
        };
    }
}