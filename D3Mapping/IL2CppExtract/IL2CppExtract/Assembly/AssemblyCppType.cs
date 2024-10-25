using System.Reflection;
using System.Text.RegularExpressions;
using IL2CppExtract.Assembly.IL2Cpp;
using IL2CppExtract.Metadata.IL2Cpp;

namespace IL2CppExtract.Assembly;

public partial class AssemblyCppType
{
    private readonly Dictionary<int, AssemblyCppType> _generatedArrayTypes = new();

    [GeneratedRegex(@"[^A-Za-z0-9_\-\.<>{}\u003E\u003C]", RegexOptions.Compiled)]
    private static partial Regex NamespaceRegex();

    public TypeDefinition Definition { get; }
    public CppTypeDefinitionSizes Sizes { get; }
    public int Index { get; }
    public string Namespace { get; }
    public string Name { get; }
    // May get overridden by Il2CppType-based constructor below
    public MemberTypes MemberType { get; } = MemberTypes.TypeInfo;
    public TypeAttributes Attributes { get; set; }
    public bool IsEnum { get; set; }
    public TypeReference? EnumUnderlyingTypeReference { get; set; }

    public AssemblyCppField[] Fields { get; }
    
    public AssemblyFile AssemblyFile { get; }
    public AssemblyCpp Assembly { get; }
    public bool IsArray { get; set; }
    public int ArrayRank { get; set; }
    public AssemblyCppType? ElementType { get; }
    public bool IsByRef { get; set; }
    public bool IsPointer { get; set; }
    
    public Dictionary<string, ulong> Methods { get; } = new();
    
    // Type name including namespace
    // Fully qualified generic type names from the C# compiler use backtick and arity rather than a list of generic arguments
    public string? FullName {
        get 
        {
            if (ElementType != null)
            {
                var n = ElementType.FullName;
                if (n == null)
                    return null;
                if (IsArray)
                    n += "[" + new string(',', ArrayRank - 1) + "]";
                if (IsByRef)
                    n += "&";
                if (IsPointer)
                    n += "*";
                return n;
            }

            return Name;
        }
    }

    public AssemblyCppType(AssemblyCpp assembly, int typeIndex)
    {
        Assembly = assembly;
        var pkg = AssemblyFile = assembly.Package;
        Definition = pkg.Metadata.Types[typeIndex];
        Sizes = pkg.TypeDefinitionSizes[typeIndex];
        Index = typeIndex;

        Namespace = AssemblyCppType.NamespaceRegex().Replace(pkg.Metadata.Strings[Definition.NamespaceIndex], "");
        Name = pkg.Metadata.Strings[Definition.NameIndex];
        
        //Console.WriteLine($"Type {Namespace}.{Name}");
        
        TypeContainer.TypesByDefinitionIndex[typeIndex] = this;
        
        // Nested type?
        if (Definition.DeclaringTypeIndex >= 0) {
            MemberType |= MemberTypes.NestedType;
        }
        
        Attributes = (TypeAttributes) Definition.Flags;

        if (((Definition.Bitfield >> 1) & 1) == 1) 
        {
            IsEnum = true;
        }

        if (FullName != null)
        {
            TypeContainer.TypesByFullName[FullName] = this;
        }
        
        Fields = new AssemblyCppField[Definition.FieldCount];
        
        for (var f = Definition.FieldStart; f < Definition.FieldStart + Definition.FieldCount; f++)
        {
            Fields[f - Definition.FieldStart] = new AssemblyCppField(this, f, pkg);
        }
        
        // Generate methods in DefinedMethods from methodStart to methodStart+methodCount-1
        for (var m = Definition.MethodStart; m < Definition.MethodStart + Definition.MethodCount; m++)
        {
            var method = pkg.Metadata.Methods[m];
            var name = pkg.Metadata.Strings[method.NameIndex];
            var pointer = pkg.GetMethodPointer(Assembly.Module, method);
            
            if (pointer != null)
            {
                Methods[name] = pointer.Value;
                pkg.Methods[Namespace + "$$" + Name + "_" + name] = pointer.Value;
            }
        }
    }

    public AssemblyCppType(AssemblyCppType type, int rank) : this(type.Assembly, type.Index)
    {
        IsArray = true;
        Namespace = type.Namespace;
        Name = type.Name;
        ArrayRank = rank;
        ElementType = type;
    }


    
    public AssemblyCppType MakeArrayType(int rank = 1) 
    {
        if (_generatedArrayTypes.TryGetValue(rank, out var type))
            return type;
        
        type = new AssemblyCppType(this, rank);
        _generatedArrayTypes[rank] = type;
        return type;
    }
}