namespace IL2CppExtract.Metadata.IL2Cpp;

// Unity 4.6.1p5 - first release, no global-metadata.dat
// Unity 5.2.0f3 -> v15
// Unity 5.3.0f4 -> v16
// Unity 5.3.2f1 -> v19
// Unity 5.3.3f1 -> v20
// Unity 5.3.5f1 -> v21
// Unity 5.5.0f3 -> v22
// Unity 5.6.0f3 -> v23
// Unity 2017.1.0f3 -> v24
// Unity 2018.3.0f2 -> v24.1
// Unity 2019.1.0f2 -> v24.2
// Unity 2019.3.7f1 -> v24.3
// Unity 2019.4.15f1 -> v24.4
// Unity 2019.4.21f1 -> v24.5
// Unity 2020.1.0f1 -> v24.3
// Unity 2020.1.11f1 -> v24.4
// Unity 2020.2.0f1 -> v27
// Unity 2020.2.4f1 -> v27.1
// Unity 2021.1.0f1 -> v27.2
// https://unity3d.com/get-unity/download/archive
// Metadata version is written at the end of Unity.IL2CPP.MetadataCacheWriter.WriteLibIl2CppMetadata or WriteMetadata (Unity.IL2CPP.dll)

// From il2cpp-metadata.h
public class MetadataHeader
{
    public uint Signature { get; set; }
    public int Version { get; set; }
    public int StringLiteralOffset { get; set; } // string data for managed code
    public int StringLiteralCount { get; set; }
    public int StringLiteralDataOffset { get; set; }
    public int StringLiteralDataCount { get; set; }
    public int StringOffset { get; set; } // string data for managed code
    public int StringCount { get; set; }
    public int EventsOffset { get; set; } // Il2CppEventDefinition
    public int EventsCount { get; set; }
    public int PropertiesOffset { get; set; } // Il2CppPropertyDefinition
    public int PropertiesCount { get; set; }
    public int MethodsOffset { get; set; } // Il2CppMethodDefinition
    public int MethodsCount { get; set; }
    
    // Version >= 16
    public int ParameterDefaultValuesOffset { get; set; } // Il2CppParameterDefaultValue
    public int ParameterDefaultValuesCount { get; set; }
    
    public int FieldDefaultValuesOffset { get; set; } // Il2CppFieldDefaultValue
    public int FieldDefaultValuesCount { get; set; }
    public int FieldAndParameterDefaultValueDataOffset { get; set; } // uint8_t
    public int FieldAndParameterDefaultValueDataCount { get; set; }
    
    // Version >= 16
    public int FieldMarshaledSizesOffset { get; set; } // Il2CppFieldMarshaledSize
    public int FieldMarshaledSizesCount { get; set; }
    
    public int ParametersOffset { get; set; } // Il2CppParameterDefinition
    public int ParametersCount { get; set; }
    public int FieldsOffset { get; set; } // Il2CppFieldDefinition
    public int FieldsCount { get; set; }
    public int GenericParametersOffset { get; set; } // Il2CppGenericParameter
    public int GenericParametersCount { get; set; }
    public int GenericParameterConstraintsOffset { get; set; } // TypeIndex
    public int GenericParameterConstraintsCount { get; set; }
    public int GenericContainersOffset { get; set; } // Il2CppGenericContainer
    public int GenericContainersCount { get; set; }
    public int NestedTypesOffset { get; set; } // TypeDefinitionIndex
    public int NestedTypesCount { get; set; }
    public int InterfacesOffset { get; set; } // TypeIndex
    public int InterfacesCount { get; set; }
    public int VTableMethodsOffset { get; set; } // EncodedMethodIndex
    public int VTableMethodsCount { get; set; }
    public int InterfaceOffsetsOffset { get; set; } // Il2CppInterfaceOffsetPair
    public int InterfaceOffsetsCount { get; set; }
    public int TypeDefinitionsOffset { get; set; } // Il2CppTypeDefinition
    public int TypeDefinitionsCount { get; set; }
    
    // Version <= 24.1
    public int RgctxEntriesOffset { get; set; } // Il2CppRGCTXDefinition
    public int RgctxEntriesCount { get; set; }
    
