namespace IL2CppExtract.Assembly.IL2Cpp;

public class CppGenericInst
{
    public ulong TypeArgc { get; set; }
    public ulong TypeArgv { get; set; }
    
    public static CppGenericInst Read(BinaryReader reader)
    {
        return new CppGenericInst
        {
            TypeArgc = reader.ReadUInt64(),
            TypeArgv = reader.ReadUInt64(),
        };
    }
}