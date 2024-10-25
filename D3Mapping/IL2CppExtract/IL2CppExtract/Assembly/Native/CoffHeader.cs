namespace IL2CppExtract.Assembly.Native;

public class CoffHeader
{
    public ushort Machine { get; set; }
    public ushort NumberOfSections { get; set; }
    public uint TimeDateStamp { get; set; }
    public uint PointerToSymbolTable { get; set; }
    public uint NumberOfSymbols { get; set; }
    public ushort SizeOfOptionalHeader { get; set; }
    public ushort Characteristics { get; set; }
    
    public static CoffHeader Read(BinaryReader reader)
    {
        return new CoffHeader
        {
            Machine = reader.ReadUInt16(),
            NumberOfSections = reader.ReadUInt16(),
            TimeDateStamp = reader.ReadUInt32(),
            PointerToSymbolTable = reader.ReadUInt32(),
            NumberOfSymbols = reader.ReadUInt32(),
            SizeOfOptionalHeader = reader.ReadUInt16(),
            Characteristics = reader.ReadUInt16(),
        };
    }
}