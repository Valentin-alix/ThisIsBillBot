using System.Text;

namespace IL2CppExtract.Reader;

public static class ReaderUtils
{
    public static string ReadNullTerminatedString(BinaryReader reader)
    {
        var bytes = new List<byte>();
        
        while (true)
        {
            var b = reader.ReadByte();
            if (b == 0)
            {
                break;
            }
            bytes.Add(b);
        }
        
        return Encoding.UTF8.GetString(bytes.ToArray());
    }
}