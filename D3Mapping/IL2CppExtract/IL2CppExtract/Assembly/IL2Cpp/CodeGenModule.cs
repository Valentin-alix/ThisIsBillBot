namespace IL2CppExtract.Assembly.IL2Cpp;

public class CodeGenModule
{
    public ulong ModuleName { get; set; }
    public ulong MethodPointerCount { get; set; }
    public ulong MethodPointers { get; set; }
    
    // Version >= 24.5 && Version < 24.5 || Version >= 27.1
    public long AdjustorThunkCount { get; set; }
    public ulong AdjustorThunks { get; set; }
    
    public ulong InvokerIndices { get; set; }
    public ulong ReversePInvokeWrapperCount { get; set; }
    public ulong ReversePInvokeWrappersIndices { get; set; }
    public ulong RgctxRangesCount { get; set; }
    public ulong RgctxRanges { get; set; }
    public ulong RgcxtsCount { get; set; }
    public ulong Rgcxts { get; set; }
    public ulong DebuggerMetadata { get; set; }
    
    // Version >= 27 && Version <= 27.2
    public ulong CustomAttributeCacheGenerator { get; set; }
    
    // Version >= 27
    public ulong ModuleInitializer { get; set; }
    public ulong StaticConstructorTypeIndices { get; set; }
    public ulong MetadataRegistration { get; set; }
    public ulong CodeRegistration { get; set; }
    
    public static CodeGenModule Read(BinaryReader reader, double version)
    {
        return new CodeGenModule
        {
            ModuleName = reader.ReadUInt64(),
            MethodPointerCount = reader.ReadUInt64(),
            MethodPointers = reader.ReadUInt64(),
            AdjustorThunkCount = (Math.Abs(version - 24.5f) < 0.01 || version >= 27.1) ? reader.ReadInt64() : 0,
            AdjustorThunks = (Math.Abs(version - 24.5f) < 0.01 || version >= 27.1) ? reader.ReadUInt64() : 0,
            InvokerIndices = reader.ReadUInt64(),
            ReversePInvokeWrapperCount = reader.ReadUInt64(),
            ReversePInvokeWrappersIndices = reader.ReadUInt64(),
            RgctxRangesCount = reader.ReadUInt64(),
            RgctxRanges = reader.ReadUInt64(),
            RgcxtsCount = reader.ReadUInt64(),
            Rgcxts = reader.ReadUInt64(),
            DebuggerMetadata = reader.ReadUInt64(),
            CustomAttributeCacheGenerator = version >= 27 && version <= 27.2 ? reader.ReadUInt64() : 0,
            ModuleInitializer = version >= 27 ? reader.ReadUInt64() : 0,
            StaticConstructorTypeIndices = version >= 27 ? reader.ReadUInt64() : 0,
            MetadataRegistration = version >= 27 ? reader.ReadUInt64() : 0,
            CodeRegistration = version >= 27 ? reader.ReadUInt64() : 0,
        };
    }
}