    // Version >= 16
    public int ImagesOffset { get; set; } // Il2CppImageDefinition
    public int ImagesCount { get; set; }
    public int AssembliesOffset { get; set; }
    public int AssembliesCount { get; set; }
    
    // Version >= 19 && Version < 24.5
    public int MetadataUsageListsOffset { get; set; } // Il2CppMetadataUsageList
    public int MetadataUsageListsCount { get; set; }
    public int MetadataUsagePairsOffset { get; set; } // Il2CppMetadataUsagePair
    public int MetadataUsagePairsCount { get; set; }
    
    // Version >= 19
    public int FieldRefsOffset { get; set; } // Il2CppFieldRef
    public int FieldRefsCount { get; set; }
    
    // Version >= 20
    public int ReferencedAssembliesOffset { get; set; }
    public int ReferencedAssembliesCount { get; set; }
    
    // Version >= 21 && Version < 27.2
    public int AttributesInfoOffset { get; set; }
    public int AttributesInfoCount { get; set; }
    public int AttributeTypesOffset { get; set; }
    public int AttributeTypesCount { get; set; }
    
    // Version >= 29
    public uint AttributeDataOffset { get; set; }
    public int AttributeDataSize { get; set; }
    public uint AttributeDataRangeOffset { get; set; }
    public int AttributeDataRangeSize { get; set; }
    
    // Version >= 22
    public int UnresolvedVirtualCallParameterTypesOffset { get; set; }
    public int UnresolvedVirtualCallParameterTypesCount { get; set; }
    public int UnresolvedVirtualCallParameterRangesOffset { get; set; }
    public int UnresolvedVirtualCallParameterRangesCount { get; set; }
    
    // Version >= 23
    public int WindowsRuntimeTypeNamesOffset { get; set; }
    public int WindowsRuntimeTypeNamesSize { get; set; }
    
    // Version >= 27
    public int WindowsRuntimeStringsOffset { get; set; }
    public int WindowsRuntimeStringsSize { get; set; }
    
    // Version >= 24
    public int ExportedTypeDefinitionsOffset { get; set; }
    public int ExportedTypeDefinitionsCount { get; set; }

