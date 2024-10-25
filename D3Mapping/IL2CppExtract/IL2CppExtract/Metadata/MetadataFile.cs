using System.Text;
using IL2CppExtract.Assembly;
using IL2CppExtract.Assembly.IL2Cpp;
using IL2CppExtract.Metadata.IL2Cpp;
using IL2CppExtract.Reader;

namespace IL2CppExtract.Metadata;

public record ConstantBlobArrayElement(TypeDefinition? TypeDef, object? Value, CppTypeEnum TypeEnum);
public record ConstantBlobArray(TypeDefinition? ArrayTypeDef, ConstantBlobArrayElement[] Elements, CppTypeEnum ArrayTypeEnum);

public class MetadataFile
{
    public required MetadataHeader Header { get; set; }
    public required ImageDefinition[] Images { get; set; }
    public required TypeDefinition[] Types { get; set; }
    public required FieldDefinition[] Fields { get; set; }
    public required FieldDefaultValue[] FieldDefaultValues { get; set; }
    public required AssemblyDefinition[] Assemblies { get; set; }
    public required MethodDefinition[] Methods { get; set; }
    public Dictionary<int, (ulong, object?)> FieldDefaultDictionary { get; set; } = new Dictionary<int, (ulong, object?)>();

    public double Version { get; set; }
    public required BinaryReader Reader { get; init; }

    public required Dictionary<int, string> Strings { get; set; } = new Dictionary<int, string>();
    
    public static MetadataFile Read(FileStream stream)
    {
        var reader = new BinaryReader(stream);
        var header = MetadataHeader.Read(reader);

        if (header.Version > 29)
        {
            throw new NotSupportedException($"Unsupported metadata version: {header.Version}");
        }
        
        if(reader.BaseStream.Position != header.StringLiteralOffset)
        {
            throw new Exception($"Unexpected position: {reader.BaseStream.Position} != {header.StringLiteralOffset}");
        }
        
        var images = Array.Empty<ImageDefinition>();
        
        if (header.Version >= 16)
        {
            // we read images size array
            var count = header.ImagesCount / ImageDefinition.GetSize(header.Version);
            var offset = header.ImagesOffset;
            images = new ImageDefinition[count];
            
            reader.BaseStream.Seek(offset, SeekOrigin.Begin);
            
            for (var i = 0; i < count; i++)
            {
                images[i] = ImageDefinition.Read(reader, header.Version);
            }
        }

        var strings = new Dictionary<int, string>();
        
        reader.BaseStream.Seek(header.StringOffset, SeekOrigin.Begin);

        while (reader.BaseStream.Position < header.StringOffset + header.StringCount)
        {
            var index = (int)(reader.BaseStream.Position - header.StringOffset);
            var str = ReaderUtils.ReadNullTerminatedString(reader);
            strings[index] = str;
        }

        var fields = ReadFields(header, reader);
        var fieldsDefaultValues = ReadFieldsDefaultValues(header, reader);
        
        return new MetadataFile()
        {
            Header = header,
            Images = images,
            Types =  ReadTypes(header, reader),
            Fields = fields,
            FieldDefaultValues = fieldsDefaultValues, 
            Assemblies = ReadAssemblies(header, reader),
            Methods = ReadMethods(header, reader),
            Strings = strings,
            Version = header.Version,
            Reader = reader
        };
    }
    
    public void GenerateFieldDefaultDictionary(AssemblyFile file)
    {
        var dictionary = new Dictionary<int, (ulong, object?)>();
        
        foreach (var field in FieldDefaultValues)
        {
            var (value, obj) = GetDefaultValue(field.TypeIndex, field.DataIndex, file, Header);
            dictionary[field.FieldIndex] = (value, obj);
        }
        
        FieldDefaultDictionary = dictionary;
    }

    public (ulong, object?) GetDefaultValue(int typeIndex, int dataIndex, AssemblyFile file, MetadataHeader header)
    {
        // No default
        if (dataIndex == -1)
            return (0ul, null);
        
        // Get pointer in binary to default value
        var pValue = header.FieldAndParameterDefaultValueDataOffset + dataIndex;
        var typeRef = file.TypeReferences[typeIndex];

        // Default value is null
        if (pValue == 0)
            return (0ul, null);

        Reader.BaseStream.Seek(pValue, SeekOrigin.Begin);
        var obj = GetConstantValueFromBlob(file, typeRef.Type);
        return ((ulong)pValue, obj);
    }

