using System.Text;

namespace IL2CppExtract.Assembly.Native;

[Flags]
public enum PESectionChararacteristics : uint
{
    ImageScnCntCode               = 0x00000020,
    ImageScnCntInitializedData   = 0x00000040,
    ImageScnCntUninitializedData = 0x00000080,
    ImageScnMemExecute            = 0x20000000,
    ImageScnMemRead               = 0x40000000,
    ImageScnMemWrite              = 0x80000000
}
public class PESection
{
    public required string Name { get; set; }
    public uint VirtualSize { get; set; } // Size in memory
    public uint VirtualAddress { get; set; }
    public uint SizeOfRawData { get; set; }
    public uint PointerToRawData { get; set; }
    public uint PointerToRelocations { get; set; }
    public uint PointerToLinenumbers { get; set; }
    public ushort NumberOfRelocations { get; set; }
    public ushort NumberOfLinenumbers { get; set; }
    public PESectionChararacteristics CharacteristicsValue { get; set; }
    
    public static PESection Read(BinaryReader reader)
    {
        return new PESection
        {
            Name = Encoding.UTF8.GetString(reader.ReadBytes(8)).TrimEnd('\0'),
            VirtualSize = reader.ReadUInt32(),
            VirtualAddress = reader.ReadUInt32(),
            SizeOfRawData = reader.ReadUInt32(),
            PointerToRawData = reader.ReadUInt32(),
            PointerToRelocations = reader.ReadUInt32(),
            PointerToLinenumbers = reader.ReadUInt32(),
            NumberOfRelocations = reader.ReadUInt16(),
            NumberOfLinenumbers = reader.ReadUInt16(),
            CharacteristicsValue = (PESectionChararacteristics)reader.ReadUInt32()
        };
    }
}