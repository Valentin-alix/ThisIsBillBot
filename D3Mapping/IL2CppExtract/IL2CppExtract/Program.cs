using System.Buffers;
using IL2CppExtract.Assembly;
using IL2CppExtract.Metadata;

const string dir = @"D:\Programmes\Dofus-dofus3";

var assemblyFile = $@"{dir}\GameAssembly.dll";
var globalMetadata = $@"{dir}\Dofus_Data\il2cpp_data\Metadata\global-metadata.dat";

using var metadataStream = new FileStream(globalMetadata, FileMode.Open, FileAccess.Read);
var metadata = MetadataFile.Read(metadataStream);

using var assemblyStream = new FileStream(assemblyFile, FileMode.Open, FileAccess.Read);
var assembly = AssemblyFile.Read(assemblyStream, metadata);

assembly.ExportStaticStrings();