    public object? GetConstantValueFromBlob(AssemblyFile file, CppTypeEnum type)
    {       
        const byte kArrayTypeWithDifferentElements = 1;
        object? value = null;

        switch (type)
        {
            case CppTypeEnum.Il2CppTypeBoolean:
                value = Reader.ReadBoolean();
                break;
            case CppTypeEnum.Il2CppTypeU1:
            case CppTypeEnum.Il2CppTypeI1:
                value = Reader.ReadByte();
                break;
            case CppTypeEnum.Il2CppTypeChar:
                // UTF-8 character assumed
                value = BitConverter.ToChar(Reader.ReadBytes(2), 0);
                break;
            case CppTypeEnum.Il2CppTypeU2:
                value = Reader.ReadUInt16();
                break;
            case CppTypeEnum.Il2CppTypeI2:
                value = Reader.ReadInt16();
                break;
            case CppTypeEnum.Il2CppTypeU4:
                value = ReadCompressedUInt32(Reader, Version);
                break;
            case CppTypeEnum.Il2CppTypeI4:
                value = ReadCompressedInt32(Reader, Version);
                break;
            case CppTypeEnum.Il2CppTypeU8:
                value = Reader.ReadUInt64();
                break;
            case CppTypeEnum.Il2CppTypeI8:
                value = Reader.ReadInt64();
                break;
            case CppTypeEnum.Il2CppTypeR4:
                value = Reader.ReadSingle();
                break;
            case CppTypeEnum.Il2CppTypeR8:
                value = Reader.ReadDouble();
                break;
            case CppTypeEnum.Il2CppTypeString:
                var uiLen = ReadCompressedInt32(Reader, Version);
                if (uiLen != -1)
                    value = Encoding.UTF8.GetString(Reader.ReadBytes(uiLen));

                break;
            case CppTypeEnum.Il2CppTypeSzarray:
                var length = ReadCompressedInt32(Reader, Version);
                if (length == -1)
                    break;
                
                // This is only used in custom arguments.
                // We actually want the reflection TypeInfo here, but as we do not have it yet
                // we store everything in a custom array type to be changed out later in the TypeModel.
                var arrayElementType = ReadEncodedTypeEnum(file, Reader, out var arrayElementDef);
                var arrayElementsAreDifferent = Reader.ReadByte();

                var array = new ConstantBlobArrayElement[length];
                if (arrayElementsAreDifferent == kArrayTypeWithDifferentElements)
                {
                    for (var i = 0; i < length; i++)
                    {
                        var elementType = ReadEncodedTypeEnum(file, Reader, out var elementTypeDef);
                        array[i] = new ConstantBlobArrayElement(elementTypeDef, GetConstantValueFromBlob(file, elementType), elementType);
                    }
                }
                else
                {
                    for (var i = 0; i < length; i++)
                    {
                        array[i] = new ConstantBlobArrayElement(arrayElementDef, GetConstantValueFromBlob(file, arrayElementType), arrayElementType);
                    }
                }

                value = new ConstantBlobArray(arrayElementDef, array, arrayElementType);
                break;
            case CppTypeEnum.Il2CppTypeClass:
            case CppTypeEnum.Il2CppTypeObject:
            case CppTypeEnum.Il2CppTypeGenericinst:
                break;
            case CppTypeEnum.Il2CppTypeIl2CppTypeIndex:
                var index = ReadCompressedInt32(Reader, Version);
                if (index != -1)
                    value = file.TypeReferences[index];
                break;
            
        }
        
        return value;
    }

    private CppTypeEnum ReadEncodedTypeEnum(AssemblyFile file, BinaryReader reader, out TypeDefinition? enumType)
    {
        enumType = null;

        var typeEnum = (CppTypeEnum)reader.ReadByte();
        
        if (typeEnum != CppTypeEnum.Il2CppTypeEnum)
            return typeEnum;
        
        var typeIndex = ReadCompressedInt32(Reader, Version);
        var typeHandle = (uint)file.TypeReferences[typeIndex].DataPoint;
        enumType = Types[typeHandle];

        var elementTypeHandle = file.TypeReferences[enumType.ElementTypeIndex].DataPoint;
        var elementType = Types[elementTypeHandle];
        typeEnum = file.TypeReferences[elementType.ByValTypeIndex].Type;

        return typeEnum;
    }

