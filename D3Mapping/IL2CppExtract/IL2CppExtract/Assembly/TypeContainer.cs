namespace IL2CppExtract.Assembly;

public static class TypeContainer
{
    public static AssemblyCppType[] TypesByDefinitionIndex { get; set; } = [];
    public static AssemblyCppType?[] TypesByReferenceIndex { get; set; } = [];
    public static List<AssemblyCppField> RVAFields { get; set; } = new();
    public static Dictionary<string, AssemblyCppType> TypesByFullName { get; set; } = new();

}

public class TypeReference
{
    public required AssemblyCppType Type { get; set; }
    public int ReferenceIndex = -1;
    public int DefinitionIndex = -1;
    

    public AssemblyCppType? Value
    {
        get
        {
            if (ReferenceIndex >= 0)
            {
                return TypeContainer.TypesByReferenceIndex[ReferenceIndex];
            }
            
            if (DefinitionIndex >= 0)
            {
                return TypeContainer.TypesByDefinitionIndex[DefinitionIndex];
            }
            
            throw new InvalidOperationException("No reference or definition index set");
        }
    }
    public static TypeReference FromReferenceIndex(AssemblyCppType type, int index)
    {
        return new TypeReference
        {
            Type = type,
            ReferenceIndex = index,
        };
    }
    
    public static TypeReference FromDefinitionIndex(AssemblyCppType type, int index)
    {
        return new TypeReference
        {
            Type = type,
            DefinitionIndex = index,
        };
    }
}