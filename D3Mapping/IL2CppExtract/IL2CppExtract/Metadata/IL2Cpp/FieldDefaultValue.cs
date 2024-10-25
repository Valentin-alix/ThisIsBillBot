namespace IL2CppExtract.Metadata.IL2Cpp;

public class FieldDefaultValue
{
    public int FieldIndex { get; set; }
    public int TypeIndex { get; set; }
    public int DataIndex { get; set; }

    public static int GetSize(double version)
    {
        return 3 * sizeof(int);
    }
    
    public static FieldDefaultValue Read(BinaryReader reader, double version)
    {
        return new FieldDefaultValue
        {
            FieldIndex = reader.ReadInt32(),
            TypeIndex = reader.ReadInt32(),
            DataIndex = reader.ReadInt32(),
        };
    }
}