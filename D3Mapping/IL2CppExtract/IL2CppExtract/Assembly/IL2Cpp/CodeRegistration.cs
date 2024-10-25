namespace IL2CppExtract.Assembly.IL2Cpp;

public class CodeRegistration
{
    // Version <= 24.1
    public ulong MehodPointersCount { get; set; }
    public ulong MehodPointers { get; set; }
    
    public ulong ReversePInvokeWrappersCount { get; set; }
    public ulong ReversePInvokeWrappers { get; set; }
    
    // Version <= 22
    public ulong DelegateWrappersFromManagedToNativeCount { get; set; }
    public ulong DelegateWrappersFromManagedToNative { get; set; }
    public ulong MarshalingFunctionsCount { get; set; }
    public ulong MarshalingFunctions { get; set; }
    
    // Version >= 21 && Version <= 22
    public ulong CcwMarshalingFunctionsCount { get; set; }
    public ulong CcwMarshalingFunctions { get; set; }
    
    public ulong GenericMethodPointersCount { get; set; }
    public ulong GenericMethodPointers { get; set; }
    
    // Version >= 27.1 && Version == 24.5
    public ulong GenericAdjustorThunks { get; set; }
    
    public ulong InvokerPointersCount { get; set; }
    public ulong InvokerPointers { get; set; }
    
    // Version <= 24.5
    public ulong CustomAttributeCount { get; set; }
    public ulong CustomAttributeGenerators { get; set; }
    
    // Version >= 21 && Version <= 22
    public ulong GuildCount { get; set; }
    public ulong Guilds { get; set; }
    
    // Version >= 22 && Version <= 29
    public ulong UnresolvedVirtualCallCount { get; set; }
    
    // Version >= 29.1
    public ulong UnresolvedIndirectCallCount { get; set; }
    
    // Version => 22
    public ulong UnresolvedVirtualCallPointers { get; set; }
    
    // Version => 29.1
    public ulong UnresolvedIndirectCallPointers { get; set; }
    public ulong UnresolveStaticCallPointers { get; set; }
    
    // Version >= 23
    public ulong InteropDataCount { get; set; }
    public ulong InteropData { get; set; }
    
    // Version >= 24.3
    public ulong WindowsRuntimeFactoryCount { get; set; }
    public ulong WindowsRuntimeFactoryTable { get; set; }
    
    // Version >= 24.2
    public ulong CodeGenModulesCount { get; set; }
    public ulong CodeGenModules { get; set; }
    
    public static ulong GetSize(double version)
    {
        if (version >= 29.1)
        {
            return 18 * sizeof(ulong);
        }
        
        if (version == 29)
        {
            return 15 * sizeof(ulong);
        } 
        
        throw new NotSupportedException($"Unsupported version: {version}");
    }

    public static CodeRegistration Read(BinaryReader reader, double version)
    {
        var mehodPointersCount = version <= 24.1 ? reader.ReadUInt64() : 0;
        var mehodPointers = version <= 24.1 ? reader.ReadUInt64() : 0;
        var reversePInvokeWrappersCount = reader.ReadUInt64();
        var reversePInvokeWrappers = reader.ReadUInt64();
        var delegateWrappersFromManagedToNativeCount = version <= 22 ? reader.ReadUInt64() : 0;
        var delegateWrappersFromManagedToNative = version <= 22 ? reader.ReadUInt64() : 0;
        var marshalingFunctionsCount = version <= 22 ? reader.ReadUInt64() : 0;
        var marshalingFunctions = version <= 22 ? reader.ReadUInt64() : 0;
        var ccwMarshalingFunctionsCount = version >= 21 && version <= 22 ? reader.ReadUInt64() : 0;
        var ccwMarshalingFunctions = version >= 21 && version <= 22 ? reader.ReadUInt64() : 0;
        var genericMethodPointersCount = reader.ReadUInt64();
        var genericMethodPointers = reader.ReadUInt64();
        var genericAdjustorThunks = version is >= 27.1 or 24.5 ? reader.ReadUInt64() : 0;
        var invokerPointersCount = reader.ReadUInt64();
        var invokerPointers = reader.ReadUInt64();
        var customAttributeCount = version <= 24.5 ? reader.ReadUInt64() : 0;
        var customAttributeGenerators = version <= 24.5 ? reader.ReadUInt64() : 0;
        var guildCount = version >= 21 && version <= 22 ? reader.ReadUInt64() : 0;
        var guilds = version >= 21 && version <= 22 ? reader.ReadUInt64() : 0;
        var unresolvedVirtualCallCount = version >= 22 && version <= 29 ? reader.ReadUInt64() : 0;
        var unresolvedIndirectCallCount = version >= 29.1 ? reader.ReadUInt64() : 0;
        var unresolvedVirtualCallPointers = version >= 22 ? reader.ReadUInt64() : 0;
        var unresolvedIndirectCallPointers = version >= 29.1 ? reader.ReadUInt64() : 0;
        var unresolveStaticCallPointers = version >= 29.1 ? reader.ReadUInt64() : 0;
        var interopDataCount = version >= 23 ? reader.ReadUInt64() : 0;
        var interopData = version >= 23 ? reader.ReadUInt64() : 0;
        var windowsRuntimeFactoryCount = version >= 24.3 ? reader.ReadUInt64() : 0;
        var windowsRuntimeFactoryTable = version >= 24.3 ? reader.ReadUInt64() : 0;
        var codeGenModulesCount = version >= 24.2 ? reader.ReadUInt64() : 0;
        var codeGenModules = version >= 24.2 ? reader.ReadUInt64() : 0;

        return new CodeRegistration
        {
            MehodPointersCount = mehodPointersCount,
            MehodPointers = mehodPointers,
            ReversePInvokeWrappersCount = reversePInvokeWrappersCount,
            ReversePInvokeWrappers = reversePInvokeWrappers,
            DelegateWrappersFromManagedToNativeCount = delegateWrappersFromManagedToNativeCount,
            DelegateWrappersFromManagedToNative = delegateWrappersFromManagedToNative,
            MarshalingFunctionsCount = marshalingFunctionsCount,
            MarshalingFunctions = marshalingFunctions,
            CcwMarshalingFunctionsCount = ccwMarshalingFunctionsCount,
            CcwMarshalingFunctions = ccwMarshalingFunctions,
            GenericMethodPointersCount = genericMethodPointersCount,
            GenericMethodPointers = genericMethodPointers,
            GenericAdjustorThunks = genericAdjustorThunks,
            InvokerPointersCount = invokerPointersCount,
            InvokerPointers = invokerPointers,
            CustomAttributeCount = customAttributeCount,
            CustomAttributeGenerators = customAttributeGenerators,
            GuildCount = guildCount,
            Guilds = guilds,
            UnresolvedVirtualCallCount = unresolvedVirtualCallCount,
            UnresolvedIndirectCallCount = unresolvedIndirectCallCount,
            UnresolvedVirtualCallPointers = unresolvedVirtualCallPointers,
            UnresolvedIndirectCallPointers = unresolvedIndirectCallPointers,
            UnresolveStaticCallPointers = unresolveStaticCallPointers,
            InteropDataCount = interopDataCount,
            InteropData = interopData,
            WindowsRuntimeFactoryCount = windowsRuntimeFactoryCount,
            WindowsRuntimeFactoryTable = windowsRuntimeFactoryTable,
            CodeGenModulesCount = codeGenModulesCount,
            CodeGenModules = codeGenModules
        };
    }

}