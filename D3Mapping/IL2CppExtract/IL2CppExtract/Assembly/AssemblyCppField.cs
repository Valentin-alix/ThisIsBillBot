using System.Reflection;
using IL2CppExtract.Metadata.IL2Cpp;

namespace IL2CppExtract.Assembly;

public class AssemblyCppField
{   
    public FieldDefinition Definition { get; set; }
    public string Name { get; set; }
    public ulong DefaultValueMetadataAddress { get; set; }
    public object? DefaultValue { get; set; }
    public FieldAttributes Attributes { get; }
    public bool HasFieldRVA => (Attributes & FieldAttributes.HasFieldRVA) != 0;
    public TypeReference FieldType { get; set; }
    
    
    public AssemblyCppField(AssemblyCppType type, int fieldIndex, AssemblyFile pkg)
    {
        Definition = pkg.Metadata.Fields[fieldIndex];
        Name = pkg.Metadata.Strings[Definition.NameIndex];
        var fieldType = pkg.TypeReferences[Definition.TypeIndex];
        
        FieldType = TypeReference.FromReferenceIndex(type, Definition.TypeIndex);
        
        Attributes = (FieldAttributes) fieldType.Attrs;
        
        // Default initialization value if present
        if (pkg.Metadata.FieldDefaultDictionary.TryGetValue(fieldIndex, out (ulong address, object? variant) value)) 
        {
            DefaultValue = value.variant;
            DefaultValueMetadataAddress = value.address;
        }

        if (HasFieldRVA)
        {
            TypeContainer.RVAFields.Add(this);
        }
    }
    
    public byte[] GetFieldRVABuffer(AssemblyFile pkg)
    {
        if (!HasFieldRVA || DefaultValueMetadataAddress == 0)
        {
            return [];
        }

        if (FieldType.Value == null)
        {
            Console.WriteLine($"Field {Name} has FieldRVA but no type");
            return [];
        }
        
        pkg.Metadata.Reader.BaseStream.Seek((long)DefaultValueMetadataAddress, SeekOrigin.Begin);
        var preview = pkg.Metadata.Reader.ReadBytes(FieldType.Value.Sizes.NativeSize);
                
        if (preview.Length != FieldType.Value.Sizes.NativeSize)
        {
            throw new Exception("Field RVA preview read failed");
        }
        
        return preview;
    }




}