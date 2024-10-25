namespace IL2CppExtract.Metadata.IL2Cpp;

public class FieldDefinition
{
    public int NameIndex { get; set; }
    public int TypeIndex { get; set; }
    
    // Version <= 24
    public int CustomAttributeIndex { get; set; }
    
    // Version >= 19
    public uint Token { get; set; }
    
    public static int GetSize(double version)
    {
        if (version >= 24)
        {
            return 3 * sizeof(int);
        }
        
        if (version >= 19)
        {
            return 4 * sizeof(int);
        }
        
        return 2 * sizeof(int);
    }
    
    public static FieldDefinition Read(BinaryReader reader, double version)
    {
        return new FieldDefinition
        {
            NameIndex = reader.ReadInt32(),
            TypeIndex = reader.ReadInt32(),
            CustomAttributeIndex = version <= 24 ? reader.ReadInt32() : 0,
            Token = version >= 19 ? reader.ReadUInt32() : 0,
        };
    }
}