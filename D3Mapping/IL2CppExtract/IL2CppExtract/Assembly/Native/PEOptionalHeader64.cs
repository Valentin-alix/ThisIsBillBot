namespace IL2CppExtract.Assembly.Native;

public class RvaEntry
{
    public uint VirtualAddress { get; set; }
    public uint Size { get; set; }
    
    public static RvaEntry[] ReadArray(BinaryReader reader, int count)
    {
        var entries = new RvaEntry[count];
        
        for (var i = 0; i < count; i++)
        {
            entries[i] = new RvaEntry
            {
                VirtualAddress = reader.ReadUInt32(),
                Size = reader.ReadUInt32()
            };
        }
        
        return entries;
    }
}

public class PEOptionalHeader64
{
    public const int MagicNumber = 0x20b;
    
    public ushort Magic { get; set; }
    public byte MajorLinkerVersion { get; set; }
    public byte MinorLinkerVersion { get; set; }
    public uint SizeOfCode { get; set; }
    public uint SizeOfInitializedData { get; set; }
    public uint SizeOfUninitializedData { get; set; }
    public uint AddressOfEntryPoint { get; set; }
    public uint BaseOfCode { get; set; }
    public ulong ImageBase { get; set; }
    public uint SectionAlignment { get; set; }
    public uint FileAlignment { get; set; }
    public ushort MajorOSVersion { get; set; }
    public ushort MinorOSVersion { get; set; }
    public ushort MajorImageVersion { get; set; }
    public ushort MinorImageVersion { get; set; }
    public ushort MajorSubsystemVersion { get; set; }
    public ushort MinorSubsystemVersion { get; set; }
    public uint Win32VersionValue { get; set; }
    public uint SizeOfImage { get; set; }
    public uint SizeOfHeaders { get; set; }
    public uint Checksum { get; set; }
    public ushort Subsystem { get; set; }
    public ushort DLLCharacteristics { get; set; }
    public ulong SizeOfStackReserve { get; set; }
    public ulong SizeOfStackCommit { get; set; }
    public ulong SizeOfHeapReserve { get; set; }
    public ulong SizeOfHeapCommit { get; set; }
    public uint LoaderFlags { get; set; }
    public uint NumberOfRvaAndSizes { get; set; }
    
    public RvaEntry[] DataDirectory { get; set; } = [];
    
    public static PEOptionalHeader64 Read(BinaryReader reader)
    {
        var magic = reader.ReadUInt16();

        if(magic != MagicNumber)
        {
            throw new Exception($"Invalid PE Optional Header Magic number: {magic}");
        }
        
        var header = new PEOptionalHeader64
        {
            Magic = magic,
            MajorLinkerVersion = reader.ReadByte(),
            MinorLinkerVersion = reader.ReadByte(),
            SizeOfCode = reader.ReadUInt32(),
            SizeOfInitializedData = reader.ReadUInt32(),
            SizeOfUninitializedData = reader.ReadUInt32(),
            AddressOfEntryPoint = reader.ReadUInt32(),
            BaseOfCode = reader.ReadUInt32(),
            ImageBase = reader.ReadUInt64(),
            SectionAlignment = reader.ReadUInt32(),
            FileAlignment = reader.ReadUInt32(),
            MajorOSVersion = reader.ReadUInt16(),
            MinorOSVersion = reader.ReadUInt16(),
            MajorImageVersion = reader.ReadUInt16(),
            MinorImageVersion = reader.ReadUInt16(),
            MajorSubsystemVersion = reader.ReadUInt16(),
            MinorSubsystemVersion = reader.ReadUInt16(),
            Win32VersionValue = reader.ReadUInt32(),
            SizeOfImage = reader.ReadUInt32(),
            SizeOfHeaders = reader.ReadUInt32(),
            Checksum = reader.ReadUInt32(),
            Subsystem = reader.ReadUInt16(),
            DLLCharacteristics = reader.ReadUInt16(),
            SizeOfStackReserve = reader.ReadUInt64(),
            SizeOfStackCommit = reader.ReadUInt64(),
            SizeOfHeapReserve = reader.ReadUInt64(),
            SizeOfHeapCommit = reader.ReadUInt64(),
            LoaderFlags = reader.ReadUInt32(),
            NumberOfRvaAndSizes = reader.ReadUInt32(),
        };
        
        header.DataDirectory = RvaEntry.ReadArray(reader, (int)header.NumberOfRvaAndSizes);
        
        return header;
    }
}