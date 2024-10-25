namespace IL2CppExtract.Metadata.IL2Cpp;

public class AssemblyNameDefinition
{
    public int NameIndex { get; set; }
    public int CultureIndex { get; set; }
    
    // Version <= 24.3
    public int HashValueIndex { get; set; }
    
    public int PublicKeyIndex { get; set; }
    
    // Version <= 15 (Array length = 8)
    public byte[] PublicKeyTokenOld { get; set; } = [];
    
    public uint HashAlgorithm { get; set; }
    public int HashLength { get; set; }
    
    public uint Flags { get; set; }
    public int Major { get; set; }
    public int Minor { get; set; }
    public int Build { get; set; }
    public int Revision { get; set; }
    
    // Version >= 16 (Array length = 8)
    public byte[] PublicKeyToken { get; set; } = [];
    
    public static AssemblyNameDefinition Read(BinaryReader reader, double version)
    { 
        return new AssemblyNameDefinition
        {
            NameIndex = reader.ReadInt32(),
            CultureIndex = reader.ReadInt32(),
            HashValueIndex = version <= 24.3 ? reader.ReadInt32() : 0,
            PublicKeyIndex = reader.ReadInt32(),
            PublicKeyTokenOld = version <= 15 ? reader.ReadBytes(8) : [],
            HashAlgorithm = reader.ReadUInt32(),
            HashLength = reader.ReadInt32(),
            Flags = reader.ReadUInt32(),
            Major = reader.ReadInt32(),
            Minor = reader.ReadInt32(),
            Build = reader.ReadInt32(),
            Revision = reader.ReadInt32(),
            PublicKeyToken = version >= 16 ? reader.ReadBytes(8) : [],
        };
    }

    public static int GetSize(double version)
    {
        if (version >= 29)
        {
            return 10 * sizeof(int) + 8;
        }
        
        throw new NotSupportedException($"Unsupported metadata version: {version}");
    }
}