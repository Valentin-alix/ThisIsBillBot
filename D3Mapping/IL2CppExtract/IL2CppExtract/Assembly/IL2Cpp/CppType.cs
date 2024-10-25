namespace IL2CppExtract.Assembly.IL2Cpp;

public enum CppTypeEnum
{
    Il2CppTypeEnd = 0x00, /* End of List */
    Il2CppTypeVoid = 0x01,
    Il2CppTypeBoolean = 0x02,
    Il2CppTypeChar = 0x03,
    Il2CppTypeI1 = 0x04,
    Il2CppTypeU1 = 0x05,
    Il2CppTypeI2 = 0x06,
    Il2CppTypeU2 = 0x07,
    Il2CppTypeI4 = 0x08,
    Il2CppTypeU4 = 0x09,
    Il2CppTypeI8 = 0x0a,
    Il2CppTypeU8 = 0x0b,
    Il2CppTypeR4 = 0x0c,
    Il2CppTypeR8 = 0x0d,
    Il2CppTypeString = 0x0e,
    Il2CppTypePtr = 0x0f, /* arg: <type> token */
    Il2CppTypeByref = 0x10, /* arg: <type> token */
    Il2CppTypeValuetype = 0x11, /* arg: <type> token */
    Il2CppTypeClass = 0x12, /* arg: <type> token */
    Il2CppTypeVar = 0x13, /* Generic parameter in a generic type definition, represented as number (compressed unsigned integer) number */
    Il2CppTypeArray = 0x14, /* type, rank, boundsCount, bound1, loCount, lo1 */
    Il2CppTypeGenericinst = 0x15, /* <type> <type-arg-count> <type-1> \x{2026} <type-n> */
    Il2CppTypeTypedbyref = 0x16,
    Il2CppTypeI = 0x18,
    Il2CppTypeU = 0x19,
    Il2CppTypeFnptr = 0x1b, /* arg: full method signature */
    Il2CppTypeObject = 0x1c,
    Il2CppTypeSzarray = 0x1d, /* 0-based one-dim-array */
    Il2CppTypeMvar = 0x1e, /* Generic parameter in a generic method definition, represented as number (compressed unsigned integer)  */
    Il2CppTypeCmodReqd = 0x1f, /* arg: typedef or typeref token */
    Il2CppTypeCmodOpt = 0x20, /* optional arg: typedef or typref token */
    Il2CppTypeInternal = 0x21, /* CLR internal type */

    Il2CppTypeModifier = 0x40, /* Or with the following types */
    Il2CppTypeSentinel = 0x41, /* Sentinel for varargs method signature */
    Il2CppTypePinned = 0x45, /* Local var that points to pinned object */

    Il2CppTypeEnum = 0x55, /* an enumeration */
    Il2CppTypeIl2CppTypeIndex = 0xff /* Type index metadata table */
}

public class CppType
{
    public ulong DataPoint { get; set; }
    public ulong Bits { get; set; }
    
    public uint Attrs => (uint)(Bits & 0xffff);
    public CppTypeEnum Type => (CppTypeEnum)((Bits >> 16) & 0xff);
    
    public uint NumMods => (uint)((Bits >> 24) & 0x1f);
    public bool ByRef => ((Bits >> 29) & 1) == 1;
    public bool Pinned => ((Bits >> 30) & 1) == 1;
    public bool ValueType => ((Bits >> 31) & 1) == 1;
    
    public static CppType Read(BinaryReader reader)
    {
        return new CppType
        {
            DataPoint = reader.ReadUInt64(),
            Bits = reader.ReadUInt64()
        };
    }
    
}