namespace IL2CppExtract.Metadata.IL2Cpp;

public class AssemblyDefinition
{
    public AssemblyNameDefinition Name => NameNew ?? NameOld ?? throw new Exception("Name is null");
    
    // Version <= 15
    public AssemblyNameDefinition? NameOld { get; set; }
    
    public int ImageIndex { get; set; }
    
    // Version >= 24.1
    public uint Token { get; set; }
    
    // Version < 24
    public int CustomAttributeIndex { get; set; }
    
    // Version >= 20
    public int ReferencedAssemblyStart { get; set; }
    public int ReferencedAssemblyCount { get; set; }
    
    // Version >= 16
    public AssemblyNameDefinition? NameNew { get; set; }
    
    public static AssemblyDefinition Read(BinaryReader reader, double version)
    {
        return new AssemblyDefinition
        {
            NameOld = version <= 15 ? AssemblyNameDefinition.Read(reader, version) : null,
            ImageIndex = reader.ReadInt32(),
            Token = version >= 24.1 ? reader.ReadUInt32() : 0,
            CustomAttributeIndex = version < 24 ? reader.ReadInt32() : 0,
            ReferencedAssemblyStart = version >= 20 ? reader.ReadInt32() : 0,
            ReferencedAssemblyCount = version >= 20 ? reader.ReadInt32() : 0,
            NameNew = version >= 16 ? AssemblyNameDefinition.Read(reader, version) : null,
        };
    }

    public static int GetSize(double version)
    {
        if (version >= 29)
        {
            return 4 * sizeof(int) + AssemblyNameDefinition.GetSize(version);
        }
        
        throw new NotSupportedException($"Unsupported metadata version: {version}");
    }
}