namespace IL2CppExtract.Assembly.IL2Cpp;

public class CppArrayType
{
    public ulong EType { get; set; }
    public byte Rank { get; set; }
    public byte NumSizes { get; set; }
    public byte NumLoBounds { get; set; }
    public ulong Sizes { get; set; }
    public ulong LoBounds { get; set; }
    
    public static CppArrayType Read(BinaryReader reader)
    {
        return new CppArrayType
        {
            EType = reader.ReadUInt64(),
            Rank = reader.ReadByte(),
            NumSizes = reader.ReadByte(),
            NumLoBounds = reader.ReadByte(),
            Sizes = reader.ReadUInt64(),
            LoBounds = reader.ReadUInt64(),
        };
    }
}