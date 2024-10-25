namespace IL2CppExtract.Metadata.IL2Cpp;

public class MethodDefinition
{
    public int NameIndex { get; set; }
    
    // Version >= 16
    public int DeclaringType { get; set; }
    
    public int ReturnType { get; set; }
    public int ParameterStart { get; set; }
    
    // Version <= 24
    public int CustomAttributeIndex { get; set; }
    
    public int GenericContainerIndex { get; set; }
    
    // Version <= 24.1
    public int MethodIndex { get; set; }
    public int InvokerIndex { get; set; }
    public int ReversePInvokeWrapperIndex { get; set; }
    public int RgctxStartIndex { get; set; }
    public int RgctxCount { get; set; }
    
    public uint Token { get; set; }
    public ushort Flags { get; set; }
    public ushort IFlags { get; set; }
    public ushort Slot { get; set; }
    public ushort ParameterCount { get; set; }
    
    public static int GetSize(double version)
    {
        if (version >= 29)
        {
            return (4 * sizeof(ushort)) + (6 * sizeof(int));
        }    
        
        throw new Exception("Unsupported version");
    }
    
    public static MethodDefinition Read(BinaryReader reader, double version)
    {
        var def = new MethodDefinition
        {
            NameIndex = reader.ReadInt32()
        };

        if (version >= 16)
        {
            def.DeclaringType = reader.ReadInt32();
        }
        
        def.ReturnType = reader.ReadInt32();
        def.ParameterStart = reader.ReadInt32();
        
        if (version <= 24)
        {
            def.CustomAttributeIndex = reader.ReadInt32();
        }
        
        def.GenericContainerIndex = reader.ReadInt32();
        
        if (version <= 24.1)
        {
            def.MethodIndex = reader.ReadInt32();
            def.InvokerIndex = reader.ReadInt32();
            def.ReversePInvokeWrapperIndex = reader.ReadInt32();
            def.RgctxStartIndex = reader.ReadInt32();
            def.RgctxCount = reader.ReadInt32();
        }
        
        def.Token = reader.ReadUInt32();
        def.Flags = reader.ReadUInt16();
        def.IFlags = reader.ReadUInt16();
        def.Slot = reader.ReadUInt16();
        def.ParameterCount = reader.ReadUInt16();
        
        return def;
    }
}