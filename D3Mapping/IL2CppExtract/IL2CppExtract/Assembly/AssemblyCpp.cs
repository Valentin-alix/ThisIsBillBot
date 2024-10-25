using System.Text.RegularExpressions;
using IL2CppExtract.Assembly.IL2Cpp;
using IL2CppExtract.Metadata.IL2Cpp;

namespace IL2CppExtract.Assembly;

public partial class AssemblyCpp
{
    [GeneratedRegex(@"[^A-Za-z0-9_\-\.()]")]
    private static partial Regex AssemblyNameRegex();
    
    public ImageDefinition Image { get; }
    public string ShortName { get; }
    public string Name { get; }
    public string Culture { get; }
    public string Version { get; }
    public string FullName { get; }
    public AssemblyDefinition Definition { get; }
    public CodeGenModule Module { get; }
    public List<AssemblyCppType> Types { get; } = new List<AssemblyCppType>();
    
    public AssemblyFile Package { get; }
    
    public AssemblyCpp(AssemblyFile file, int index)
    {
        Package = file;
        Image = file.Metadata.Images[index];
            
        ShortName = file.Metadata.Strings[Image.NameIndex];
        Definition = file.Metadata.Assemblies[Image.AssemblyIndex];

        if (Definition.ImageIndex != index)
        {
            throw new Exception("Assembly/image index mismatch");
        }
            
        var nameDef = Definition.Name;
        Name = AssemblyCpp.AssemblyNameRegex().Replace(file.Metadata.Strings[nameDef.NameIndex], "");
        Culture = file.Metadata.Strings[nameDef.CultureIndex];
            
        if (string.IsNullOrEmpty(Culture))
            Culture = "neutral";
            
        var pkt = Convert.ToHexString(nameDef.PublicKeyToken);
        if (pkt == "0000000000000000")
            pkt = "null";
            
        Version = string.Format($"{nameDef.Major}.{nameDef.Minor}.{nameDef.Build}.{nameDef.Revision}");
        FullName = string.Format($"{Name}, Version={Version}, Culture={Culture}, PublicKeyToken={pkt.ToLower()}");
        Module = file.Modules[ShortName];
        
        // Generate types in DefinedTypes from typeStart to typeStart+typeCount-1
        for (var t = Image.TypeStart; t < Image.TypeStart + Image.TypeCount; t++) 
        {
            var type = new AssemblyCppType(this, t);

            // Don't add empty module definitions
            if (type.Name != "<Module>")
                Types.Add(type);
        }
        
    }
}
