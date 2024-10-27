using Il2CppDumper;
using IL2CppExtract.Assembly;
using IL2CppExtract.Metadata;
using System.Buffers;
using System.Reflection;
using System.Reflection.PortableExecutable;

const string dirServ = @"C:\Users\Valentin\AppData\Local\Ankama\Dofus-dofus3";
const string dirBur = @"D:\Programmes\Dofus-dofus3";
const string dir = dirServ;

var assemblyFile = $@"{dir}\GameAssembly.dll";
var globalMetadata = $@"{dir}\Dofus_Data\il2cpp_data\Metadata\global-metadata.dat";

Il2CppDumper.Il2CppParser.Init(assemblyFile, globalMetadata, out var metadataIl2CppDumper, out var il2Cpp);

using var metadataStream = new FileStream(globalMetadata, FileMode.Open, FileAccess.Read);
var metadata = MetadataFile.Read(metadataStream, metadataIl2CppDumper);


using var assemblyStream = new FileStream(assemblyFile, FileMode.Open, FileAccess.Read);
var assembly = AssemblyFile.Read(assemblyStream, metadata, il2Cpp);

assembly.ExportStaticStrings();