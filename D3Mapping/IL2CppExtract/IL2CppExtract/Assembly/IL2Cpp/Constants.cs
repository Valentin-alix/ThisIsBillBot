namespace IL2CppExtract.Assembly.IL2Cpp;

public class Constants
{
    public static List<string> FullNameTypeString = new List<string>
    {
        "END",
        "System.Void",
        "System.Boolean",
        "System.Char",
        "System.SByte",
        "System.Byte",
        "System.Int16",
        "System.UInt16",
        "System.Int32",
        "System.UInt32",
        "System.Int64",
        "System.UInt64",
        "System.Single",
        "System.Double",
        "System.String",
        "PTR",                 // Processed separately
        "BYREF",
        "System.ValueType",    // Processed separately
        "CLASS",               // Processed separately
        "T",
        "System.Array",        // Processed separately
        "GENERICINST",         // Processed separately
        "System.TypedReference", // params
        "None",
        "System.IntPtr",
        "System.UIntPtr",
        "None",
        "System.Delegate",
        "System.Object",
        "SZARRAY",             // Processed separately
        "T",
        "CMOD_REQD",
        "CMOD_OPT",
        "INTERNAL",

        // Added in for convenience
        "System.Decimal"
    };
}