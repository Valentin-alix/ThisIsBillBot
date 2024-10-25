namespace IL2CppExtract.Metadata.IL2Cpp;

public class ImageDefinition
{
    public int NameIndex { get; set; }
    public int AssemblyIndex { get; set; }
    public int TypeStart { get; set; }
    public uint TypeCount { get; set; }
    
    // Version >= 24
    public int ExportedTypeStart { get; set; }
    public uint ExportedTypeCount { get; set; }
    
    public int EntryPointIndex { get; set; }
    
    // Version >= 19
    public uint Token { get; set; }
    
    // Version >= 24.1
    public int CustomAttributeStart { get; set; }
    public uint CustomAttributeCount { get; set; }
    
    public static int GetSize(double version)
    {
        if (version >= 24.1)
        {
            return 10 * sizeof(int);
        }
        
        if (version <= 24)
        {
            return 8 * sizeof(int);
        }
        
        return 5 * sizeof(int) + sizeof(uint);
    }
    

    public static ImageDefinition Read(BinaryReader reader, double version)
    {
        return new ImageDefinition
        {
            NameIndex = reader.ReadInt32(),
            AssemblyIndex = reader.ReadInt32(),
            TypeStart = reader.ReadInt32(),
            TypeCount = reader.ReadUInt32(),
            ExportedTypeStart = version >= 24 ? reader.ReadInt32() : 0,
            ExportedTypeCount = version >= 24 ? reader.ReadUInt32() : 0,
            EntryPointIndex = reader.ReadInt32(),
            Token = version >= 19 ? reader.ReadUInt32() : 0,
            CustomAttributeStart = version >= 24.1 ? reader.ReadInt32() : 0,
            CustomAttributeCount = version >= 24.1 ? reader.ReadUInt32() : 0,
        };
    }
}