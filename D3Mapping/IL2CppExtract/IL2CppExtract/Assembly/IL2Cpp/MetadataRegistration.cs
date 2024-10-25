namespace IL2CppExtract.Assembly.IL2Cpp;

public class MetadataRegistration
{
    public long GenericClassesCount { get; set; }
    public ulong GenericClasses { get; set; }
    public long GenericInstsCount { get; set; }
    public ulong GenericInsts { get; set; }
    public long GenericMethodTableCount { get; set; }
    public ulong GenericMethodTable { get; set; }
    public long TypesCount { get; set; }
    public ulong Types { get; set; }
    public long MethodSpecsCount { get; set; }
    public ulong MethodSpecs { get; set; }
    
    // Version <= 16
    public long MethodReferencesCount { get; set; }
    public ulong MethodReferences { get; set; }
    
    public long FieldOffsetsCount { get; set; }
    public ulong FieldOffsets { get; set; }
    public long TypeDefinitionsSizesCount { get; set; }
    public ulong TypeDefinitionsSizes { get; set; }
    
    // Version >= 19
    public long MetadataUsageCount { get; set; }
    public ulong MetadataUsage { get; set; }
    
    public static int GetSize(double version)
    {
        if(version >= 29)
        {
            return 16 * sizeof(long);
        }
        
        throw new NotSupportedException($"Unsupported metadata version: {version}");
    }
    
    public static MetadataRegistration Read(BinaryReader reader, double version)
    {
        return new MetadataRegistration
        {
            GenericClassesCount = reader.ReadInt64(),
            GenericClasses = reader.ReadUInt64(),
            GenericInstsCount = reader.ReadInt64(),
            GenericInsts = reader.ReadUInt64(),
            GenericMethodTableCount = reader.ReadInt64(),
            GenericMethodTable = reader.ReadUInt64(),
            TypesCount = reader.ReadInt64(),
            Types = reader.ReadUInt64(),
            MethodSpecsCount = reader.ReadInt64(),
            MethodSpecs = reader.ReadUInt64(),
            MethodReferencesCount = version <= 16 ? reader.ReadInt64() : 0,
            MethodReferences = version <= 16 ? reader.ReadUInt64() : 0,
            FieldOffsetsCount = reader.ReadInt64(),
            FieldOffsets = reader.ReadUInt64(),
            TypeDefinitionsSizesCount = reader.ReadInt64(),
            TypeDefinitionsSizes = reader.ReadUInt64(),
            MetadataUsageCount = version >= 19 ? reader.ReadInt64() : 0,
            MetadataUsage = version >= 19 ? reader.ReadUInt64() : 0,
        };
    }
}