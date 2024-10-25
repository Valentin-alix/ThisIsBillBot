namespace IL2CppExtract.Metadata.IL2Cpp;

public class TypeDefinition
{
    public int NameIndex { get; set; }
    public int NamespaceIndex { get; set; }
    
    // Version <= 24
    public int CustomAttributeIndex { get; set; }
    
    public int ByValTypeIndex { get; set; }
    
    // Version <= 24.5
    public int ByRefTypeIndex { get; set; }
    
    public int DeclaringTypeIndex { get; set; }
    public int ParentIndex { get; set; }
    public int ElementTypeIndex { get; set; }
    
    // Version <= 24.1
    public int RgctxStartIndex { get; set; }
    public int RgctxCount { get; set; }
    
    public int GenericContainerIndex { get; set; }
    
    // Version <= 22
    public int DelegateWrapperFromManagedToNativeIndex { get; set; }
    public int MarshallingFunctionsIndex { get; set; }
    
    // Version >= 21 && Version <= 22
    public int CCWFunctionIndex { get; set; }
    public int GuidIndex { get; set; }
    
    public uint Flags { get; set; }
    public int FieldStart { get; set; }
    public int MethodStart { get; set; }
    public int EventStart { get; set; }
    public int PropertyStart { get; set; }
    public int NestedTypeStart { get; set; }
    public int InterfaceStart { get; set; }
    public int VTableStart { get; set; }
    public int InterfaceOffsetsStart { get; set; }
    
    public ushort MethodCount { get; set; }
    public ushort PropertyCount { get; set; }
    public ushort FieldCount { get; set; }
    public ushort EventCount { get; set; }
    public ushort NestedTypeCount { get; set; }
    public ushort VTableCount { get; set; }
    public ushort InterfacesCount { get; set; }
    public ushort InterfaceOffsetsCount { get; set; }
 
    // bitfield to portably encode boolean values as single bits
    // 01 - valuetype;
    // 02 - enumtype;
    // 03 - has_finalize;
    // 04 - has_cctor;
    // 05 - is_blittable;
    // 06 - is_import; (from v22: is_import_or_windows_runtime)
    // 07-10 - One of nine possible PackingSize values (0, 1, 2, 4, 8, 16, 32, 64, or 128)
    // 11-14 - One of four possible ClassSize values (0, 1, 2, or 3)
    public uint Bitfield { get; set; }
    
    // Version >= 19
    public uint Token { get; set; }
    
    
    public static int GetSize(double version)
    {
        if (version >= 24.5)
        {
            return (18 * sizeof(int)) + (sizeof(ushort) * 8);
        }
        
        throw new NotSupportedException($"TODO: Implement a better way to calculate the size of TypeDefinition for version {version}");
    }
    
    public static TypeDefinition Read(BinaryReader reader, double version)
    {
        return new TypeDefinition
        {
            NameIndex = reader.ReadInt32(),
            NamespaceIndex = reader.ReadInt32(),
            CustomAttributeIndex = version <= 24 ? reader.ReadInt32() : 0,
            ByValTypeIndex = reader.ReadInt32(),
            ByRefTypeIndex = version <= 24.5 ? reader.ReadInt32() : 0,
            DeclaringTypeIndex = reader.ReadInt32(),
            ParentIndex = reader.ReadInt32(),
            ElementTypeIndex = reader.ReadInt32(),
            RgctxStartIndex = version <= 24.1 ? reader.ReadInt32() : 0,
            RgctxCount = version <= 24.1 ? reader.ReadInt32() : 0,
            GenericContainerIndex = reader.ReadInt32(),
            DelegateWrapperFromManagedToNativeIndex = version <= 22 ? reader.ReadInt32() : 0,
            MarshallingFunctionsIndex = version <= 22 ? reader.ReadInt32() : 0,
            CCWFunctionIndex = version >= 21 && version <= 22 ? reader.ReadInt32() : 0,
            GuidIndex = version is >= 21 and <= 22 ? reader.ReadInt32() : 0,
            Flags = reader.ReadUInt32(),
            FieldStart = reader.ReadInt32(),
            MethodStart = reader.ReadInt32(),
            EventStart = reader.ReadInt32(),
            PropertyStart = reader.ReadInt32(),
            NestedTypeStart = reader.ReadInt32(),
            InterfaceStart = reader.ReadInt32(),
            VTableStart = reader.ReadInt32(),
            InterfaceOffsetsStart = reader.ReadInt32(),
            MethodCount = reader.ReadUInt16(),
            PropertyCount = reader.ReadUInt16(),
            FieldCount = reader.ReadUInt16(),
            EventCount = reader.ReadUInt16(),
            NestedTypeCount = reader.ReadUInt16(),
            VTableCount = reader.ReadUInt16(),
            InterfacesCount = reader.ReadUInt16(),
            InterfaceOffsetsCount = reader.ReadUInt16(),
            Bitfield = reader.ReadUInt32(),
            Token = version >= 19 ? reader.ReadUInt32() : 0,
        };
    }
}