    private int ReadCompressedInt32(BinaryReader reader, double version)
    {
        if (version < 29)
        {
            return reader.ReadInt32();
        }
        
        var val = ReadCompressedUInt32(reader, version);
        
        if (val == uint.MaxValue)
            return int.MaxValue;

        var signFlag = val & 1;
        val >>= 1;

        return signFlag == 1 
            ? -(int) (val + 1) 
            : (int)val;
    }
    
    private uint ReadCompressedUInt32(BinaryReader reader, double version)
    {
        if (version < 29)
        {
            return reader.ReadUInt32();
        }
        
        var first = reader.ReadByte();
        
        if((first & 0x80) == 0)
        {
            return first;
        }

        if ((first & 0xc0) == 0x80)
        {
            return ((first & ~0x80u) << 8) | reader.ReadByte();
        }
        
        if ((first & 0xe0) == 0xc0)
            return ((first & ~0xc0u) << 24) | ((uint)reader.ReadByte() << 16) | ((uint)reader.ReadByte() << 8) | reader.ReadByte();

        
        return first switch
        {
            0xf0 => reader.ReadUInt32(),
            0xfe => uint.MaxValue - 1,
            0xff => uint.MaxValue,
            _ => throw new InvalidDataException("Invalid compressed integer format")
        };
    }
    
    private static MethodDefinition[] ReadMethods(MetadataHeader header, BinaryReader reader)
    {
        var count = header.MethodsCount / MethodDefinition.GetSize(header.Version);
        var offset = header.MethodsOffset;
        
        var methods = new MethodDefinition[count];
        reader.BaseStream.Seek(offset, SeekOrigin.Begin);
        
        for (var i = 0; i < count; i++)
        {
            methods[i] = MethodDefinition.Read(reader, header.Version);
        }
        
        return methods;
    }

    
    private static TypeDefinition[] ReadTypes(MetadataHeader header, BinaryReader reader)
    {
        var typesCount = header.TypeDefinitionsCount / TypeDefinition.GetSize(header.Version);
        var typesOffset = header.TypeDefinitionsOffset;
        
        var types = new TypeDefinition[typesCount];
        reader.BaseStream.Seek(typesOffset, SeekOrigin.Begin);
        
        for (var i = 0; i < typesCount; i++)
        {
            types[i] = TypeDefinition.Read(reader, header.Version);
        }
        return types;
    }
    
    private static AssemblyDefinition[] ReadAssemblies(MetadataHeader header, BinaryReader reader)
    {
        var assembliesCount = header.AssembliesCount / AssemblyDefinition.GetSize(header.Version);
        var assembliesOffset = header.AssembliesOffset;
        
        var assemblies = new AssemblyDefinition[assembliesCount];
        reader.BaseStream.Seek(assembliesOffset, SeekOrigin.Begin);
        
        for (var i = 0; i < assembliesCount; i++)
        {
            assemblies[i] = AssemblyDefinition.Read(reader, header.Version);
        }
        
        return assemblies;
    }
    
    private static FieldDefinition[] ReadFields(MetadataHeader header, BinaryReader reader)
    {
        var fieldsCount = header.FieldsCount / FieldDefinition.GetSize(header.Version);
        var fieldsOffset = header.FieldsOffset;
        
        var fields = new FieldDefinition[fieldsCount];
        reader.BaseStream.Seek(fieldsOffset, SeekOrigin.Begin);
        
        for (var i = 0; i < fieldsCount; i++)
        {
            fields[i] = FieldDefinition.Read(reader, header.Version);
        }
        
        return fields;
    }
    
    private static FieldDefaultValue[] ReadFieldsDefaultValues(MetadataHeader header, BinaryReader reader)
    {
        var fieldsCount = header.FieldDefaultValuesCount / FieldDefaultValue.GetSize(header.Version);
        var fieldsOffset = header.FieldDefaultValuesOffset;
        
        var fields = new FieldDefaultValue[fieldsCount];
        reader.BaseStream.Seek(fieldsOffset, SeekOrigin.Begin);
        
        for (var i = 0; i < fieldsCount; i++)
        {
            fields[i] = FieldDefaultValue.Read(reader, header.Version);
        }
        
        return fields;
    }
}