    public static MetadataHeader Read(BinaryReader reader)
    {
        var signature = reader.ReadUInt32();
        
        if (signature != 0xFAB11BAF)
            throw new Exception("Invalid metadata signature " + signature.ToString("X"));
        
        var version = reader.ReadInt32();
        
        return new MetadataHeader
        {
            Signature = signature,
            Version = version,
            StringLiteralOffset = reader.ReadInt32(),
            StringLiteralCount = reader.ReadInt32(),
            StringLiteralDataOffset = reader.ReadInt32(),
            StringLiteralDataCount = reader.ReadInt32(),
            StringOffset = reader.ReadInt32(),
            StringCount = reader.ReadInt32(),
            EventsOffset = reader.ReadInt32(),
            EventsCount = reader.ReadInt32(),
            PropertiesOffset = reader.ReadInt32(),
            PropertiesCount = reader.ReadInt32(),
            MethodsOffset = reader.ReadInt32(),
            MethodsCount = reader.ReadInt32(),
            ParameterDefaultValuesOffset = version >= 16 ? reader.ReadInt32() : 0,
            ParameterDefaultValuesCount = version >= 16 ? reader.ReadInt32() : 0,
            FieldDefaultValuesOffset = reader.ReadInt32(),
            FieldDefaultValuesCount = reader.ReadInt32(),
            FieldAndParameterDefaultValueDataOffset = reader.ReadInt32(),
            FieldAndParameterDefaultValueDataCount = reader.ReadInt32(),
            FieldMarshaledSizesOffset = reader.ReadInt32(),
            FieldMarshaledSizesCount = reader.ReadInt32(),
            ParametersOffset = version >= 16 ? reader.ReadInt32() : 0,
            ParametersCount = version >= 16 ? reader.ReadInt32() : 0,
            FieldsOffset = reader.ReadInt32(),
            FieldsCount = reader.ReadInt32(),
            GenericParametersOffset = reader.ReadInt32(),
            GenericParametersCount = reader.ReadInt32(),
            GenericParameterConstraintsOffset = reader.ReadInt32(),
            GenericParameterConstraintsCount = reader.ReadInt32(),
            GenericContainersOffset = reader.ReadInt32(),
            GenericContainersCount = reader.ReadInt32(),
            NestedTypesOffset = reader.ReadInt32(),
            NestedTypesCount = reader.ReadInt32(),
            InterfacesOffset = reader.ReadInt32(),
            InterfacesCount = reader.ReadInt32(),
            VTableMethodsOffset = reader.ReadInt32(),
            VTableMethodsCount = reader.ReadInt32(),
            InterfaceOffsetsOffset = reader.ReadInt32(),
            InterfaceOffsetsCount = reader.ReadInt32(),
            TypeDefinitionsOffset = reader.ReadInt32(),
            TypeDefinitionsCount = reader.ReadInt32(),
            RgctxEntriesOffset = version <= 24.1 ? reader.ReadInt32() : 0,
            RgctxEntriesCount = version <= 24.1 ? reader.ReadInt32() : 0,
            ImagesOffset = version >= 16 ? reader.ReadInt32() : 0,
            ImagesCount = version >= 16 ? reader.ReadInt32() : 0,
            AssembliesOffset = version >= 16 ? reader.ReadInt32() : 0,
            AssembliesCount = version >= 16 ? reader.ReadInt32() : 0,
            MetadataUsageListsOffset = version >= 19 && version < 24.5 ? reader.ReadInt32() : 0,
            MetadataUsageListsCount = version >= 19 && version < 24.5 ? reader.ReadInt32() : 0,
            MetadataUsagePairsOffset = version >= 19 && version < 24.5 ? reader.ReadInt32() : 0,
            MetadataUsagePairsCount = version >= 19 && version < 24.5 ? reader.ReadInt32() : 0,
            FieldRefsOffset = version >= 19 ? reader.ReadInt32() : 0,
            FieldRefsCount = version >= 19 ? reader.ReadInt32() : 0,
            ReferencedAssembliesOffset = version >= 20 ? reader.ReadInt32() : 0,
            ReferencedAssembliesCount = version >= 20 ? reader.ReadInt32() : 0,
            AttributesInfoOffset = version >= 21 && version < 27.2 ? reader.ReadInt32() : 0,
            AttributesInfoCount = version >= 21 && version < 27.2 ? reader.ReadInt32() : 0,
            AttributeTypesOffset = version >= 21 && version < 27.2 ? reader.ReadInt32() : 0,
            AttributeTypesCount = version >= 21 && version < 27.2 ? reader.ReadInt32() : 0,
            AttributeDataOffset = version >= 29 ? reader.ReadUInt32() : 0,
            AttributeDataSize = version >= 29 ? reader.ReadInt32() : 0,
            AttributeDataRangeOffset = version >= 29 ? reader.ReadUInt32() : 0,
            AttributeDataRangeSize = version >= 29 ? reader.ReadInt32() : 0,
            UnresolvedVirtualCallParameterTypesOffset = version >= 22 ? reader.ReadInt32() : 0,
            UnresolvedVirtualCallParameterTypesCount = version >= 22 ? reader.ReadInt32() : 0,
            UnresolvedVirtualCallParameterRangesOffset = version >= 22 ? reader.ReadInt32() : 0,
            UnresolvedVirtualCallParameterRangesCount = version >= 22 ? reader.ReadInt32() : 0,
            WindowsRuntimeTypeNamesOffset = version >= 23 ? reader.ReadInt32() : 0,
            WindowsRuntimeTypeNamesSize = version >= 23 ? reader.ReadInt32() : 0,
            WindowsRuntimeStringsOffset = version >= 27 ? reader.ReadInt32() : 0,
            WindowsRuntimeStringsSize = version >= 27 ? reader.ReadInt32() : 0,
            ExportedTypeDefinitionsOffset = version >= 24 ? reader.ReadInt32() : 0,
            ExportedTypeDefinitionsCount = version >= 24 ? reader.ReadInt32() : 0
        };
    }

    
}